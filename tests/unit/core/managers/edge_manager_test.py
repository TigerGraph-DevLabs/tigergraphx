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

    def test_add_edges_from_valid_data(self):
        """Test adding edges with valid data, including normalization."""
        normalized_edges = [
            ("1", "2", {}),  # Normalized edge with string IDs
            ("NodeB", "NodeC", {"weight": 1.0}),  # Already normalized
        ]
        src_node_type = "Entity"
        edge_type = "transfer"
        tgt_node_type = "Entity"

        self.mock_connection.upsertEdges.return_value = len(normalized_edges)
        result = self.edge_manager.add_edges_from(
            normalized_edges, src_node_type, edge_type, tgt_node_type
        )

        self.mock_connection.upsertEdges.assert_called_once_with(
            sourceVertexType=src_node_type,
            edgeType=edge_type,
            targetVertexType=tgt_node_type,
            edges=normalized_edges,
        )
        assert result == len(normalized_edges)

    def test_add_edges_from_upsert_exception(self):
        """Test that an exception in upsertEdges is handled correctly."""
        normalized_edges = [
            ("1", "2", {"attr": "value"}),
            ("NodeA", "NodeB", {}),
        ]
        src_node_type = "Entity"
        edge_type = "transfer"
        tgt_node_type = "Entity"

        self.mock_connection.upsertEdges.side_effect = Exception("Upsert error")
        result = self.edge_manager.add_edges_from(
            normalized_edges, src_node_type, edge_type, tgt_node_type
        )

        self.mock_connection.upsertEdges.assert_called_once_with(
            sourceVertexType=src_node_type,
            edgeType=edge_type,
            targetVertexType=tgt_node_type,
            edges=normalized_edges,
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

    def test_get_edge_data_single_edge_success(self):
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

    def test_get_edge_data_no_edges(self):
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
        assert result is None

    def test_get_edge_data_multi_edge_with_discriminator(self):
        src_node_id = "node1"
        tgt_node_id = "node2"
        src_node_type = "Person"
        edge_type = "Friend"
        tgt_node_type = "Person"

        self.mock_connection.getEdges.return_value = [
            {"discriminator": "best_friend", "attributes": {"since": 2020}},
            {"discriminator": "colleague", "attributes": {"since": 2019}},
        ]

        result = self.edge_manager.get_edge_data(
            src_node_id, tgt_node_id, src_node_type, edge_type, tgt_node_type
        )

        assert result == {
            "best_friend": {"since": 2020},
            "colleague": {"since": 2019},
        }

    def test_get_edge_data_multi_edge_without_discriminator(self):
        src_node_id = "node1"
        tgt_node_id = "node2"
        src_node_type = "Person"
        edge_type = "Friend"
        tgt_node_type = "Person"

        self.mock_connection.getEdges.return_value = [
            {"attributes": {"since": 2020}},
            {"attributes": {"since": 2019}},
        ]

        result = self.edge_manager.get_edge_data(
            src_node_id, tgt_node_id, src_node_type, edge_type, tgt_node_type
        )

        assert result == {
            0: {"since": 2020},
            1: {"since": 2019},
        }

    def test_get_edge_data_invalid_edge_format(self):
        src_node_id = "node1"
        tgt_node_id = "node2"
        src_node_type = "Person"
        edge_type = "Friend"
        tgt_node_type = "Person"

        self.mock_connection.getEdges.return_value = [
            "invalid_edge",  # Not a dict
            {"attributes": {"since": 2021}},  # Valid edge
        ]

        result = self.edge_manager.get_edge_data(
            src_node_id, tgt_node_id, src_node_type, edge_type, tgt_node_type
        )

        assert result == {"since": 2021}

    def test_get_edge_data_unexpected_return_type(self):
        src_node_id = "node1"
        tgt_node_id = "node2"
        src_node_type = "Person"
        edge_type = "Friend"
        tgt_node_type = "Person"

        self.mock_connection.getEdges.return_value = "unexpected_string"

        result = self.edge_manager.get_edge_data(
            src_node_id, tgt_node_id, src_node_type, edge_type, tgt_node_type
        )

        assert result is None  # Should return None for unexpected response

    def test_get_edge_data_exception_handling(self):
        src_node_id = "node1"
        tgt_node_id = "node2"
        src_node_type = "Person"
        edge_type = "Friend"
        tgt_node_type = "Person"

        self.mock_connection.getEdges.side_effect = Exception("Test exception")

        result = self.edge_manager.get_edge_data(
            src_node_id, tgt_node_id, src_node_type, edge_type, tgt_node_type
        )

        assert result is None  # Should return None on exception
