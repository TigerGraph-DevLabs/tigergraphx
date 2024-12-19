from abc import ABC
from typing import Any, List

from tigergraphx.vector_search import BaseVectorDB, BaseEmbedding


class BaseSearchEngine(ABC):
    """Base class for a search engine that performs text-to-vector searches in a vector store."""

    def __init__(self, embedding_model: BaseEmbedding, vector_db: BaseVectorDB):
        """
        Initialize the search engine with an embedding model and a vector database.

        Args:
            embedding_model (BaseEmbedding): The model used to generate text embeddings.
            vector_db (BaseVectorDB): The vector database for storing and querying embeddings.
        """
        self.embedding_model = embedding_model
        self.vector_db = vector_db

    async def search(self, text: str, k: int = 10, **kwargs: Any) -> List[str]:
        """
        Convert text to embedding and search in the vector database.

        Args:
            text (str): The input text to search.
            k (int, optional): The number of top results to return. Defaults to 10.
            **kwargs (Any): Additional arguments for the vector database query.

        Returns:
            List[str]: A list of IDs corresponding to the search results.
        """
        embedding = await self.embedding_model.generate_embedding(text)
        results = self.vector_db.query(query_embedding=embedding, k=k, **kwargs)
        return results
