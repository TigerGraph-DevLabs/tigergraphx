from abc import ABC, abstractmethod
from typing import Any

from tigergraphx.config import BaseLLMConfig


class BaseLLMManager(ABC):
    """Base class for LLM implementations."""

    def __init__(self, config: BaseLLMConfig):
        """
        Initialize the base LLM manager.

        Args:
            config (BaseLLMConfig): Configuration for the LLM.
        """
        self.config = config

    @abstractmethod
    def get_llm(self) -> Any:
        """
        Retrieve the initialized LLM instance.

        Returns:
            Any: The initialized LLM instance.
        """
        pass
