from .base_search_engine import BaseSearchEngine

from tigergraphx.vector_search import (
    OpenAIEmbedding,
    NanoVectorDBManager,
)


class NanoVectorDBSearchEngine(BaseSearchEngine):
    """
    Search engine that performs text embedding and similarity search using OpenAI and NanoVectorDB.
    """

    embedding_model: OpenAIEmbedding
    vector_db: NanoVectorDBManager

    def __init__(
        self, embedding_model: OpenAIEmbedding, vector_db: NanoVectorDBManager
    ):
        """
        Initialize the NanoVectorDBSearchEngine.

        Args:
            embedding_model: The embedding model used for text-to-vector conversion.
            vector_db: The vector database for similarity search.
        """
        super().__init__(embedding_model, vector_db)
