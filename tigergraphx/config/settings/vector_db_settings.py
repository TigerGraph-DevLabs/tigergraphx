from typing import Optional
from pathlib import Path
from lancedb import timedelta, ThreadPoolExecutor
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


class LanceDBConfig(BaseVectorDBConfig):
    """Configuration class for LanceDB."""

    type: str = Field(default="LanceDB", description="Default type for LanceDBConfig.")
    table_name: str = Field(
        default="entity_description_embeddings",
        description="Default table name for embeddings.",
    )
    uri: str | Path = Field(description="URI or path to the LanceDB resource.")
    api_key: Optional[str] = Field(
        default=None, description="API key for authentication, if required."
    )
    region: str = Field(default="us-east-1", description="Default region for LanceDB.")
    host_override: Optional[str] = Field(
        default=None, description="Host override for custom LanceDB endpoints."
    )
    read_consistency_interval: Optional[timedelta] = Field(
        default=None, description="Read consistency interval for queries."
    )
    request_thread_pool: Optional[int | ThreadPoolExecutor] = Field(
        default=None, description="Thread pool for managing requests."
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
