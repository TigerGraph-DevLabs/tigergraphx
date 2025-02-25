# Copyright 2025 TigerGraph Inc.
# Licensed under the Apache License, Version 2.0.
# See the LICENSE file or https://www.apache.org/licenses/LICENSE-2.0
#
# Permission is granted to use, copy, modify, and distribute this software
# under the License. The software is provided "AS IS", without warranty.

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
