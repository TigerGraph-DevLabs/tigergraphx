import pytest
from unittest.mock import MagicMock
from tigergraphx.core.managers.statistics_manager import StatisticsManager


class TestStatisticsManager:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.mock_connection = MagicMock()
        self.mock_connection.runInstalledQuery = MagicMock()

        mock_context = MagicMock()
        mock_context.connection = self.mock_connection
        self.statistics_manager = StatisticsManager(mock_context)

    def test_degree_success(self):
        node_id = "node1"
        node_type = "Person"
        edge_types = "Friend"

        self.mock_connection.runInstalledQuery.return_value = [{"degree": 3}]

        result = self.statistics_manager.degree(node_id, node_type, edge_types)

        self.mock_connection.runInstalledQuery.assert_called_once_with(
            "api_degree",
            {
                "input": (node_id, node_type),
                "edge_types": edge_types,
            },
        )
        assert result == 3

    def test_degree_no_result(self):
        node_id = "node2"
        node_type = "Person"
        edge_types = "Friend"

        self.mock_connection.runInstalledQuery.return_value = []

        result = self.statistics_manager.degree(node_id, node_type, edge_types)

        self.mock_connection.runInstalledQuery.assert_called_once_with(
            "api_degree",
            {
                "input": (node_id, node_type),
                "edge_types": edge_types,
            },
        )
        assert result == 0

    def test_degree_exception(self):
        node_id = "node3"
        node_type = "Person"
        edge_types = "Friend"

        self.mock_connection.runInstalledQuery.side_effect = Exception("Error")

        result = self.statistics_manager.degree(node_id, node_type, edge_types)

        self.mock_connection.runInstalledQuery.assert_called_once_with(
            "api_degree",
            {
                "input": (node_id, node_type),
                "edge_types": edge_types,
            },
        )
        assert result == 0
