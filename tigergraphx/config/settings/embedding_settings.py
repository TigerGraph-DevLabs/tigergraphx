from pydantic import Field
from ..base_config import BaseConfig


class BaseEmbeddingConfig(BaseConfig):
    """Base configuration class for embedding models."""

    type: str = Field(
        description="Mandatory base type; derived classes can override or set a default."
    )


class OpenAIEmbeddingConfig(BaseEmbeddingConfig):
    """Configuration class for OpenAI Embedding models."""

    type: str = Field(
        default="OpenAI", description="Default type for OpenAIEmbeddingConfig."
    )
    model: str = Field(
        default="text-embedding-3-small", description="Default OpenAI embedding model."
    )
    max_tokens: int = Field(
        default=8191, description="Maximum number of tokens supported."
    )
    max_retries: int = Field(
        default=10, description="Maximum number of retries for API calls."
    )
    encoding_name: str = Field(
        default="cl100k_base", description="Token encoding name used by the model."
    )
