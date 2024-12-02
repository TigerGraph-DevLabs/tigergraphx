from abc import ABC, abstractmethod
from typing import Any, Dict, List
from pathlib import Path
import pandas as pd

from tigergraphx.config import BaseVectorDBConfig


class BaseVectorDB(ABC):
    """Abstract base class for managing vector database connections."""

    def __init__(self, config: BaseVectorDBConfig):
        """Initialize the base vector DB manager."""
        self.config = config

    @abstractmethod
    def connect(self, uri: str | Path, **kwargs: Any) -> None:
        """Connect to the vector database and set up the connection."""

    @abstractmethod
    def insert_data(self, data: pd.DataFrame, overwrite: bool = True) -> None:
        """Insert data into the vector database."""

    @abstractmethod
    def delete_data(self, filter_conditions: Dict[str, Any]) -> None:
        """Delete data from the vector database based on filter conditions."""

    @abstractmethod
    def update_data(
        self, filter_conditions: Dict[str, Any], new_data: Dict[str, Any]
    ) -> None:
        """Update existing data in the vector database based on filter conditions."""

    @abstractmethod
    def query(
        self,
        query_embedding: List[float],
        k: int = 10,
        **kwargs: Any,
    ) -> List[str]:
        """Perform a similarity search by vector and return results in the desired format."""
