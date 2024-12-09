import logging
from dataclasses import dataclass, field
from typing import Literal
import asyncio
import json

from .utils import always_get_an_event_loop
from .graph_manager import GraphManager
from .prompt import PROMPTS
from .context_builder import (
    LocalContextBuilder,
    GlobalContextBuilder,
)

from tigergraphx import create_openai_components

logger = logging.getLogger(__name__)


@dataclass
class QueryParam:
    mode: Literal["local", "global"] = "global"
    only_need_context: bool = False
    response_type: str = "Multiple Paragraphs"
    level: int = 2
    top_k: int = 20
    # local search
    local_max_token_for_text_unit: int = 4000  # 12000 * 0.33
    local_max_token_for_local_context: int = 4800  # 12000 * 0.4
    local_max_token_for_community_report: int = 3200  # 12000 * 0.27
    local_community_single_one: bool = False
    # global search
    global_min_community_rating: float = 0
    global_max_consider_community: float = 512
    global_max_token_for_community_report: int = 16384
    global_special_community_map_llm_kwargs: dict = field(
        default_factory=lambda: {"response_format": {"type": "json_object"}}
    )


class GraphRAG:
    settings_path: str = "resources/settings.yaml"

    def __init__(self):
        graph_manager = GraphManager(to_load_data=False)
        (self.openai_chat, search_engine) = create_openai_components(self.settings_path)
        self.local_context_builder = LocalContextBuilder(
            graph=graph_manager.graph, search_engine=search_engine
        )
        self.global_context_builder = GlobalContextBuilder(graph=graph_manager.graph)

    def query(self, query: str, param: QueryParam = QueryParam()):
        loop = always_get_an_event_loop()
        return loop.run_until_complete(self.aquery(query, param))

    async def aquery(self, query: str, param: QueryParam = QueryParam()):
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
                return json.loads(response).get("points", [])
            except Exception as e:
                logger.error(f"Error during map stage: {e}")
                return {}  # Fallback to an empty dict on failure

        # Apply the map process to all contexts in context_list
        try:
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
        print(system_prompt)

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
