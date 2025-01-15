import logging
from pathlib import Path
from typing import List, Dict
from tenacity import RetryError
from openai.types.chat import ChatCompletionMessageParam

from .base_chat import BaseChat

from tigergraphx.config import OpenAIChatConfig
from tigergraphx.llm import OpenAIManager
from tigergraphx.utils import RetryMixin


logger = logging.getLogger(__name__)


class OpenAIChat(BaseChat, RetryMixin):
    """Implementation of BaseChat for OpenAI models."""

    config: OpenAIChatConfig

    def __init__(
        self,
        llm_manager: OpenAIManager,
        config: OpenAIChatConfig | Dict | str | Path,
    ):
        """
        Initialize the OpenAIChat with the provided LLM manager and configuration.

        Args:
            llm_manager: Manager for OpenAI LLM interactions.
            config: Configuration for OpenAI chat.
        """
        config = OpenAIChatConfig.ensure_config(config)
        super().__init__(config)
        self.llm = llm_manager.get_llm()
        self.retryer = self.initialize_retryer(self.config.max_retries, max_wait=10)

    async def chat(self, messages: List[ChatCompletionMessageParam]) -> str:
        """
        Asynchronously process the messages and return the generated response.

        Args:
            messages: List of messages for chat completion.

        Returns:
            The generated response.

        Raises:
            RetryError: If retry attempts are exhausted.
            Exception: For any unexpected errors during processing.
        """
        try:
            async for attempt in self.retryer:
                with attempt:
                    response = await self.llm.chat.completions.create(
                        messages=messages,
                        model=self.config.model,
                    )
                    return response.choices[0].message.content or ""
        except RetryError as e:
            logger.error(f"RetryError in chat for messages: {messages} | {e}")
            raise

        return ""
