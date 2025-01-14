from unittest.mock import MagicMock
import pytest
from typing import List, Optional
import pandas as pd

from tigergraphx.core.view.node_view import NodeView


class MockGraph:
    def __init__(self, node_types: Optional[List[str]] = None):
        self.node_types = node_types or ["default"]
        # Setup mock methods for node operations.
        self.get_node_data = MagicMock(return_value={})
        self.has_node = MagicMock(return_value=False)
        self.get_nodes = MagicMock(return_value=pd.DataFrame())
        self.number_of_nodes = MagicMock(return_value=0)


class TestNodeView:
    def test_get_item_homogeneous(self):
        """Test __getitem__ for a homogeneous graph."""
        # Create a homogeneous graph (only one node type).
        graph = MockGraph(node_types=["default"])
        expected_data = {"name": "Alice"}
        graph.get_node_data = MagicMock(return_value=expected_data)

        node_view = NodeView(graph)
        # Pass a string key, which represents the node_id.
        data = node_view["node_1"]

        graph.get_node_data.assert_called_once_with(node_id="node_1")
        assert data == expected_data

    def test_get_item_heterogeneous(self):
        """Test __getitem__ for a heterogeneous graph."""
        # Create a heterogeneous graph (multiple node types).
        graph = MockGraph(node_types=["user", "item"])
        expected_data = {"name": "Bob"}
        graph.get_node_data = MagicMock(return_value=expected_data)

        node_view = NodeView(graph)
        # Pass a tuple key: (node_type, node_id)
        data = node_view[("user", "node_2")]

        graph.get_node_data.assert_called_once_with(node_type="user", node_id="node_2")
        assert data == expected_data

    def test_get_item_invalid_key(self):
        """Test __getitem__ raises ValueError for an invalid key type."""
        graph = MockGraph(node_types=["default"])
        node_view = NodeView(graph)

        # Using an invalid key type (e.g., int) should raise a ValueError.
        with pytest.raises(ValueError):
            _ = node_view[123]

    def test_contains_homogeneous(self):
        """Test __contains__ for a homogeneous graph."""
        graph = MockGraph(node_types=["default"])
        # Setup the has_node mock to return True.
        graph.has_node = MagicMock(return_value=True)

        node_view = NodeView(graph)
        result = "node_3" in node_view

        graph.has_node.assert_called_once_with(node_id="node_3")
        assert result is True

    def test_contains_heterogeneous(self):
        """Test __contains__ for a heterogeneous graph."""
        graph = MockGraph(node_types=["user", "item"])
        # Setup the has_node mock to return True.
        graph.has_node = MagicMock(return_value=True)

        node_view = NodeView(graph)
        result = ("item", "node_4") in node_view

        graph.has_node.assert_called_once_with(node_type="item", node_id="node_4")
        assert result is True

    def test_contains_invalid_key(self):
        """Test __contains__ raises ValueError for an invalid key type."""
        graph = MockGraph(node_types=["default"])
        node_view = NodeView(graph)

        with pytest.raises(ValueError):
            _ = 123 in node_view

    def test_iter_homogeneous(self):
        """Test __iter__ for a homogeneous graph to return just node IDs."""
        # Create a dataframe with node IDs only.
        df = pd.DataFrame({"v_id": ["node_1", "node_2", "node_3"]})
        graph = MockGraph(node_types=["default"])
        graph.get_nodes = MagicMock(return_value=df)

        node_view = NodeView(graph)
        # Iteration should only yield the 'v_id' values.
        node_ids = list(iter(node_view))
        assert node_ids == ["node_1", "node_2", "node_3"]

    def test_iter_heterogeneous(self):
        """Test __iter__ for a heterogeneous graph to return (node_type, node_id) pairs."""
        # Create a dataframe with both node IDs and types.
        df = pd.DataFrame({"v_id": ["node_1", "node_2"], "v_type": ["user", "item"]})
        graph = MockGraph(node_types=["user", "item"])
        graph.get_nodes = MagicMock(return_value=df)

        node_view = NodeView(graph)
        nodes = list(iter(node_view))
        # Each element should be a tuple (v_type, v_id).
        assert nodes == [("user", "node_1"), ("item", "node_2")]

    def test_len(self):
        """Test __len__ returns the correct number of nodes."""
        graph = MockGraph(node_types=["default"])
        # Setup the number_of_nodes mock to return 5.
        graph.number_of_nodes = MagicMock(return_value=5)

        node_view = NodeView(graph)
        assert len(node_view) == 5
