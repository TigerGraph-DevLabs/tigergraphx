from tigergraphx import DataType, UndiGraph
from .base_graph_test import TestBaseGraph


class TestUndiGraph(TestBaseGraph):
    def set_up(self):
        graph_name = "UndiGraph"
        node_primary_key = "id"
        node_attributes = {
            "id": DataType.STRING,
            "entity_type": DataType.STRING,
            "description": DataType.STRING,
            "source_id": DataType.STRING,
        }
        edge_attributes = {
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

    def test_undigraph(self):
        # Set up
        self.set_up()
        # Adding and removing nodes and edges
        self.G.add_node("A")
        self.G.add_node("B", entity_type="Org", description="This is B.")
        self.G.add_edge("A", "B", weight=2.1, keywords="This is an edge")

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
