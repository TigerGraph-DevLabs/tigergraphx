from typing import List
import pandas as pd
import numpy as np
from nano_vectordb import NanoVectorDB

from .base_vector_db import BaseVectorDB

from tigergraphx.config import NanoVectorDBConfig


class NanoVectorDBManager(BaseVectorDB):
    """A wrapper class for NanoVectorDB that implements BaseVectorDB."""

    config: NanoVectorDBConfig

    def __init__(
        self,
        config: NanoVectorDBConfig,
    ):
        """
        Initialize the NanoVectorDBWrapper.

        Args:
            config (NanoVectorDBConfig): Configuration for NanoVectorDB.
        """
        super().__init__(config)
        self._db = NanoVectorDB(
            embedding_dim=config.embedding_dim, storage_file=str(config.storage_file)
        )

    def insert_data(self, data: pd.DataFrame) -> None:
        """
        Insert data into NanoVectorDB.

        Args:
            data (pd.DataFrame): DataFrame containing the data to insert.
        """
        records = []
        for _, row in data.iterrows():
            record = {"__id__": row["__id__"], "__vector__": row["__vector__"]}
            for col in data.columns:
                if col not in ["__id__", "__vector__"]:
                    record[col] = row[col]
            records.append(record)

        self._db.upsert(records)

    def query(
        self,
        query_embedding: List[float],
        k: int = 10,
    ) -> List[str]:
        """
        Perform a similarity search and return results.

        Args:
            query_embedding (List[float]): Query embedding vector for similarity search.
            k (int, optional): Number of top results to retrieve. Defaults to 10.

        Returns:
            List[str]: List of IDs from the search results.
        """
        results = self._db.query(query=np.array(query_embedding), top_k=k)
        return [result["__id__"] for result in results]
