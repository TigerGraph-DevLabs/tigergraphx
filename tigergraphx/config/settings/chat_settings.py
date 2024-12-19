from pydantic import Field
from ..base_config import BaseConfig


class BaseChatConfig(BaseConfig):
    """
    Base configuration class for chat models.
    """

    type: str = Field(
        description="Mandatory base type; derived classes can override or set a default."
    )


class OpenAIChatConfig(BaseChatConfig):
    """
    Configuration class for OpenAI Chat models.
    """

    type: str = Field(
        default="OpenAI", description="Default type for OpenAIChatConfig."
    )
    model: str = Field(default="gpt-4o-mini", description="Default OpenAI model.")
    max_retries: int = Field(
        default=10, description="Maximum number of retries for API calls."
    )
