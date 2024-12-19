from abc import ABC, abstractmethod
from typing import List, Any

from tigergraphx.config import BaseChatConfig


class BaseChat(ABC):
    """Base class for chat models."""

    def __init__(self, config: BaseChatConfig):
        """
        Initialize the chat model with the given configuration.

        Args:
            config (BaseChatConfig): Configuration for the chat model.
        """
        self.config = config

    @abstractmethod
    async def chat(self, messages: List[Any]) -> str:
        """
        Asynchronously process the messages and return the generated response.

        Args:
            messages (List[Any]): A list of messages to process.

        Returns:
            str: The generated response.
        """
        pass
