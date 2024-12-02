from abc import ABC, abstractmethod
from typing import List, Any

from tigergraphx.config import BaseChatConfig


class BaseChat(ABC):
    """Base class for chat models."""

    def __init__(self, config: BaseChatConfig):
        """Initialize the chat model with the given configuration.."""
        self.config = config

    @abstractmethod
    async def chat(self, messages: List[Any]) -> str:
        """Asynchronously processes the messages and returns the generated response."""
        pass
