from pathlib import Path
from pydantic import Field

from ..base_config import BaseConfig


class BaseVectorDBConfig(BaseConfig):
    """Base configuration class for vector databases."""

    type: str = Field(description="Mandatory type field to identify the database type.")


class TigerVectorConfig(BaseVectorDBConfig):
    """Configuration class for TigerVector."""

    type: str = Field(
        default="TigerVector",
        description="Default type for TigerVectorConfig.",
    )
    graph_name: str = Field(description="The name of the graph to be used.")
    node_type: str = Field(
        default="MyNode", description="The default node type for storing embeddings."
    )
    vector_attribute_name: str = Field(
        description="The name of the vector attribute for embeddings."
    )


class NanoVectorDBConfig(BaseVectorDBConfig):
    """Configuration class for NanoVectorDB."""

    type: str = Field(
        default="NanoVectorDB", description="Default type for NanoVectorDBConfig."
    )
    storage_file: str | Path = Field(
        default="nano-vectordb.json",
        description="Path to the storage file for NanoVectorDB.",
    )
    embedding_dim: int = Field(
        default=1536, description="Default embedding dimension for NanoVectorDB."
    )
