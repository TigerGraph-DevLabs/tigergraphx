from .base_search_engine import BaseSearchEngine

from tigergraphx.vector_search import (
    OpenAIEmbedding,
    TigerVectorManager,
)


class TigerVectorSearchEngine(BaseSearchEngine):
    """
    Search engine that performs text embedding and similarity search using OpenAI and LanceDB.
    """

    embedding_model: OpenAIEmbedding
    vector_db: TigerVectorManager

    def __init__(self, embedding_model: OpenAIEmbedding, vector_db: TigerVectorManager):
        """
        Initialize the TigerVectorSearchEngine.

        Args:
            embedding_model (OpenAIEmbedding): The embedding model used for text-to-vector conversion.
            vector_db (TigerVectorManager): The vector database for similarity search.
        """
        super().__init__(embedding_model, vector_db)
