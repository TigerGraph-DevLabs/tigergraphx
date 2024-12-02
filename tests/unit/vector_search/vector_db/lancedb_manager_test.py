import pytest
import pandas as pd
from unittest.mock import MagicMock

from tigergraphx import LanceDBManager, LanceDBConfig


class TestLanceDBManager:
    @pytest.fixture
    def lancedb_manager(self, mocker):
        # Mock LanceDB connection and table
        mock_connection = mocker.patch("lancedb.connect")
        mock_table = MagicMock()

        # Mock table functions and properties
        mock_connection.return_value.table_names.return_value = []
        mock_connection.return_value.create_table.return_value = mock_table
        mock_connection.return_value.open_table.return_value = mock_table

        # Initialize LanceDBManager instance
        manager = LanceDBManager(LanceDBConfig(type="LanceDB", uri="mock_uri"))
        manager._connection = mock_connection.return_value
        manager._table = mock_table
        return manager

    def test_connect_existing_table(self, lancedb_manager):
        manager = lancedb_manager
        assert manager._connection.create_table.call_count == 1
        assert manager._connection.open_table.call_count == 0

        # Mock the table already exists
        manager._connection.table_names.return_value = [manager.TABLE_NAME]

        # Re-run connect to check if it opens the existing table
        manager.connect("mock_uri")

        # Assert that open_table was called instead of create_table
        assert manager._connection.create_table.call_count == 1
        assert manager._connection.open_table.call_count == 1

    def test_connect_create_table(self, lancedb_manager):
        manager = lancedb_manager
        assert manager._connection.create_table.call_count == 1

        # Mock the table does not exist
        manager._connection.table_names.return_value = []

        # Re-run connect to check if it creates the table
        manager.connect("mock_uri")

        # Assert that create_table was called
        assert manager._connection.create_table.call_count == 2

    def test_insert_data(self, lancedb_manager):
        manager = lancedb_manager
        assert manager._connection.create_table.call_count == 1

        # Prepare mock data
        data = pd.DataFrame(
            [
                {
                    "id": "1",
                    "text": "test text",
                    "vector": [0.1, 0.2, 0.3],
                    "attributes": "{}",
                }
            ]
        )

        # Insert data
        manager.insert_data(data, overwrite=True)

        # Assert that create_table was called with overwrite
        assert manager._connection.create_table.call_count == 2

        # Test inserting without overwrite
        manager.insert_data(data, overwrite=False)
        assert manager._connection.create_table.call_count == 2
        assert manager._table.add.call_count == 1

    def test_delete_data(self, lancedb_manager):
        manager = lancedb_manager

        # Mock filtered data to be deleted
        manager._table.search.return_value.to_list.return_value = [{"id": "1"}]

        # Call delete_data with a condition
        filter_conditions = {"id": "1"}
        manager.delete_data(filter_conditions)

        # Ensure delete was called on each matching row
        assert manager._table.delete.call_count == 1

    def test_update_data(self, lancedb_manager):
        manager = lancedb_manager

        # Mock data to be updated
        manager._table.search.return_value.to_list.return_value = [
            {"id": "1", "text": "old text"}
        ]

        # Define filter and new data
        filter_conditions = {"id": "1"}
        new_data = {"text": "new text"}

        # Update data
        manager.update_data(filter_conditions, new_data)

        # Ensure the original row was deleted and new row was added
        assert manager._table.delete.call_count == 1
        assert manager._table.add.call_count == 1

    def test_query(self, lancedb_manager):
        manager = lancedb_manager

        # Mock search results for the query
        manager._table.search.return_value.limit.return_value.to_list.return_value = [
            {
                "id": "1",
                "text": "test text",
                "vector": [0.1, 0.2, 0.3],
                "attributes": "{}",
                "_distance": 0.1,
            }
        ]

        # Perform query
        result_list = manager.query(query_embedding=[0.1, 0.2, 0.3], k=1)

        # Check DataFrame contents
        assert len(result_list) == 1
        assert result_list[0] == "1"
