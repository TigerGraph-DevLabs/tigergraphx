from typing import Dict
from pathlib import Path
from openai import AsyncOpenAI

from .base_llm_manager import BaseLLMManager
from ..config import OpenAIConfig


class OpenAIManager(BaseLLMManager):
    """Manages an asynchronous OpenAI instance for LLM operations."""

    config: OpenAIConfig

    def __init__(
        self,
        config: OpenAIConfig | Dict | str | Path,
    ):
        """Initialize OpenAIManager with OpenAI settings."""
        config = OpenAIConfig.ensure_config(config)
        super().__init__(config)
        if not self.config.api_key:
            raise ValueError("API key is required to initialize OpenAIManager.")

        # Initialize the LLM immediately
        self._llm: AsyncOpenAI = AsyncOpenAI(
            api_key=self.config.api_key,
            base_url=self.config.base_url,
            organization=self.config.organization,
            timeout=self.config.request_timeout,
            max_retries=self.config.max_retries,
        )

    def get_llm(self) -> AsyncOpenAI:
        """Retrieve the initialized async OpenAI instance."""
        return self._llm
