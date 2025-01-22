import tiktoken
from typing import Optional, List, Dict, Any
from abc import ABC, abstractmethod
import pandas as pd

from tigergraphx.core import Graph
from tigergraphx.vector_search import BaseSearchEngine


class BaseContextBuilder(ABC):
    """
    Abstract base class for building context using graph data and a search engine.

    Attributes:
        graph: The graph object.
        single_batch: Whether to process data in a single batch.
        search_engine: The search engine for retrieving top-k objects.
        token_encoder: Token encoder for text tokenization.
    """

    def __init__(
        self,
        graph: Graph,
        single_batch: bool,
        search_engine: Optional[BaseSearchEngine] = None,
        token_encoder: Optional[tiktoken.Encoding] = None,
    ):
        """
        Initialize the BaseContextBuilder.

        Args:
            graph: The graph object.
            single_batch: Whether to process data in a single batch.
            search_engine: The search engine for similarity searches.
            token_encoder: Token encoder for text tokenization. Defaults to "cl100k_base".
        """
        self.graph = graph
        self.single_batch = single_batch
        self.search_engine = search_engine
        self.token_encoder = token_encoder or tiktoken.get_encoding("cl100k_base")

    @abstractmethod
    async def build_context(self, *args, **kwargs) -> str | List[str]:
        """
        Abstract method to build context.

        Returns:
            The generated context as a string or list of strings.
        """
        pass

    def batch_and_convert_to_text(
        self,
        graph_data: pd.DataFrame,
        section_name: str,
        single_batch: bool = False,
        max_tokens: int = 12000,
    ) -> str | List[str]:
        """
        Convert graph data to a formatted string or list of strings in batches based on token count.

        Args:
            graph_data: The graph data to convert.
            section_name: The section name for the header.
            single_batch: Whether to process data in a single batch. Defaults to False.
            max_tokens: Maximum number of tokens per batch. Defaults to 12000.

        Returns:
            The formatted graph data as a string or list of strings.
        """
        header = f"-----{section_name}-----\n" + "|".join(graph_data.columns) + "\n"
        content_rows = [
            "|".join(str(value) for value in row) for row in graph_data.values
        ]

        header_tokens = self._num_tokens(header, self.token_encoder)
        batches = []
        current_batch = header
        current_tokens = header_tokens

        for row in content_rows:
            row_tokens = self._num_tokens(row, self.token_encoder)

            if current_tokens + row_tokens > max_tokens:
                batches.append(current_batch.strip())
                if single_batch:
                    return batches[0]

                current_batch = header + row + "\n"
                current_tokens = header_tokens + row_tokens
            else:
                current_batch += row + "\n"
                current_tokens += row_tokens

        if current_batch.strip():
            batches.append(current_batch.strip())

        return batches[0] if single_batch else batches

    async def retrieve_top_k_objects(
        self, query: str, k: int = 10, **kwargs: Dict[str, Any]
    ) -> List[str]:
        """
        Retrieve the top-k objects most similar to the query.

        Args:
            query: The query string.
            k: The number of top results to retrieve. Defaults to 10.
            **kwargs: Additional parameters for the search engine.

        Returns:
            A list of the top-k results.

        Raises:
            ValueError: If `k` is less than or equal to 0 or if the search engine is not initialized.
        """
        if k <= 0:
            raise ValueError("Parameter 'k' must be greater than 0.")

        if not self.search_engine:
            raise ValueError("Search engine is not initialized.")

        if query:
            oversample_scaler = 2
            search_results = await self.search_engine.search(
                text=query,
                k=k * oversample_scaler,
            )
            return search_results
        return []

    @staticmethod
    def _num_tokens(text: str, token_encoder: tiktoken.Encoding | None = None) -> int:
        """
        Return the number of tokens in the given text.

        Args:
            text: The text to tokenize.
            token_encoder: The token encoder to use. Defaults to None.

        Returns:
            The number of tokens in the text.
        """
        if token_encoder is None:
            token_encoder = tiktoken.get_encoding("cl100k_base")
        return len(token_encoder.encode(text))  # type: ignore
