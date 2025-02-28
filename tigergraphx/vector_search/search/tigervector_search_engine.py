# Copyright 2025 TigerGraph Inc.
# Licensed under the Apache License, Version 2.0.
# See the LICENSE file or https://www.apache.org/licenses/LICENSE-2.0
#
# Permission is granted to use, copy, modify, and distribute this software
# under the License. The software is provided "AS IS", without warranty.

from .base_search_engine import BaseSearchEngine

from tigergraphx.vector_search import (
    OpenAIEmbedding,
    TigerVectorManager,
)


class TigerVectorSearchEngine(BaseSearchEngine):
    """
    Search engine that performs text embedding and similarity search using OpenAI and TigerVector.
    """

    embedding_model: OpenAIEmbedding
    vector_db: TigerVectorManager

    def __init__(self, embedding_model: OpenAIEmbedding, vector_db: TigerVectorManager):
        """
        Initialize the TigerVectorSearchEngine.

        Args:
            embedding_model: The embedding model used for text-to-vector conversion.
            vector_db: The vector database for similarity search.
        """
        super().__init__(embedding_model, vector_db)
