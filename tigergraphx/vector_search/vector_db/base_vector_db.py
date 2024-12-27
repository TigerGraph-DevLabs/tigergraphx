from abc import ABC, abstractmethod
from typing import Any, Dict, List
import pandas as pd

from tigergraphx.config import BaseVectorDBConfig


class BaseVectorDB(ABC):
    """Abstract base class for managing vector database connections."""

    def __init__(self, config: BaseVectorDBConfig):
        """
        Initialize the base vector DB manager.

        Args:
            config (BaseVectorDBConfig): Configuration for the vector database connection.
        """
        self.config = config

    @abstractmethod
    def insert_data(self, data: pd.DataFrame, overwrite: bool = True) -> None:
        """
        Insert data into the vector database.

        Args:
            data (pd.DataFrame): The data to be inserted.
            overwrite (bool, optional): Whether to overwrite existing data. Defaults to True.
        """
        pass

    @abstractmethod
    def delete_data(self, filter_conditions: Dict[str, Any]) -> None:
        """
        Delete data from the vector database based on filter conditions.

        Args:
            filter_conditions (Dict[str, Any]): Conditions to filter which data to delete.
        """
        pass

    @abstractmethod
    def update_data(
        self, filter_conditions: Dict[str, Any], new_data: Dict[str, Any]
    ) -> None:
        """
        Update existing data in the vector database based on filter conditions.

        Args:
            filter_conditions (Dict[str, Any]): Conditions to filter which data to update.
            new_data (Dict[str, Any]): New data to update the existing records with.
        """
        pass

    @abstractmethod
    def query(
        self,
        query_embedding: List[float],
        k: int = 10,
        **kwargs: Any,
    ) -> List[str]:
        """
        Perform a similarity search by vector and return results in the desired format.

        Args:
            query_embedding (List[float]): The embedding vector to query.
            k (int, optional): Number of nearest neighbors to return. Defaults to 10.
            **kwargs (Any): Additional keyword arguments for the query.

        Returns:
            List[str]: List of result identifiers.
        """
        pass
