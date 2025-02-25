# Copyright 2025 TigerGraph Inc.
# Licensed under the Apache License, Version 2.0.
# See the LICENSE file or https://www.apache.org/licenses/LICENSE-2.0
#
# Permission is granted to use, copy, modify, and distribute this software
# under the License. The software is provided "AS IS", without warranty.

import logging
from dataclasses import dataclass
from typing import Literal
import asyncio
import json

from .prompt import PROMPTS
from .context_builder import (
    LocalContextBuilder,
    GlobalContextBuilder,
)

from tigergraphx import Graph
from tigergraphx.factories import create_openai_components

logger = logging.getLogger(__name__)


@dataclass
class QueryParam:
    mode: Literal["local", "global"] = "global"
    only_need_context: bool = False
    response_type: str = "Multiple Paragraphs"
    top_k: int = 20


@dataclass
class GraphRAG:
    schema_path: str = "applications/msft_graphrag/query/resources/graph_schema.yaml"
    loading_job_path: str = (
        "applications/msft_graphrag/query/resources/loading_job_config.yaml"
    )
    settings_path: str = "applications/msft_graphrag/query/resources/settings.yaml"
    to_load_data: bool = True

    def __post_init__(self):
        logger.info(
            "Initializing GraphRAG with schema_path: %s, loading_job_path: %s, settings_path: %s",
            self.schema_path,
            self.loading_job_path,
            self.settings_path,
        )
        # Create Graph Schema
        graph = Graph(
            graph_schema=self.schema_path,
            drop_existing_graph=False,
        )
        # Load Data
        if self.to_load_data:
            logger.info(
                "Loading data into graph using loading job config: %s",
                self.loading_job_path,
            )
            graph.load_data(loading_job_config=self.loading_job_path)
        # Create Context Builders
        (self.openai_chat, search_engine) = create_openai_components(self.settings_path, graph)
        self.local_context_builder = LocalContextBuilder(
            graph=graph, search_engine=search_engine
        )
        self.global_context_builder = GlobalContextBuilder(graph=graph)

    def query(self, query: str, param: QueryParam = QueryParam()):
        logger.info("Executing query with parameters: %s", param)
        loop = self.always_get_an_event_loop()
        return loop.run_until_complete(self.aquery(query, param))

    async def aquery(self, query: str, param: QueryParam = QueryParam()):
        logger.info("Starting asynchronous query execution.")
        if param.mode == "local":
            response = await self.local_query(
                query,
                param,
            )
        elif param.mode == "global":
            response = await self.global_query(
                query,
                param,
            )
        else:
            raise ValueError(f"Unknown mode {param.mode}")
        return response

    async def local_query(
        self,
        query: str,
        query_param: QueryParam,
    ) -> str:
        """
        Perform a local search using the context builder and return the result.
        """
        logger.info("Performing local query with top_k: %d", query_param.top_k)
        # Generate context using the local context builder
        context = await self.local_context_builder.build_context(
            query,
            k=query_param.top_k,
        )
        if query_param.only_need_context:
            if not isinstance(context, str):
                raise TypeError("Expected `context` to be an instance of str.")
            return context

        # Validate that context exists
        if not context:
            return PROMPTS["fail_response"]

        # Construct the system prompt using the context
        system_prompt = PROMPTS["local_rag_response"].format(
            context_data=context, response_type=query_param.response_type
        )

        # Perform the query using OpenAIChat
        logger.info("Executing final query with OpenAIChat.")
        try:
            response = await self.openai_chat.chat(
                [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": query},
                ]
            )
            return response
        except Exception as e:
            logger.error(f"Error during local_query: {e}")
            return "An error occurred while processing the query."

    async def global_query(
        self,
        query: str,
        query_param: QueryParam,
    ) -> str:
        """
        Execute a global query using the provided context and query parameters.
        """

        logger.info("Performing global query.")
        # Retrieve context using the global context builder
        context_list = await self.global_context_builder.build_context()

        # Handle case where only the context is needed
        if query_param.only_need_context:
            if not isinstance(context_list, list):
                raise TypeError("Expected `context_list` to be a list.")
            return "\n\n".join(context_list)

        # Return failure response if context is empty
        if not context_list:
            return PROMPTS["fail_response"]

        # Map process: Process each context in the context_list
        async def _process_context(context: str) -> dict:
            """
            Process an individual context through the map stage.
            """
            # Construct system prompt for map stage
            sys_prompt = PROMPTS["global_map_rag_points"].format(context_data=context)
            try:
                # Perform the query using OpenAIChat
                response = await self.openai_chat.chat(
                    [
                        {"role": "system", "content": sys_prompt},
                        {"role": "user", "content": query},
                    ]
                )
                # Parse JSON response
                if isinstance(response, dict):
                    return json.loads(response).get("points", {})
                else:
                    return {}
            except Exception as e:
                logger.error(f"Error during map stage: {e}")
                return {}  # Fallback to an empty dict on failure

        # Apply the map process to all contexts in context_list
        try:
            logger.info("Mapping contexts.")
            mapped_contexts = await asyncio.gather(
                *[_process_context(context) for context in context_list]
            )
        except Exception as e:
            logger.error(f"Error during mapping phase: {e}")
            return "An error occurred during the mapping process."

        # Combine mapped contexts
        combined_points = []
        for context in mapped_contexts:
            combined_points.extend(context)

        logger.info("Combining and sorting mapped contexts.")
        # Sort combined points by score in descending order
        combined_points.sort(key=lambda x: x.get("score", 0), reverse=True)

        # Prepare data for the reduction step
        combined_context = "\n".join(
            f"{point['description']} (Score: {point['score']})"
            for point in combined_points
        )

        # Construct the system prompt for reduction
        system_prompt = PROMPTS["global_reduce_rag_response"].format(
            report_data=combined_context,
            response_type=query_param.response_type,
        )

        # Perform the final query using OpenAIChat
        try:
            response = await self.openai_chat.chat(
                [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": query},
                ]
            )
            return response
        except Exception as e:
            logger.error(f"Error during global_query: {e}")
            return "An error occurred while processing the query."

    @staticmethod
    def always_get_an_event_loop() -> asyncio.AbstractEventLoop:
        try:
            logger.info("Retrieving existing event loop.")
            # If there is already an event loop, use it.
            loop = asyncio.get_event_loop()
        except RuntimeError:
            logger.info("No existing event loop found. Creating a new event loop.")
            # If in a sub-thread, create a new event loop.
            logger.info("Creating a new event loop in a sub-thread.")
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        return loop
