from ..base_config import BaseConfig


class BaseChatConfig(BaseConfig):
    """Base configuration class for chat models."""

    type: str  # Mandatory base type; derived classes can override or set a default.


class OpenAIChatConfig(BaseChatConfig):
    """Configuration class for OpenAI Chat models."""

    type: str = "OpenAI"  # Default type for OpenAIChatConfig.
    model: str = "gpt-4o-mini"  # Default OpenAI model.
    max_retries: int = 10  # Maximum number of retries for API calls.
