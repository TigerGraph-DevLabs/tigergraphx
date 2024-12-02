from ..base_config import BaseConfig


class BaseEmbeddingConfig(BaseConfig):
    """Base configuration class for embedding models."""

    type: str  # Mandatory base type; derived classes can override or set a default.


class OpenAIEmbeddingConfig(BaseEmbeddingConfig):
    """Configuration class for OpenAI Embedding models."""

    type: str = "OpenAI"  # Default type for OpenAIEmbeddingConfig.
    model: str = "text-embedding-3-small"  # Default OpenAI model.
    max_tokens: int = 8191  # Maximum number of tokens supported.
    max_retries: int = 10  # Maximum number of retries for API calls.
    encoding_name: str = "cl100k_base"  # Token encoding name.
