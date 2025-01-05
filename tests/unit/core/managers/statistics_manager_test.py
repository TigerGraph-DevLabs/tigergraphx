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
        self.mock_connection.runInterpretedQuery.return_value = [{"degree": 3}]
        result = self.statistics_manager.degree(node_id, node_type, edge_types)
        self.mock_connection.runInterpretedQuery.assert_called_once()
        assert result == 3

    def test_degree_no_result(self):
        node_id = "node2"
        node_type = "Person"
        edge_types = "Friend"
        self.mock_connection.runInterpretedQuery.return_value = []
        result = self.statistics_manager.degree(node_id, node_type, edge_types)
        self.mock_connection.runInterpretedQuery.assert_called_once()
        assert result == 0

    def test_degree_exception(self):
        node_id = "node3"
        node_type = "Person"
        edge_types = "Friend"
        self.mock_connection.runInterpretedQuery.side_effect = Exception("Error")
        result = self.statistics_manager.degree(node_id, node_type, edge_types)
        self.mock_connection.runInterpretedQuery.assert_called_once()
        assert result == 0

    def test_number_of_nodes_single_type(self):
        node_type = "Person"
        self.mock_connection.getVertexCount.return_value = 5
        result = self.statistics_manager.number_of_nodes(node_type)
        self.mock_connection.getVertexCount.assert_called_once_with(node_type)
        assert result == 5

    def test_number_of_nodes_multiple_types(self):
        node_type = ["Person", "Company"]
        self.mock_connection.getVertexCount.return_value = {"Person": 3, "Company": 2}
        result = self.statistics_manager.number_of_nodes(node_type)
        self.mock_connection.getVertexCount.assert_called_once_with(node_type)
        assert result == 5

    def test_number_of_nodes_all_types(self):
        self.mock_connection.getVertexCount.return_value = {"Person": 3, "Company": 2}
        result = self.statistics_manager.number_of_nodes()
        self.mock_connection.getVertexCount.assert_called_once_with("*")
        assert result == 5

    def test_number_of_nodes_exception(self):
        self.mock_connection.getVertexCount.side_effect = Exception("Error")
        result = self.statistics_manager.number_of_nodes()
        self.mock_connection.getVertexCount.assert_called_once_with("*")
        assert result == 0

    def test_number_of_edges_single_type(self):
        edge_type = "Friend"
        self.mock_connection.getEdgeCount.return_value = 10
        result = self.statistics_manager.number_of_edges(edge_type)
        self.mock_connection.getEdgeCount.assert_called_once_with(edge_type)
        assert result == 10

    def test_number_of_edges_all_types(self):
        self.mock_connection.getEdgeCount.return_value = {"Friend": 7, "Colleague": 5}
        result = self.statistics_manager.number_of_edges()
        self.mock_connection.getEdgeCount.assert_called_once_with("*")
        assert result == 12

    def test_number_of_edges_exception(self):
        self.mock_connection.getEdgeCount.side_effect = Exception("Error")
        result = self.statistics_manager.number_of_edges()
        self.mock_connection.getEdgeCount.assert_called_once_with("*")
        assert result == 0
