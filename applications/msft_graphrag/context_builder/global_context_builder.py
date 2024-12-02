import tiktoken
from typing import Optional, List

from tigergraphx.graphrag import BaseContextBuilder

from tigergraphx.core import Graph


class GlobalContextBuilder(BaseContextBuilder):
    def __init__(
        self,
        graph: Graph,
        token_encoder: Optional[tiktoken.Encoding] = None,
    ):
        """Initialize LocalContextBuilder with graph config and token encoder."""
        super().__init__(
            graph=graph,
            single_batch=False,
            token_encoder=token_encoder,
        )

    async def build_context(self) -> str | List[str]:
        """Build local context."""
        context: List[str] = []

        config = {
            "max_tokens": 12000,
            "section_name": "Communities",
            "return_attributes": ["id", "rank", "title", "full_content"],
            "limit": 1000,
        }
        df = self.graph.get_nodes(
            node_type="Community",
            return_attributes=config["return_attributes"],
            limit=config["limit"],
        )
        if df is not None:
            text_context = self.batch_and_convert_to_text(
                graph_data=df,
                max_tokens=config["max_tokens"],
                single_batch=self.single_batch,
                section_name=config["section_name"],
            )
            context.extend(
                text_context if isinstance(text_context, list) else [text_context]
            )

        return context
