import pytest
from unittest.mock import MagicMock
from tigergraphx.core.managers.node_manager import NodeManager


class TestNodeManager:
    @pytest.fixture(autouse=True)
    def setup(self):
        """Set up a mock context and NodeManager for all tests."""
        self.mock_connection = MagicMock()
        mock_context = MagicMock()
        mock_context.connection = self.mock_connection  # Use the mocked connection
        mock_context.graph_schema = MagicMock()
        self.node_manager = NodeManager(mock_context)

    def test_add_node_success(self):
        """Test that add_node calls upsertVertex on success."""
        node_id = "node1"
        node_type = "Person"
        attributes = {"name": "Alice"}
        self.mock_connection.upsertVertex.return_value = None
        result = self.node_manager.add_node(node_id, node_type, **attributes)
        self.mock_connection.upsertVertex.assert_called_once_with(
            node_type, node_id, attributes
        )
        assert result is None

    def test_add_node_failure(self):
        """Test that add_node handles exceptions gracefully."""
        node_id = "node2"
        node_type = "Person"
        attributes = {"name": "Bob"}
        self.mock_connection.upsertVertex.side_effect = Exception("Error")
        result = self.node_manager.add_node(node_id, node_type, **attributes)
        self.mock_connection.upsertVertex.assert_called_once_with(
            node_type, node_id, attributes
        )
        assert result is None

    def test_remove_node_success(self):
        """Test that remove_node returns True when a node is successfully removed."""
        node_id = "node1"
        node_type = "Person"
        self.mock_connection.delVerticesById.return_value = 1
        result = self.node_manager.remove_node(node_id, node_type)
        self.mock_connection.delVerticesById.assert_called_once_with(node_type, node_id)
        assert result is True

    def test_remove_node_not_exists(self):
        """Test that remove_node returns False when the node does not exist."""
        node_id = "node2"
        node_type = "Person"
        self.mock_connection.delVerticesById.return_value = 0
        result = self.node_manager.remove_node(node_id, node_type)
        self.mock_connection.delVerticesById.assert_called_once_with(node_type, node_id)
        assert result is False

    def test_remove_node_exception(self):
        """Test that remove_node returns False when an exception occurs."""
        node_id = "node3"
        node_type = "Person"
        self.mock_connection.delVerticesById.side_effect = Exception("Error")
        result = self.node_manager.remove_node(node_id, node_type)
        self.mock_connection.delVerticesById.assert_called_once_with(node_type, node_id)
        assert result is False

    def test_has_node_exists(self):
        node_id = "node1"
        node_type = "Person"

        self.mock_connection.getVerticesById.return_value = [{"id": node_id}]

        result = self.node_manager.has_node(node_id, node_type)

        self.mock_connection.getVerticesById.assert_called_once_with(node_type, node_id)
        assert result is True

    def test_has_node_not_exists(self):
        node_id = "node2"
        node_type = "Person"
        self.mock_connection.getVerticesById.return_value = []
        result = self.node_manager.has_node(node_id, node_type)
        self.mock_connection.getVerticesById.assert_called_once_with(node_type, node_id)
        assert result is False

    def test_get_node_data_success(self):
        node_id = "node1"
        node_type = "Person"
        self.mock_connection.getVerticesById.return_value = [
            {"attributes": {"name": "Alice"}}
        ]
        result = self.node_manager.get_node_data(node_id, node_type)
        self.mock_connection.getVerticesById.assert_called_once_with(
            vertexType=node_type, vertexIds=node_id
        )
        assert result == {"name": "Alice"}

    def test_get_node_data_failure(self):
        node_id = "node2"
        node_type = "Person"
        self.mock_connection.getVerticesById.return_value = []
        result = self.node_manager.get_node_data(node_id, node_type)
        self.mock_connection.getVerticesById.assert_called_once_with(
            vertexType=node_type, vertexIds=node_id
        )
        assert result is None

    def test_get_node_edges_success(self):
        node_id = "node1"
        node_type = "Person"
        edge_types = "Friend"
        num_edge_samples = 1000

        self.mock_connection.runInstalledQuery.return_value = [
            {"edges": ["edge1", "edge2"]}
        ]

        result = self.node_manager.get_node_edges(
            node_id, node_type, edge_types, num_edge_samples
        )

        self.mock_connection.runInstalledQuery.assert_called_once_with(
            "api_get_node_edges",
            f"input={node_id}&input.type={node_type}&edge_types={edge_types}&num_edge_samples={num_edge_samples}",
        )
        assert result == ["edge1", "edge2"]

    def test_get_node_edges_failure(self):
        node_id = "node2"
        node_type = "Person"
        edge_types = "Friend"
        num_edge_samples = 1000

        self.mock_connection.runInstalledQuery.side_effect = Exception("Error")

        result = self.node_manager.get_node_edges(
            node_id, node_type, edge_types, num_edge_samples
        )

        self.mock_connection.runInstalledQuery.assert_called_once_with(
            "api_get_node_edges",
            f"input={node_id}&input.type={node_type}&edge_types={edge_types}&num_edge_samples={num_edge_samples}",
        )
        assert result == []
