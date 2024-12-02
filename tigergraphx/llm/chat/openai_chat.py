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
        config = OpenAIChatConfig.ensure_config(config)
        super().__init__(config)
        self.llm = llm_manager.get_llm()
        self.retryer = self.initialize_retryer(self.config.max_retries, max_wait=10)

    async def chat(self, messages: List[ChatCompletionMessageParam]) -> str:
        """Asynchronously processes the messages and returns the generated response."""
        try:
            async for attempt in self.retryer:
                with attempt:
                    response = await self.llm.chat.completions.create(
                        messages=messages,
                        model=self.config.model,
                    )
                    return response.choices[0].message.content or ""
        except RetryError as e:
            # Log retry errors for traceability
            logger.error(f"RetryError in chat for message: {messages}... | {e}")
        except Exception as e:
            # Log and re-raise unexpected exceptions
            logger.error(f"Unhandled exception in chat: {e}")
            raise

        # Final return statement in case no return occurs in try-except block
        return ""
