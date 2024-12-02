from .base_search_engine import BaseSearchEngine

from tigergraphx.vector_search import (
    OpenAIEmbedding,
    LanceDBManager,
)


class LanceDBSearchEngine(BaseSearchEngine):
    """Search engine that performs text embedding and similarity search using OpenAI and LanceDB."""

    embedding_model: OpenAIEmbedding
    vector_db: LanceDBManager

    def __init__(self, embedding_model: OpenAIEmbedding, vector_db: LanceDBManager):
        super().__init__(embedding_model, vector_db)
