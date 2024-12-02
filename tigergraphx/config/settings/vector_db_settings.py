from typing import Optional, Union
from pathlib import Path
from lancedb import timedelta, ThreadPoolExecutor

from ..base_config import BaseConfig


class BaseVectorDBConfig(BaseConfig):
    """Base configuration class for vector databases."""

    type: str  # Mandatory type field to identify the database type.


class LanceDBConfig(BaseVectorDBConfig):
    """Configuration class for LanceDB."""

    type: str = "LanceDB"  # Default type for LanceDBConfig.
    table_name: str = (
        "entity_description_embeddings"  # Default table name for embeddings.
    )
    uri: Union[str, Path]  # URI or path to the LanceDB resource.
    api_key: Optional[str] = None  # API key for authentication, if required.
    region: str = "us-east-1"  # Default region for LanceDB.
    host_override: Optional[str] = None  # Host override for custom LanceDB endpoints.
    read_consistency_interval: Optional[timedelta] = (
        None  # Read consistency interval for queries.
    )
    request_thread_pool: Optional[Union[int, ThreadPoolExecutor]] = (
        None  # Thread pool for requests.
    )
