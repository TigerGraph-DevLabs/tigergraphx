import pytest
from unittest.mock import MagicMock
from tigergraphx.core.managers.statistics_manager import StatisticsManager


class TestStatisticsManager:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.mock_tigergraph_api = MagicMock()
        self.mock_tigergraph_api.run_interpreted_query = MagicMock()
        mock_context = MagicMock()
        mock_context.tigergraph_api = self.mock_tigergraph_api
        self.statistics_manager = StatisticsManager(mock_context)

    def test_degree_success(self):
        node_id = "node1"
        node_type = "Person"
        edge_types = {"Friend"}
        self.mock_tigergraph_api.run_interpreted_query.return_value = [{"degree": 3}]
        result = self.statistics_manager.degree(node_id, node_type, edge_types)
        self.mock_tigergraph_api.run_interpreted_query.assert_called_once()
        assert result == 3

    def test_degree_no_result(self):
        node_id = "node2"
        node_type = "Person"
        edge_types = {"Friend"}
        self.mock_tigergraph_api.run_interpreted_query.return_value = []
        result = self.statistics_manager.degree(node_id, node_type, edge_types)
        self.mock_tigergraph_api.run_interpreted_query.assert_called_once()
        assert result == 0

    def test_degree_exception(self):
        node_id = "node3"
        node_type = "Person"
        edge_types = {"Friend"}
        self.mock_tigergraph_api.run_interpreted_query.side_effect = Exception("Error")
        result = self.statistics_manager.degree(node_id, node_type, edge_types)
        self.mock_tigergraph_api.run_interpreted_query.assert_called_once()
        assert result == 0

    def test_number_of_nodes_single_type(self):
        node_type = "Person"
        self.mock_tigergraph_api.run_interpreted_query.return_value = [{"number_of_nodes": 5}]
        result = self.statistics_manager.number_of_nodes(node_type)
        self.mock_tigergraph_api.run_interpreted_query.assert_called_once()
        assert result == 5

    def test_number_of_nodes_all_types(self):
        self.mock_tigergraph_api.run_interpreted_query.return_value = [{"number_of_nodes": 5}]
        result = self.statistics_manager.number_of_nodes()
        self.mock_tigergraph_api.run_interpreted_query.assert_called_once()
        assert result == 5

    def test_number_of_nodes_exception(self):
        self.mock_tigergraph_api.run_interpreted_query.side_effect = Exception("Error")
        result = self.statistics_manager.number_of_nodes()
        self.mock_tigergraph_api.run_interpreted_query.assert_called_once()
        assert result == 0

    def test_number_of_edges_single_type(self):
        edge_type = "Friend"
        self.mock_tigergraph_api.run_interpreted_query.return_value = [{"number_of_edges": 5}]
        result = self.statistics_manager.number_of_edges(edge_type)
        self.mock_tigergraph_api.run_interpreted_query.assert_called_once()
        assert result == 5

    def test_number_of_edges_all_types(self):
        self.mock_tigergraph_api.run_interpreted_query.return_value = [{"number_of_edges": 5}]
        result = self.statistics_manager.number_of_edges()
        self.mock_tigergraph_api.run_interpreted_query.assert_called_once()
        assert result == 5

    def test_number_of_edges_exception(self):
        self.mock_tigergraph_api.run_interpreted_query.side_effect = Exception("Error")
        result = self.statistics_manager.number_of_edges()
        self.mock_tigergraph_api.run_interpreted_query.assert_called_once()
        assert result == 0
