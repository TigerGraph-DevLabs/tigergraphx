from abc import ABC, abstractmethod
from typing import List

from tigergraphx.config import BaseEmbeddingConfig


class BaseEmbedding(ABC):
    """Base class for text embedding models."""

    def __init__(self, config: BaseEmbeddingConfig):
        """Initialize the base embedding model."""
        self.config = config

    @abstractmethod
    async def generate_embedding(self, text: str) -> List[float]:
        """Asynchronously generate embeddings for a given text."""
        pass
