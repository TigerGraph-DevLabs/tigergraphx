import pytest
from unittest.mock import MagicMock
from tigergraphx.core.managers.query_manager import QueryManager


class TestQueryManager:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.mock_connection = MagicMock()
        self.mock_connection.runInstalledQuery = MagicMock()

        mock_context = MagicMock()
        mock_context.connection = self.mock_connection
        self.query_manager = QueryManager(mock_context)

    def test_run_query_success(self):
        query_name = "test_query"
        params = {"param1": "value1"}
        self.mock_connection.runInstalledQuery.return_value = "result"
        result = self.query_manager.run_query(query_name, params)
        self.mock_connection.runInstalledQuery.assert_called_once_with(
            queryName=query_name, params=params
        )
        assert result == "result"

    def test_run_query_error(self):
        query_name = "test_query"
        params = {"param1": "value1"}
        self.mock_connection.runInstalledQuery.side_effect = Exception("Error")
        result = self.query_manager.run_query(query_name, params)
        self.mock_connection.runInstalledQuery.assert_called_once_with(
            queryName=query_name, params=params
        )
        assert result is None

    def test_get_nodes_success(self):
        node_type = "Person"
        self.query_manager.get_nodes_from_spec = MagicMock(return_value="nodes_df")
        result = self.query_manager.get_nodes(node_type)
        assert result == "nodes_df"

    def test_get_neighbors_success(self):
        start_nodes = "node1"
        start_node_type = "Person"
        self.query_manager.get_neighbors_from_spec = MagicMock(
            return_value="neighbors_df"
        )
        result = self.query_manager.get_neighbors(start_nodes, start_node_type)
        assert result == "neighbors_df"
