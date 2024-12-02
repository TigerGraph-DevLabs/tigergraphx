import pytest
from unittest.mock import MagicMock

from tigergraphx.core.managers.edge_manager import EdgeManager


class TestEdgeManager:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.mock_connection = MagicMock()
        self.mock_connection.upsertEdge = MagicMock()
        self.mock_connection.getEdgeCountFrom = MagicMock()
        self.mock_connection.getEdges = MagicMock()

        mock_context = MagicMock()
        mock_context.connection = self.mock_connection
        self.edge_manager = EdgeManager(mock_context)

    def test_add_edge_success(self):
        src_node_id = "node1"
        tgt_node_id = "node2"
        src_node_type = "Person"
        edge_type = "Friend"
        tgt_node_type = "Person"
        attributes = {"since": 2021}

        self.mock_connection.upsertEdge.return_value = None

        result = self.edge_manager.add_edge(
            src_node_id,
            tgt_node_id,
            src_node_type,
            edge_type,
            tgt_node_type,
            **attributes,
        )

        self.mock_connection.upsertEdge.assert_called_once_with(
            src_node_type,
            src_node_id,
            edge_type,
            tgt_node_type,
            tgt_node_id,
            attributes,
        )
        assert result is None

    def test_add_edge_failure(self):
        src_node_id = "node1"
        tgt_node_id = "node2"
        src_node_type = "Person"
        edge_type = "Friend"
        tgt_node_type = "Person"
        attributes = {"since": 2021}

        self.mock_connection.upsertEdge.side_effect = Exception("Error")

        result = self.edge_manager.add_edge(
            src_node_id,
            tgt_node_id,
            src_node_type,
            edge_type,
            tgt_node_type,
            **attributes,
        )

        self.mock_connection.upsertEdge.assert_called_once_with(
            src_node_type,
            src_node_id,
            edge_type,
            tgt_node_type,
            tgt_node_id,
            attributes,
        )
        assert result is None

    def test_has_edge_exists(self):
        src_node_id = "node1"
        tgt_node_id = "node2"
        src_node_type = "Person"
        edge_type = "Friend"
        tgt_node_type = "Person"

        self.mock_connection.getEdgeCountFrom.return_value = 1

        result = self.edge_manager.has_edge(
            src_node_id, tgt_node_id, src_node_type, edge_type, tgt_node_type
        )

        self.mock_connection.getEdgeCountFrom.assert_called_once_with(
            src_node_type, src_node_id, edge_type, tgt_node_type, tgt_node_id
        )
        assert result is True

    def test_has_edge_not_exists(self):
        src_node_id = "node1"
        tgt_node_id = "node2"
        src_node_type = "Person"
        edge_type = "Friend"
        tgt_node_type = "Person"

        self.mock_connection.getEdgeCountFrom.return_value = 0

        result = self.edge_manager.has_edge(
            src_node_id, tgt_node_id, src_node_type, edge_type, tgt_node_type
        )

        self.mock_connection.getEdgeCountFrom.assert_called_once_with(
            src_node_type, src_node_id, edge_type, tgt_node_type, tgt_node_id
        )
        assert result is False

    def test_get_edge_data_success(self):
        src_node_id = "node1"
        tgt_node_id = "node2"
        src_node_type = "Person"
        edge_type = "Friend"
        tgt_node_type = "Person"

        self.mock_connection.getEdges.return_value = [{"attributes": {"since": 2021}}]

        result = self.edge_manager.get_edge_data(
            src_node_id, tgt_node_id, src_node_type, edge_type, tgt_node_type
        )

        self.mock_connection.getEdges.assert_called_once_with(
            src_node_type, src_node_id, edge_type, tgt_node_type, tgt_node_id
        )
        assert result == {"since": 2021}

    def test_get_edge_data_failure(self):
        src_node_id = "node1"
        tgt_node_id = "node2"
        src_node_type = "Person"
        edge_type = "Friend"
        tgt_node_type = "Person"

        self.mock_connection.getEdges.return_value = []

        result = self.edge_manager.get_edge_data(
            src_node_id, tgt_node_id, src_node_type, edge_type, tgt_node_type
        )

        self.mock_connection.getEdges.assert_called_once_with(
            src_node_type, src_node_id, edge_type, tgt_node_type, tgt_node_id
        )
        assert result == {}
