from abc import ABC
from typing import Any, List

from tigergraphx.vector_search import BaseVectorDB, BaseEmbedding


class BaseSearchEngine(ABC):
    """Base class for a search engine that performs text-to-vector searches in a vector store."""

    def __init__(self, embedding_model: BaseEmbedding, vector_db: BaseVectorDB):
        self.embedding_model = embedding_model
        self.vector_db = vector_db

    async def search(self, text: str, k: int = 10, **kwargs: Any) -> List[str]:
        """Convert text to embedding and search in the vector database."""
        # Step 1: Generate the embedding for the text
        embedding = await self.embedding_model.generate_embedding(text)

        # Step 2: Query the vector database using the embedding
        results = self.vector_db.query(query_embedding=embedding, k=k, **kwargs)
        return results
