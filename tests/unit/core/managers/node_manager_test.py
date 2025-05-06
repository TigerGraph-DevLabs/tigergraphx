import pytest
from unittest.mock import MagicMock

from tigergraphx.core.managers.node_manager import NodeManager

from tigergraphx.config import (
    GraphSchema,
    NodeSchema,
    AttributeSchema,
    DataType,
)


class TestNodeManager:
    @pytest.fixture(autouse=True)
    def setup(self):
        """Set up a mock context and NodeManager for all tests."""
        # Mocking the connection and graph schema
        self.mock_tigergraph_api = MagicMock()
        mock_context = MagicMock()
        mock_context.tigergraph_api = self.mock_tigergraph_api
        mock_context.graph_schema = GraphSchema(
            graph_name="MyGraph",
            nodes={
                "MyNode": NodeSchema(
                    primary_key="name",
                    attributes={
                        "name": AttributeSchema(data_type=DataType.STRING),
                        "value": AttributeSchema(data_type=DataType.BOOL),
                    },
                ),
            },
            edges={},
        )

        self.node_manager = NodeManager(mock_context)

    def test_add_nodes_from_single_node(self):
        """Test adding a single node with common attributes."""
        self.mock_tigergraph_api.upsert_graph_data.return_value = [
            {"accepted_vertices": 1, "accepted_edges": 0}
        ]
        normalized_nodes = [("node1", {"size": 10})]
        result = self.node_manager.add_nodes_from(normalized_nodes, "MyNode")
        assert result == 1
        self.mock_tigergraph_api.upsert_graph_data.assert_called_once_with(
            "MyGraph",
            {"vertices": {"MyNode": {"node1": {"size": {"value": 10}}}}},
        )

    def test_add_nodes_from_multiple_nodes(self):
        """Test adding multiple nodes with individual and common attributes."""
        self.mock_tigergraph_api.upsert_graph_data.return_value = [
            {"accepted_vertices": 2, "accepted_edges": 0}
        ]
        normalized_nodes = [
            ("node1", {"color": "red", "size": 10}),
            ("node2", {"size": 10}),
        ]
        result = self.node_manager.add_nodes_from(normalized_nodes, "MyNode")
        assert result == 2
        self.mock_tigergraph_api.upsert_graph_data.assert_called_once_with(
            "MyGraph",
            {
                "vertices": {
                    "MyNode": {
                        "node1": {"color": {"value": "red"}, "size": {"value": 10}},
                        "node2": {"size": {"value": 10}},
                    }
                }
            },
        )

    def test_add_nodes_from_upsert_exception(self):
        """Test that an exception in upsertVertices is handled correctly."""
        self.mock_tigergraph_api.upsert_graph_data.side_effect = Exception(
            "Upsert error"
        )
        normalized_nodes = [("node1", {"size": 10})]
        result = self.node_manager.add_nodes_from(normalized_nodes, "MyNode")
        assert result is None
        self.mock_tigergraph_api.upsert_graph_data.assert_called_once_with(
            "MyGraph",
            {"vertices": {"MyNode": {"node1": {"size": {"value": 10}}}}},
        )

    def test_remove_node_success(self):
        """Test that remove_node returns True when a node is successfully removed."""
        node_id = "node1"
        node_type = "Person"
        self.mock_tigergraph_api.delete_a_node.return_value = {"deleted_vertices": 1}
        result = self.node_manager.remove_node(node_id, node_type)
        self.mock_tigergraph_api.delete_a_node.assert_called_once_with(
            "MyGraph", node_type, node_id
        )
        assert result is True

    def test_remove_node_not_exists(self):
        """Test that remove_node returns False when the node does not exist."""
        node_id = "node2"
        node_type = "Person"
        self.mock_tigergraph_api.delete_a_node.return_value = {"deleted_vertices": 0}
        result = self.node_manager.remove_node(node_id, node_type)
        self.mock_tigergraph_api.delete_a_node.assert_called_once_with(
            "MyGraph", node_type, node_id
        )
        assert result is False

    def test_remove_node_exception(self):
        """Test that remove_node returns False when an exception occurs."""
        node_id = "node3"
        node_type = "Person"
        self.mock_tigergraph_api.delete_a_node.side_effect = Exception("Error")
        result = self.node_manager.remove_node(node_id, node_type)
        self.mock_tigergraph_api.delete_a_node.assert_called_once_with(
            "MyGraph", node_type, node_id
        )
        assert result is False

    def test_has_node_exists(self):
        node_id = "node1"
        node_type = "Person"

        self.mock_tigergraph_api.retrieve_a_node.return_value = [{"id": node_id}]

        result = self.node_manager.has_node(node_id, node_type)

        self.mock_tigergraph_api.retrieve_a_node.assert_called_once_with(
            "MyGraph", node_type, node_id
        )
        assert result is True

    def test_has_node_not_exists(self):
        node_id = "node2"
        node_type = "Person"
        self.mock_tigergraph_api.retrieve_a_node.return_value = []
        result = self.node_manager.has_node(node_id, node_type)
        self.mock_tigergraph_api.retrieve_a_node.assert_called_once_with(
            "MyGraph", node_type, node_id
        )
        assert result is False

    def test_get_node_data_success(self):
        node_id = "node1"
        node_type = "Person"
        self.mock_tigergraph_api.retrieve_a_node.return_value = [
            {"attributes": {"name": "Alice"}}
        ]
        result = self.node_manager.get_node_data(node_id, node_type)
        self.mock_tigergraph_api.retrieve_a_node.assert_called_once_with(
            "MyGraph", node_type, node_id
        )
        assert result == {"name": "Alice"}

    def test_get_node_data_failure(self):
        node_id = "node2"
        node_type = "Person"
        self.mock_tigergraph_api.retrieve_a_node.return_value = []
        result = self.node_manager.get_node_data(node_id, node_type)
        self.mock_tigergraph_api.retrieve_a_node.assert_called_once_with(
            "MyGraph", node_type, node_id
        )
        assert result is None

    def test_get_node_edges_success(self):
        node_id = "node1"
        node_type = "Person"
        edge_types = {"Friend"}
        self.mock_tigergraph_api.run_interpreted_query.return_value = [
            {
                "edges": [
                    {"from_id": "node1", "to_id": "node2"},
                    {
                        "from_id": "node1",
                        "to_id": "node3",
                        "discriminator": "2024-01-01T00:00:00",
                    },
                ]
            }
        ]
        result = self.node_manager.get_node_edges(node_id, node_type, edge_types)
        self.mock_tigergraph_api.run_interpreted_query.assert_called_once()
        assert result == [("node1", "node2"), ("node1", "node3", "2024-01-01T00:00:00")]

    def test_get_node_edges_failure(self):
        node_id = "node2"
        node_type = "Person"
        edge_types = {"Friend"}

        self.mock_tigergraph_api.run_interpreted_query.side_effect = Exception("Error")

        result = self.node_manager.get_node_edges(node_id, node_type, edge_types)

        self.mock_tigergraph_api.run_interpreted_query.assert_called_once()
        assert result == []

    def test_clear(self):
        """Test the clear method of NodeManager."""
        self.mock_tigergraph_api.delete_nodes = MagicMock()

        self.node_manager.clear()

        self.mock_tigergraph_api.delete_nodes.assert_any_call("MyGraph", "MyNode")
        assert self.mock_tigergraph_api.delete_nodes.call_count == 1
