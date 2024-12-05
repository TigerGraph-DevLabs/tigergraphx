from unittest.mock import MagicMock
import pytest
import pandas as pd

from tigergraphx.core.graph.base_graph import BaseGraph
from tigergraphx.core.view.node_view import NodeView


class MockGraph(BaseGraph):
    def __init__(self, node_type=None):
        self.node_type = node_type
        self._node_manager = MagicMock()
        self._node_manager.get_node_data = MagicMock(return_value={})
        self._node_manager.has_node = MagicMock(return_value=False)
        self._statistics_manager = MagicMock()
        self._statistics_manager.number_of_nodes = MagicMock(return_value=0)

    def _get_node_data(self, node_id: str, node_type: str) -> dict:
        return self._node_manager.get_node_data(node_id, node_type)

    def _has_node(self, node_id: str, node_type: str) -> bool:
        return self._node_manager.has_node(node_id, node_type)


class TestNodeView:
    def test_get_item_homogeneous(self):
        graph = MockGraph(node_type="Person")
        node_view = NodeView(graph)
        node_view.graph._node_manager.get_node_data.return_value = {
            "type": "Person",
            "id": "123",
        }
        result = node_view["123"]
        assert result == {"type": "Person", "id": "123"}

    def test_get_item_heterogeneous(self):
        graph = MockGraph()
        node_view = NodeView(graph)
        node_view.graph._node_manager.get_node_data.return_value = {
            "type": "Animal",
            "id": "456",
        }
        result = node_view[("Animal", "456")]
        assert result == {"type": "Animal", "id": "456"}

    def test_get_item_invalid_key(self):
        graph = MockGraph()
        node_view = NodeView(graph)
        with pytest.raises(ValueError):
            node_view[123]  # Invalid key for heterogeneous graph

    def test_get_item_invalid_tuple(self):
        graph = MockGraph()
        node_view = NodeView(graph)
        with pytest.raises(ValueError):
            node_view[("Animal",)]  # Invalid tuple length

    def test_contains_homogeneous(self):
        graph = MockGraph(node_type="Person")
        node_view = NodeView(graph)
        graph._node_manager.has_node.return_value = True
        assert "123" in node_view

    def test_contains_heterogeneous(self):
        graph = MockGraph()
        node_view = NodeView(graph)
        graph._node_manager.has_node.return_value = True
        assert ("Animal", "456") in node_view

    def test_contains_invalid_key(self):
        graph = MockGraph()
        node_view = NodeView(graph)
        with pytest.raises(ValueError):
            print("invalid_key" in node_view)  # Invalid key for homogeneous graph

    def test_contains_invalid_tuple(self):
        graph = MockGraph()
        node_view = NodeView(graph)
        with pytest.raises(ValueError):
            node_view[("Animal",)]  # Invalid tuple length

    def test_iter_homogeneous(self):
        graph = MockGraph(node_type="Person")
        graph._get_nodes = MagicMock(
            return_value=pd.DataFrame([
                {"v_id": "1"},
                {"v_id": "2"},
                {"v_id": "3"},
            ])
        )
        node_view = NodeView(graph)
        result = list(node_view)
        expected = ["1", "2", "3"]
        assert result == expected

    def test_iter_heterogeneous(self):
        graph = MockGraph()
        graph._get_nodes = MagicMock(
            return_value=pd.DataFrame([
                {"v_type": "Person", "v_id": "1"},
                {"v_type": "Company", "v_id": "2"},
                {"v_type": "Person", "v_id": "3"},
            ])
        )
        node_view = NodeView(graph)
        result = list(node_view)
        expected = [("Person", "1"), ("Company", "2"), ("Person", "3")]
        assert result == expected

    def test_len_homogeneous(self):
        graph = MockGraph(node_type="Person")
        graph._statistics_manager.number_of_nodes.return_value = 3
        node_view = NodeView(graph)
        assert len(node_view) == 3

    def test_len_heterogeneous(self):
        graph = MockGraph()
        graph._statistics_manager.number_of_nodes.return_value = 5
        node_view = NodeView(graph)
        assert len(node_view) == 5
