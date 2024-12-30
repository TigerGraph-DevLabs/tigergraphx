from abc import ABC, abstractmethod
from typing import List
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
    def insert_data(self, data: pd.DataFrame) -> None:
        """
        Insert data into the vector database.

        Args:
            data (pd.DataFrame): The data to be inserted.
        """
        pass

    @abstractmethod
    def query(
        self,
        query_embedding: List[float],
        k: int = 10,
    ) -> List[str]:
        """
        Perform a similarity search by vector and return results in the desired format.

        Args:
            query_embedding (List[float]): The embedding vector to query.
            k (int, optional): Number of nearest neighbors to return. Defaults to 10.

        Returns:
            List[str]: List of result identifiers.
        """
        pass
