import pytest
import time

from .base_graph_test import TestBaseGraph

from tigergraphx.core import Graph
from tigergraphx.vector_search import TigerVectorManager


class TestTigerVector(TestBaseGraph):
    def setup_graph(self):
        """Set up the graph and add nodes and edges."""
        graph_schema = {
            "graph_name": "TigerVector",
            "nodes": {
                "Entity": {
                    "primary_key": "id",
                    "attributes": {
                        "id": "STRING",
                        "entity_type": "STRING",
                        "description": "STRING",
                        "source_id": "STRING",
                    },
                    "vector_attributes": {"emb_description": 3},
                },
            },
            "edges": {
                "relationship": {
                    "is_directed_edge": True,
                    "from_node_type": "Entity",
                    "to_node_type": "Entity",
                    "attributes": {
                        "weight": "DOUBLE",
                        "description": "STRING",
                        "keywords": "STRING",
                        "source_id": "STRING",
                    },
                },
            },
        }
        self.G = Graph(graph_schema=graph_schema)

    @pytest.fixture(autouse=True)
    def add_nodes_and_edges(self):
        """Add nodes and edges before each test case."""
        # Initialize the graph
        self.setup_graph()

        # Adding nodes and edges
        self.G.add_nodes_from(
            [
                (
                    "Entity_1",
                    {
                        "entity_type": "Person",
                        "description": "Desc1",
                        "source_id": "Source1",
                        "emb_description": [-0.01773, -0.01019, -0.01657],
                    },
                ),
                (
                    "Entity_2",
                    {
                        "entity_type": "Person",
                        "description": "Desc2",
                        "source_id": "Source2",
                        "emb_description": [-0.01926, 0.000496, 0.00671],
                    },
                ),
            ]
        )
        self.G.add_edge(
            "Entity_1",
            "Entity_2",
            "Entity",
            "relationship",
            "Entity",
            weight=1.0,
            description="Relates to",
            keywords="key1,key2",
            source_id="SourceRel",
        )
        time.sleep(3)

        yield  # The test case runs here

        self.G.clear()

    @pytest.fixture(scope="class", autouse=True)
    def drop_graph(self):
        """Drop the graph after all tests are done in the session."""
        yield
        self.setup_graph()
        self.G.drop_graph()

    def test_vector_search(self):
        assert self.G.has_node("Entity_1")
        assert self.G.has_node("Entity_2")
        assert self.G.has_edge(
            "Entity_1", "Entity_2", "Entity", "relationship", "Entity"
        )
        query_vector = [-0.01926, 0.000496, 0.00671]
        results = self.G.vector_search(query_vector, "emb_description", k=1)
        assert len(results) == 1
        results = self.G.vector_search(query_vector, "emb_description", k=2)
        assert len(results) == 2

    def test_tigervector_manager(self):
        config = {
            "type": "TigerVector",
            "graph_name": "TigerVector",
            "node_type": "Entity",
            "vector_attribute_name": "emb_description",
        }
        manager = TigerVectorManager(config, self.G)
        query_vector = [-0.01926, 0.000496, 0.00671]
        results = manager.query(query_vector, k=1)
        assert len(results) == 1
        results = manager.query(query_vector, k=2)
        assert len(results) == 2
