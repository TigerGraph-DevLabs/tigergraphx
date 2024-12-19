from abc import ABC, abstractmethod
from typing import List

from tigergraphx.config import BaseEmbeddingConfig


class BaseEmbedding(ABC):
    """Base class for text embedding models."""

    def __init__(self, config: BaseEmbeddingConfig):
        """
        Initialize the base embedding model.

        Args:
            config (BaseEmbeddingConfig): Configuration for the embedding model.
        """
        self.config = config

    @abstractmethod
    async def generate_embedding(self, text: str) -> List[float]:
        """
        Asynchronously generate embeddings for a given text.

        Args:
            text (str): The input text to generate embeddings for.

        Returns:
            List[float]: A list of floats representing the text embedding.
        """
        pass
