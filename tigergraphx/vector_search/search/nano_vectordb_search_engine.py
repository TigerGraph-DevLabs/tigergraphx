from .base_search_engine import BaseSearchEngine

from tigergraphx.vector_search import (
    OpenAIEmbedding,
    NanoVectorDBManager,
)


class NanoVectorDBSearchEngine(BaseSearchEngine):
    """Search engine that performs text embedding and similarity search using OpenAI and NanoVectorDB."""

    embedding_model: OpenAIEmbedding
    vector_db: NanoVectorDBManager

    def __init__(
        self, embedding_model: OpenAIEmbedding, vector_db: NanoVectorDBManager
    ):
        super().__init__(embedding_model, vector_db)
