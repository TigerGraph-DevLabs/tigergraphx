# Copyright 2025 TigerGraph Inc.
# Licensed under the Apache License, Version 2.0.
# See the LICENSE file or https://www.apache.org/licenses/LICENSE-2.0
#
# Permission is granted to use, copy, modify, and distribute this software
# under the License. The software is provided "AS IS", without warranty.

import os
from typing import List
import asyncio

from tigergraphx.core import Graph
from tigergraphx.graphrag import BaseContextBuilder
from tigergraphx.llm import OpenAIChat
from tigergraphx.factories import create_openai_components


class ContextBuilder(BaseContextBuilder):
    async def build_context(self, query: str, k: int = 10) -> str | List[str]:
        """Build local context."""
        context: List[str] = []

        # Retrieve top-k objects
        top_k_objects: List[str] = await self.retrieve_top_k_objects(
            query, k=k, oversample_scaler=1
        )
        if not top_k_objects:
            return ""  # Return early if no objects are retrieved

        # Iterate over all products
        for product in top_k_objects:
            node_data = self.graph.get_node_data(product, "Product")
            edges = self.graph.get_node_edges(product, "Product")
            context.append(f"Node Data for {product}: {node_data}")
            context.append(f"Edges for {product}: {edges}")

        return "\n\n".join(context)


PROMPTS = """---Role---

You are a helpful assistant responding to questions about data in the tables provided.


---Goal---

Generate a response of the target length and format that responds to the user's question, summarizing all information in the input data tables appropriate for the response length and format, and incorporating any relevant general knowledge.
If you don't know the answer, just say so. Do not make anything up.
Do not include information where the supporting evidence for it is not provided.

---Target response length and format---

{response_type}


---Data tables---

{context_data}


---Goal---

Generate a response of the target length and format that responds to the user's question, summarizing all information in the input data tables appropriate for the response length and format, and incorporating any relevant general knowledge.

If you don't know the answer, just say so. Do not make anything up.

Do not include information where the supporting evidence for it is not provided.


---Target response length and format---

{response_type}

Add sections and commentary to the response as appropriate for the length and format. Style the response in markdown.
"""


async def query(
    query: str,
    openai_chat: OpenAIChat,
    context_builder: BaseContextBuilder,
    top_k: int = 10,
    only_need_context: bool = False,
    response_type: str = "Multiple Paragraphs",
) -> str:
    """
    Perform a local search using the context builder and return the result.
    """
    # Generate context using the local context builder
    context = await context_builder.build_context(
        query,
        k=top_k,
    )
    if only_need_context:
        if not isinstance(context, str):
            raise TypeError("Expected `context` to be an instance of str.")
        return context

    # Validate that context exists
    if not context:
        return "Apologies, but I couldn't provide an answer as no relevant context was found for your query."

    # Construct the system prompt using the context
    system_prompt = PROMPTS.format(context_data=context, response_type=response_type)

    # Perform the query using OpenAIChat
    try:
        response = await openai_chat.chat(
            [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": query},
            ]
        )
        return response
    except Exception:
        return "An error occurred while processing the query."


def main():
    os.environ["TG_HOST"] = "http://127.0.0.1"
    os.environ["TG_USERNAME"] = "tigergraph"
    os.environ["TG_PASSWORD"] = "tigergraph"

    G = Graph.from_db("RetailGraph")

    # Create Context Builders
    settings = {
        "vector_db": {
            "type": "TigerVector",
            "graph_name": "RetailGraph",
            "node_type": "Product",
            "vector_attribute_name": "emb_features",
        },
        "llm": {
            "type": "OpenAI",
            # NOTE: The api_key must be provided via the environment variable OPENAI_API_KEY
        },
        "embedding": {
            "type": "OpenAI",
            "model": "text-embedding-3-small",
        },
        "chat": {
            "type": "OpenAI",
            "model": "gpt-4o-mini",
        },
    }
    (openai_chat, search_engine) = create_openai_components(settings, G)
    context_builder = ContextBuilder(graph=G, search_engine=search_engine)
    result = asyncio.run(
        query(
            query="I am looking for a begginer drone. Please give me some recommendations.",
            openai_chat=openai_chat,
            context_builder=context_builder,
            only_need_context=False,
        )
    )
    print(result)


if __name__ == "__main__":
    main()
