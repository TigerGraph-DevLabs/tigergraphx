import tiktoken
from typing import Optional, List

from tigergraphx.graphrag import BaseContextBuilder

from tigergraphx.core import Graph
from tigergraphx.vector_search import BaseSearchEngine


class LocalContextBuilder(BaseContextBuilder):
    def __init__(
        self,
        graph: Graph,
        search_engine: BaseSearchEngine,
        token_encoder: Optional[tiktoken.Encoding] = None,
    ):
        """Initialize LocalContextBuilder with graph config, search engine, and token encoder."""
        super().__init__(
            graph=graph,
            single_batch=True,
            search_engine=search_engine,
            token_encoder=token_encoder,
        )

    async def build_context(self, query: str, k: int = 10) -> str | List[str]:
        """Build local context."""
        context: List[str] = []

        # Retrieve top-k objects
        top_k_objects: List[str] = await self.retrieve_top_k_objects(query, k=k)
        if not top_k_objects:
            return ""  # Return early if no objects are retrieved

        # Define neighbor types with their attributes
        neighbor_types = [
            {
                "target_node_types": "Community",
                "max_tokens": 1200,
                "section_name": "Communities",
                "return_attributes": ["id", "title", "full_content"],
            },
            {
                "target_node_types": "Relationship",
                "max_tokens": 4800,
                "section_name": "Relationships",
                "return_attributes": [
                    "id",
                    "description",
                    "weight",
                    "rank",
                ],
            },
            {
                "target_node_types": "TextUnit",
                "max_tokens": 6000,
                "section_name": "Text Units",
                "return_attributes": ["id", "text"],
            },
        ]

        # Iterate over different neighbor types
        for neighbor in neighbor_types:
            df = self.graph.get_neighbors(
                start_nodes=top_k_objects,
                start_node_type="Entity",
                target_node_types=neighbor["target_node_types"],
                return_attributes=neighbor["return_attributes"],
            )
            if df is not None:
                text_context = self.batch_and_convert_to_text(
                    graph_data=df,
                    max_tokens=neighbor["max_tokens"],
                    single_batch=self.single_batch,
                    section_name=neighbor["section_name"],
                )
                context.extend(
                    text_context if isinstance(text_context, list) else [text_context]
                )

        return "\n\n".join(context)
