import pytest
from typing import Mapping

from tigergraphx import DataType, UndiGraph
from .base_graph_test import TestBaseGraph


class TestUndiGraph(TestBaseGraph):
    def setup_graph(self):
        """Set up the graph and add nodes and edges."""
        graph_name = "UndiGraph"
        node_primary_key = "id"
        node_attributes: Mapping = {
            "id": DataType.STRING,
            "entity_type": DataType.STRING,
            "description": DataType.STRING,
            "source_id": DataType.STRING,
        }
        edge_attributes: Mapping = {
            "weight": DataType.DOUBLE,
            "description": DataType.STRING,
            "keywords": DataType.STRING,
            "source_id": DataType.STRING,
        }
        self.G = UndiGraph(
            graph_name=graph_name,
            node_primary_key=node_primary_key,
            node_attributes=node_attributes,
            edge_attributes=edge_attributes,
        )

    @pytest.fixture(autouse=True)
    def add_nodes_and_edges(self):
        """Add nodes and edges before each test case."""
        # Initialize the graph
        self.setup_graph()

        # Adding nodes and edges
        self.G.add_node("A")
        self.G.add_node("B", entity_type="Org", description="This is B.")
        self.G.add_edge("A", "B", weight=2.1, keywords="This is an edge")

        yield  # The test case runs here

        self.G.clear()

    @pytest.fixture(scope="class", autouse=True)
    def drop_graph(self):
        """Drop the graph after all tests are done in the session."""
        yield
        self.setup_graph()
        self.G.drop_graph()

    def test_add_and_remove_nodes_and_edges(self):
        # Verify initial state
        assert self.G.has_node("A"), "Node A should exist"
        assert self.G.has_node("B"), "Node B should exist"
        assert not self.G.has_node("C"), "Node C should not exist"
        assert self.G.has_edge("A", "B"), "Edge A->B should exist"
        assert self.G.has_edge("B", "A"), "Edge B->A should exist"

        # # Removing edge
        # self.G.remove_edge("A", "B")
        # assert not self.G.has_edge("A", "B"), "Edge A->B should not exist after removal"
        #
        # # Removing nodes
        # self.G.remove_node("A")
        # assert not self.G.has_node("A"), "Node A should not exist after removal"
        # assert self.G.has_node("B"), "Node B should still exist"

    def test_node_and_edge_data(self):
        # Get node data
        node_data = self.time_execution(
            lambda: self.G.get_node_data("B"), "get_node_data"
        )
        assert node_data["entity_type"] == "Org", "Entity type of node B should be Org"
        assert (
            node_data["description"] == "This is B."
        ), "Description of node B should match"

        # Get edge data
        edge_data = self.time_execution(
            lambda: self.G.get_edge_data("A", "B"),
            "get_edge_data",
        )
        assert edge_data["weight"] == 2.1, "Weight of edge A->B should be 2.1"
        assert (
            edge_data["keywords"] == "This is an edge"
        ), "Keywords of edge A->B should match"

    def test_node_edges_count(self):
        # Counting edges
        assert len(self.G.get_node_edges("A")) == 1, "Node A should have 1 edge"
        assert len(self.G.get_node_edges("B")) == 1, "Node B should have 1 edge"

        # Reporting nodes, edges and neighbors
        ## has node/edge
        assert self.G.has_node("A")
        assert self.G.has_node("B")
        assert not self.G.has_node("C")
        assert not self.G.has_edge("A", "C")
        assert self.G.has_edge("A", "B")
        assert self.G.has_edge("B", "A")

        ## get node/edge data
        print()
        node_data = self.time_execution(
            lambda: self.G.get_node_data("B"), "get_node_data"
        )
        assert node_data["entity_type"] == "Org"
        assert node_data["description"] == "This is B."
        edge_data = self.time_execution(
            lambda: self.G.get_edge_data("A", "B"),
            "get_edge_data",
        )
        assert edge_data["weight"] == 2.1
        assert edge_data["keywords"] == "This is an edge"

        ## get node edges
        node_edges = self.time_execution(
            lambda: self.G.get_node_edges("A"),
            "get_node_edges",
        )
        assert len(node_edges) == 1
        node_edges = self.time_execution(
            lambda: self.G.get_node_edges("B"),
            "get_node_edges",
        )
        assert len(node_edges) == 1

        # Counting nodes edges and neighbors
        degree = self.time_execution(lambda: self.G.degree("A"), "degree")
        assert degree == 1
        degree = self.time_execution(lambda: self.G.degree("B"), "degree")
        assert degree == 1
