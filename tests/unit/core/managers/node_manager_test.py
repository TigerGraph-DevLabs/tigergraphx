import pytest
from unittest.mock import MagicMock
from tigergraphx.core.managers.node_manager import NodeManager


class TestNodeManager:
    @pytest.fixture(autouse=True)
    def setup(self):
        """Set up a mock context and NodeManager for all tests."""
        # Mocking the connection and graph schema
        self.mock_connection = MagicMock()
        mock_context = MagicMock()
        mock_context.connection = self.mock_connection  # Use the mocked connection
        self.mock_graph_schema = MagicMock()
        mock_context.graph_schema = self.mock_graph_schema
        self.node_manager = NodeManager(mock_context)

    def test_add_nodes_from_single_node(self):
        """Test adding a single node with common attributes."""
        self.mock_connection.upsertVertices.return_value = 1
        normalized_nodes = [("node1", {"size": 10})]
        result = self.node_manager.add_nodes_from(normalized_nodes, "MyNode")
        assert result == 1
        self.mock_connection.upsertVertices.assert_called_once_with(
            vertexType="MyNode",
            vertices=normalized_nodes,
        )

    def test_add_nodes_from_multiple_nodes(self):
        """Test adding multiple nodes with individual and common attributes."""
        self.mock_connection.upsertVertices.return_value = 2
        normalized_nodes = [
            ("node1", {"color": "red", "size": 10}),
            ("node2", {"size": 10}),
        ]
        result = self.node_manager.add_nodes_from(normalized_nodes, "MyNode")
        assert result == 2
        self.mock_connection.upsertVertices.assert_called_once_with(
            vertexType="MyNode",
            vertices=normalized_nodes,
        )

    def test_add_nodes_from_upsert_exception(self):
        """Test that an exception in upsertVertices is handled correctly."""
        self.mock_connection.upsertVertices.side_effect = Exception("Upsert error")
        normalized_nodes = [("node1", {"size": 10})]
        result = self.node_manager.add_nodes_from(normalized_nodes, "MyNode")
        assert result is None
        self.mock_connection.upsertVertices.assert_called_once_with(
            vertexType="MyNode",
            vertices=normalized_nodes,
        )

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

        self.mock_connection.runInterpretedQuery.return_value = [
            {"edges": ["edge1", "edge2"]}
        ]

        result = self.node_manager.get_node_edges(node_id, node_type, edge_types)

        self.mock_connection.runInterpretedQuery.assert_called_once()
        assert result == ["edge1", "edge2"]

    def test_get_node_edges_failure(self):
        node_id = "node2"
        node_type = "Person"
        edge_types = "Friend"

        self.mock_connection.runInterpretedQuery.side_effect = Exception("Error")

        result = self.node_manager.get_node_edges(node_id, node_type, edge_types)

        self.mock_connection.runInterpretedQuery.assert_called_once()
        assert result == []

    def test_clear(self):
        """Test the clear method of NodeManager."""
        # Define mock behavior
        self.mock_graph_schema.nodes = {"Entity1": {}, "Entity2": {}}
        self.mock_connection.delVertices = MagicMock()

        # Run the clear method
        self.node_manager.clear()

        # Assert delVertices was called for each node type
        self.mock_connection.delVertices.assert_any_call("Entity1")
        self.mock_connection.delVertices.assert_any_call("Entity2")

        # Check that delVertices was called exactly twice, once for each node type
        assert self.mock_connection.delVertices.call_count == 2
