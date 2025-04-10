import pytest
from unittest.mock import MagicMock

from tigergraphx.core.managers.edge_manager import EdgeManager

from tigergraphx.config import (
    GraphSchema,
    NodeSchema,
    EdgeSchema,
    AttributeSchema,
    DataType,
)


class TestEdgeManager:
    @pytest.fixture(autouse=True)
    def setup(self):
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
            edges={
                "MyEdge": EdgeSchema(
                    from_node_type="MyNode",
                    to_node_type="MyNode",
                )
            },
        )
        self.edge_manager = EdgeManager(mock_context)

    def test_add_edges_from_valid_data(self):
        """Test adding edges with valid data, including normalization."""
        normalized_edges = [
            ("1", "2", {}),  # Normalized edge with string IDs
            ("NodeB", "NodeC", {"weight": 1.0}),  # Already normalized
        ]
        src_node_type = "MyNode"
        edge_type = "MyEdge"
        tgt_node_type = "MyNode"

        self.mock_tigergraph_api.upsert_graph_data.return_value = [
            {"accepted_vertices": 0, "accepted_edges": len(normalized_edges)}
        ]
        result = self.edge_manager.add_edges_from(
            normalized_edges, src_node_type, edge_type, tgt_node_type
        )

        self.mock_tigergraph_api.upsert_graph_data.assert_called_once_with(
            "MyGraph",
            {
                "edges": {
                    "MyNode": {
                        "1": {"MyEdge": {"MyNode": {"2": {}}}},
                        "NodeB": {
                            "MyEdge": {"MyNode": {"NodeC": {"weight": {"value": 1.0}}}}
                        },
                    }
                }
            },
        )
        assert result == len(normalized_edges)

    def test_add_edges_from_upsert_exception(self):
        """Test that an exception in upsertEdges is handled correctly."""
        normalized_edges = [
            ("1", "2", {"attr": "value"}),
            ("NodeA", "NodeB", {}),
        ]
        src_node_type = "MyNode"
        edge_type = "MyEdge"
        tgt_node_type = "MyNode"

        self.mock_tigergraph_api.upsert_graph_data.side_effect = Exception(
            "Upsert error"
        )
        result = self.edge_manager.add_edges_from(
            normalized_edges, src_node_type, edge_type, tgt_node_type
        )

        self.mock_tigergraph_api.upsert_graph_data.assert_called_once_with(
            "MyGraph",
            {
                "edges": {
                    "MyNode": {
                        "1": {
                            "MyEdge": {"MyNode": {"2": {"attr": {"value": "value"}}}}
                        },
                        "NodeA": {"MyEdge": {"MyNode": {"NodeB": {}}}},
                    }
                }
            },
        )
        assert result is None

    def test_has_edge_exists(self):
        src_node_id = "node1"
        tgt_node_id = "node2"
        src_node_type = "Person"
        edge_type = "Friend"
        tgt_node_type = "Person"

        self.mock_tigergraph_api.retrieve_a_edge.return_value = [
            {
                "e_type": edge_type,
                "directed": False,
                "from_id": src_node_id,
                "from_type": src_node_type,
                "to_id": tgt_node_id,
                "to_type": tgt_node_id,
                "attributes": {},
            }
        ]

        result = self.edge_manager.has_edge(
            src_node_id, tgt_node_id, src_node_type, edge_type, tgt_node_type
        )

        self.mock_tigergraph_api.retrieve_a_edge.assert_called_once_with(
            graph_name="MyGraph",
            source_node_type=src_node_type,
            source_node_id=src_node_id,
            edge_type=edge_type,
            target_node_type=tgt_node_type,
            target_node_id=tgt_node_id,
        )
        assert result is True

    def test_has_edge_not_exists(self):
        src_node_id = "node1"
        tgt_node_id = "node2"
        src_node_type = "Person"
        edge_type = "Friend"
        tgt_node_type = "Person"

        self.mock_tigergraph_api.retrieve_a_edge.return_value = []

        result = self.edge_manager.has_edge(
            src_node_id, tgt_node_id, src_node_type, edge_type, tgt_node_type
        )

        self.mock_tigergraph_api.retrieve_a_edge.assert_called_once_with(
            graph_name="MyGraph",
            source_node_type=src_node_type,
            source_node_id=src_node_id,
            edge_type=edge_type,
            target_node_type=tgt_node_type,
            target_node_id=tgt_node_id,
        )
        assert result is False

    def test_get_edge_data_single_edge_success(self):
        src_node_id = "node1"
        tgt_node_id = "node2"
        src_node_type = "Person"
        edge_type = "Friend"
        tgt_node_type = "Person"

        self.mock_tigergraph_api.retrieve_a_edge.return_value = [
            {
                "e_type": edge_type,
                "directed": False,
                "from_id": src_node_id,
                "from_type": src_node_type,
                "to_id": tgt_node_id,
                "to_type": tgt_node_id,
                "attributes": {"since": 2021},
            }
        ]

        result = self.edge_manager.get_edge_data(
            src_node_id, tgt_node_id, src_node_type, edge_type, tgt_node_type
        )

        self.mock_tigergraph_api.retrieve_a_edge.assert_called_once_with(
            graph_name="MyGraph",
            source_node_type=src_node_type,
            source_node_id=src_node_id,
            edge_type=edge_type,
            target_node_type=tgt_node_type,
            target_node_id=tgt_node_id,
        )
        assert result == {"since": 2021}

    def test_get_edge_data_no_edges(self):
        src_node_id = "node1"
        tgt_node_id = "node2"
        src_node_type = "Person"
        edge_type = "Friend"
        tgt_node_type = "Person"

        self.mock_tigergraph_api.retrieve_a_edge.return_value = []

        result = self.edge_manager.get_edge_data(
            src_node_id, tgt_node_id, src_node_type, edge_type, tgt_node_type
        )

        self.mock_tigergraph_api.retrieve_a_edge.assert_called_once_with(
            graph_name="MyGraph",
            source_node_type=src_node_type,
            source_node_id=src_node_id,
            edge_type=edge_type,
            target_node_type=tgt_node_type,
            target_node_id=tgt_node_id,
        )
        assert result is None

    def test_get_edge_data_multi_edge_with_discriminator(self):
        src_node_id = "node1"
        tgt_node_id = "node2"
        src_node_type = "Person"
        edge_type = "Friend"
        tgt_node_type = "Person"

        self.mock_tigergraph_api.retrieve_a_edge.return_value = [
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

        self.mock_tigergraph_api.retrieve_a_edge.return_value = [
            {
                "e_type": edge_type,
                "directed": False,
                "from_id": src_node_id,
                "from_type": src_node_type,
                "to_id": tgt_node_id,
                "to_type": tgt_node_id,
                "attributes": {"since": 2020},
            },
            {
                "e_type": edge_type,
                "directed": False,
                "from_id": src_node_id,
                "from_type": src_node_type,
                "to_id": tgt_node_id,
                "to_type": tgt_node_id,
                "attributes": {"since": 2019},
            },
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

        self.mock_tigergraph_api.retrieve_a_edge.return_value = [
            "invalid_edge",  # Not a dict
            {
                "e_type": edge_type,
                "directed": False,
                "from_id": src_node_id,
                "from_type": src_node_type,
                "to_id": tgt_node_id,
                "to_type": tgt_node_id,
                "attributes": {"since": 2021},
            },  # Valid edge
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

        self.mock_tigergraph_api.retrieve_a_edge.return_value = "unexpected_string"

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

        self.mock_tigergraph_api.retrieve_a_edge.side_effect = Exception("Test exception")

        result = self.edge_manager.get_edge_data(
            src_node_id, tgt_node_id, src_node_type, edge_type, tgt_node_type
        )

        assert result is None  # Should return None on exception
