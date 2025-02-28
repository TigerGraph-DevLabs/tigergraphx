# Copyright 2025 TigerGraph Inc.
# Licensed under the Apache License, Version 2.0.
# See the LICENSE file or https://www.apache.org/licenses/LICENSE-2.0
#
# Permission is granted to use, copy, modify, and distribute this software
# under the License. The software is provided "AS IS", without warranty.

from abc import ABC, abstractmethod
from typing import List

from tigergraphx.config import BaseEmbeddingConfig


class BaseEmbedding(ABC):
    """Base class for text embedding models."""

    def __init__(self, config: BaseEmbeddingConfig):
        """
        Initialize the base embedding model.

        Args:
            config: Configuration for the embedding model.
        """
        self.config = config

    @abstractmethod
    async def generate_embedding(self, text: str) -> List[float]:
        """
        Asynchronously generate an embedding for the given text.

        Args:
            text: Input text to generate an embedding.

        Returns:
            A list of floats representing the text embedding.
        """
        pass
