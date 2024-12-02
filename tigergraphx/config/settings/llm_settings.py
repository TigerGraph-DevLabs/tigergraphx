from typing import Optional
from pydantic import Field

from ..base_config import BaseConfig


class BaseLLMConfig(BaseConfig):
    """Base configuration class for LLM."""

    type: str  # Mandatory type field for identifying the LLM type.


class OpenAIConfig(BaseLLMConfig):
    """Configuration class for OpenAI."""

    type: str = "OpenAI"  # Default type for OpenAIConfig.
    api_key: str = Field(alias="OPENAI_API_KEY")  # API key for authentication.
    base_url: Optional[str] = None  # Custom base URL for OpenAI API.
    organization: Optional[str] = None  # OpenAI organization ID (if applicable).
    max_retries: int = 10  # Maximum number of retries for failed API requests.
    request_timeout: float = 180.0  # Request timeout in seconds.
