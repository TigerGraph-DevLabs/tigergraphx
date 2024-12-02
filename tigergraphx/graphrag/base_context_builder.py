import tiktoken
from typing import Optional, List, Dict, Any
from abc import ABC, abstractmethod
import pandas as pd

from tigergraphx.core import Graph
from tigergraphx.vector_search import BaseSearchEngine


class BaseContextBuilder(ABC):
    def __init__(
        self,
        graph: Graph,
        single_batch: bool,
        search_engine: Optional[BaseSearchEngine] = None,
        token_encoder: Optional[tiktoken.Encoding] = None,
    ):
        self.graph = graph
        self.single_batch = single_batch
        self.search_engine = search_engine
        self.token_encoder = token_encoder or tiktoken.get_encoding("cl100k_base")

    @abstractmethod
    async def build_context(self, *args, **kwargs) -> str | List[str]:
        """Abstract method to build context."""
        pass

    def batch_and_convert_to_text(
        self,
        graph_data: pd.DataFrame,
        section_name: str,
        single_batch: bool = False,
        max_tokens: int = 12000,
    ) -> str | List[str]:
        """Converts graph data to a formatted string or list of strings in batches based on token count."""
        header = f"-----{section_name}-----\n" + "|".join(graph_data.columns) + "\n"
        content_rows = [
            "|".join(str(value) for value in row) for row in graph_data.values
        ]

        # Token count for the header
        header_tokens = self._num_tokens(header, self.token_encoder)
        batches = []
        current_batch = header
        current_tokens = header_tokens

        for row in content_rows:
            row_tokens = self._num_tokens(row, self.token_encoder)

            # Check if adding this row would exceed max token limit
            if current_tokens + row_tokens > max_tokens:
                batches.append(current_batch.strip())
                if single_batch:
                    return batches[0]

                # Start a new batch with the header
                current_batch = header + row + "\n"
                current_tokens = header_tokens + row_tokens
            else:
                # Add the row to the current batch
                current_batch += row + "\n"
                current_tokens += row_tokens

        # Append the last batch if it has content
        if current_batch.strip():
            batches.append(current_batch.strip())

        return batches[0] if single_batch else batches

    async def retrieve_top_k_objects(
        self, query: str, k: int = 10, **kwargs: Dict[str, Any]
    ) -> List[str]:
        """Retrieve the top-k objects most similar to the query."""
        if k <= 0:
            raise ValueError("Parameter 'k' must be greater than 0.")

        if not self.search_engine:
            raise ValueError("Search engine is not initialize.")

        if query:
            # Perform similarity search with oversampling to ensure quality
            oversample_scaler = 2
            search_results = await self.search_engine.search(
                text=query,
                k=k * oversample_scaler,
            )
            return search_results
        return []

    @staticmethod
    def _num_tokens(text: str, token_encoder: tiktoken.Encoding | None = None) -> int:
        """Return the number of tokens in the given text."""
        if token_encoder is None:
            token_encoder = tiktoken.get_encoding("cl100k_base")
        return len(token_encoder.encode(text))  # type: ignore
