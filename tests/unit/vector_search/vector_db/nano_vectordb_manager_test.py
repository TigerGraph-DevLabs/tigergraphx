import pytest
from unittest.mock import MagicMock
import pandas as pd
import numpy as np
from tigergraphx.vector_search.vector_db.nano_vectordb_manager import (
    NanoVectorDBManager,
)
from tigergraphx.config import NanoVectorDBConfig


@pytest.fixture
def mock_db():
    config = NanoVectorDBConfig(embedding_dim=128, storage_file=":memory:")
    manager = NanoVectorDBManager(config=config)
    manager._db = MagicMock()
    return manager


class TestNanoVectorDBManager:
    def test_insert_data(self, mock_db):
        data = pd.DataFrame(
            {
                "__id__": ["id1", "id2"],
                "__vector__": [np.random.rand(128), np.random.rand(128)],
                "attribute": ["value1", "value2"],
            }
        )
        mock_db.insert_data(data)
        mock_db._db.upsert.assert_called_once()

    def test_query(self, mock_db):
        query_embedding = np.random.rand(128).tolist()
        mock_db._db.query.return_value = [{"__id__": "id1"}, {"__id__": "id2"}]
        result = mock_db.query(query_embedding, k=2)
        assert result == ["id1", "id2"]
