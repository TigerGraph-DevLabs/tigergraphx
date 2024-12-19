from .base_search_engine import BaseSearchEngine

from tigergraphx.vector_search import (
    OpenAIEmbedding,
    LanceDBManager,
)


class LanceDBSearchEngine(BaseSearchEngine):
    """
    Search engine that performs text embedding and similarity search using OpenAI and LanceDB.
    """

    embedding_model: OpenAIEmbedding
    vector_db: LanceDBManager

    def __init__(self, embedding_model: OpenAIEmbedding, vector_db: LanceDBManager):
        """
        Initialize the LanceDBSearchEngine.

        Args:
            embedding_model (OpenAIEmbedding): The embedding model used for text-to-vector conversion.
            vector_db (LanceDBManager): The vector database for similarity search.
        """
        super().__init__(embedding_model, vector_db)
