import pytest
from unittest.mock import patch

from tigergraphx.core.graph import Graph


class TestGraph:
    @pytest.fixture(autouse=True)
    def mock_api(self):
        with patch(
            "tigergraphx.core.tigergraph_api.api.admin_api.AdminAPI.get_version"
        ) as mock_get_version:
            mock_get_version.return_value = "4.2.0"
            yield

    def test_initialize_graph_with_lazy_mode(self):
        schema = {
            "graph_name": "LazyGraph",
            "nodes": {
                "Person": {"primary_key": "name", "attributes": {"name": "STRING"}},
                "Company": {
                    "primary_key": "id",
                    "attributes": {"id": "STRING", "name": "STRING"},
                },
            },
            "edges": {
                "WorksAt": {
                    "is_directed_edge": True,
                    "from_node_type": "Person",
                    "to_node_type": "Company",
                },
                "Knows": {
                    "is_directed_edge": False,
                    "from_node_type": "Person",
                    "to_node_type": "Person",
                },
            },
        }
        graph = Graph(graph_schema=schema, mode="lazy")
        assert graph.name == "LazyGraph"
        assert graph.node_types == {"Person", "Company"}
        assert graph.edge_types == {"WorksAt", "reverse_WorksAt", "Knows"}

    def test_validate_node_type_single_node_type(self):
        schema = {
            "graph_name": "SingleNodeTypeGraph",
            "nodes": {
                "Person": {"primary_key": "name", "attributes": {"name": "STRING"}}
            },
            "edges": {},
        }
        graph = Graph(graph_schema=schema, mode="lazy")
        assert graph._validate_node_type() == "Person"

    def test_validate_node_type_multiple_node_types(self):
        schema = {
            "graph_name": "MultiNodeTypeGraph",
            "nodes": {
                "Person": {"primary_key": "name", "attributes": {"name": "STRING"}},
                "Company": {
                    "primary_key": "id",
                    "attributes": {"id": "STRING", "name": "STRING"},
                },
            },
            "edges": {},
        }
        graph = Graph(graph_schema=schema, mode="lazy")
        with pytest.raises(ValueError, match="Multiple node types detected"):
            graph._validate_node_type()

    def test_validate_edge_type_single_edge_type(self):
        schema = {
            "graph_name": "SingleEdgeTypeGraph",
            "nodes": {
                "Person": {"primary_key": "name", "attributes": {"name": "STRING"}},
            },
            "edges": {
                "Knows": {
                    "is_directed_edge": False,
                    "from_node_type": "Person",
                    "to_node_type": "Person",
                },
            },
        }
        graph = Graph(graph_schema=schema, mode="lazy")
        src, edge, tgt = graph._validate_edge_type("Person", None, "Person")
        assert src == "Person"
        assert edge == "Knows"
        assert tgt == "Person"

    def test_validate_edge_type_multiple_edge_types(self):
        schema = {
            "graph_name": "MultiEdgeTypeGraph",
            "nodes": {
                "Person": {"primary_key": "name", "attributes": {"name": "STRING"}},
                "Company": {"primary_key": "id", "attributes": {"id": "STRING"}},
            },
            "edges": {
                "Knows": {
                    "is_directed_edge": False,
                    "from_node_type": "Person",
                    "to_node_type": "Person",
                },
                "WorksAt": {
                    "is_directed_edge": True,
                    "from_node_type": "Person",
                    "to_node_type": "Company",
                },
            },
        }
        graph = Graph(graph_schema=schema, mode="lazy")
        with pytest.raises(ValueError, match="Multiple edge types detected"):
            graph._validate_edge_type("Person", None, "Person")

    def test_validate_edge_types_none(self):
        schema = {
            "graph_name": "TestGraph",
            "nodes": {
                "Person": {"primary_key": "name", "attributes": {"name": "STRING"}}
            },
            "edges": {
                "Knows": {
                    "is_directed_edge": False,
                    "from_node_type": "Person",
                    "to_node_type": "Person",
                }
            },
        }
        graph = Graph(graph_schema=schema, mode="lazy")
        assert graph._validate_edge_types_as_set(None) is None

    def test_validate_edge_types_invalid(self):
        schema = {
            "graph_name": "TestGraph",
            "nodes": {
                "Person": {"primary_key": "name", "attributes": {"name": "STRING"}}
            },
            "edges": {
                "Knows": {
                    "is_directed_edge": False,
                    "from_node_type": "Person",
                    "to_node_type": "Person",
                }
            },
        }
        graph = Graph(graph_schema=schema, mode="lazy")
        with pytest.raises(ValueError, match="Invalid edge type"):
            graph._validate_edge_types_as_set(["UnknownEdge"])

    def test_to_str_node_id(self):
        assert Graph._to_str_node_id(123) == "123"
        assert Graph._to_str_node_id("Alice") == "Alice"

    def test_to_str_edge_ids(self):
        src, tgt = Graph._to_str_edge_ids(123, "Alice")
        assert src == "123"
        assert tgt == "Alice"

    def test_to_str_node_ids(self):
        node_ids = [123, "Alice", 456]
        assert Graph._to_str_node_ids(node_ids) == ["123", "Alice", "456"]

    def test_normalize_nodes_for_adding(self):
        nodes = [123, "Alice"]
        common_attr = {"group": "test"}
        expected = [("123", {"group": "test"}), ("Alice", {"group": "test"})]
        assert Graph._normalize_nodes_for_adding(nodes, **common_attr) == expected

        nodes_with_attrs = [("Alice", {"age": 30}), (123, {"age": 40})]
        expected_with_attrs = [
            ("Alice", {"age": 30, "group": "test"}),
            ("123", {"age": 40, "group": "test"}),
        ]
        assert (
            Graph._normalize_nodes_for_adding(nodes_with_attrs, **common_attr)
            == expected_with_attrs
        )

    def test_normalize_edges_for_adding(self):
        edges = [(123, "Alice"), ("Alice", "Bob")]
        common_attr = {"relationship": "friend"}
        expected = [
            ("123", "Alice", {"relationship": "friend"}),
            ("Alice", "Bob", {"relationship": "friend"}),
        ]
        assert Graph._normalize_edges_for_adding(edges, **common_attr) == expected

        edges_with_attrs = [
            (123, "Alice", {"weight": 1.0}),
            ("Alice", "Bob", {"weight": 2.0}),
        ]
        expected_with_attrs = [
            ("123", "Alice", {"weight": 1.0, "relationship": "friend"}),
            ("Alice", "Bob", {"weight": 2.0, "relationship": "friend"}),
        ]
        assert (
            Graph._normalize_edges_for_adding(edges_with_attrs, **common_attr)
            == expected_with_attrs
        )
