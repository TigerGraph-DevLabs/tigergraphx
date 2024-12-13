from typing import Any, Dict, List, TypedDict
from pathlib import Path
import pandas as pd
import numpy as np
from nano_vectordb import NanoVectorDB

from .base_vector_db import BaseVectorDB

from tigergraphx.config import NanoVectorDBConfig

Data = TypedDict("Data", {"__id__": str, "__vector__": np.ndarray})


class NanoVectorDBManager(BaseVectorDB):
    """A wrapper class for NanoVectorDB that implements BaseVectorDB."""

    config: NanoVectorDBConfig

    def __init__(
        self,
        config: NanoVectorDBConfig,
    ):
        """Initialize the NanoVectorDBWrapper."""
        super().__init__(config)
        self._db = NanoVectorDB(
            embedding_dim=config.embedding_dim, storage_file=str(config.storage_file)
        )

    def connect(self, uri: str | Path, **kwargs: Any) -> None:
        """Connect to the vector database and set up the connection."""
        # NanoVectorDB does not require an explicit connection step.
        pass

    def insert_data(self, data: pd.DataFrame, overwrite: bool = True) -> None:
        """Insert data into NanoVectorDB."""
        records = []
        for _, row in data.iterrows():
            record = {"__id__": row["__id__"], "__vector__": row["__vector__"]}
            for col in data.columns:
                if col not in ["__id__", "__vector__"]:
                    record[col] = row[col]
            records.append(record)

        self._db.upsert(records)

    def delete_data(self, filter_conditions: Dict[str, Any]) -> None:
        """Delete data from NanoVectorDB based on filter conditions."""

        def filter_fn(data: Data) -> bool:
            return all(
                data.get(key) == value for key, value in filter_conditions.items()
            )

        ids_to_delete = [
            data["__id__"]
            for data in self._db.query(
                query=np.zeros(self._db.embedding_dim), filter_lambda=filter_fn
            )
        ]
        self._db.delete(ids_to_delete)

    def update_data(
        self, filter_conditions: Dict[str, Any], new_data: Dict[str, Any]
    ) -> None:
        """Update existing data in NanoVectorDB."""

        def filter_fn(data: Data) -> bool:
            return all(
                data.get(key) == value for key, value in filter_conditions.items()
            )

        records_to_update = self._db.query(
            query=np.zeros(self._db.embedding_dim), filter_lambda=filter_fn
        )

        updated_records = []
        for record in records_to_update:
            record.update(new_data)
            updated_records.append(record)

        self._db.upsert(updated_records)

    def query(
        self,
        query_embedding: List[float],
        k: int = 10,
        **kwargs: Any,
    ) -> List[str]:
        """Perform a similarity search and return results."""
        results = self._db.query(query=np.array(query_embedding), top_k=k)
        return [result["__id__"] for result in results]
