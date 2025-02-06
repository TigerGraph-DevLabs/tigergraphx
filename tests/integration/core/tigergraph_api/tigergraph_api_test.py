import pytest
from requests.exceptions import ConnectionError

from tigergraphx.core import Graph
from tigergraphx.core.tigergraph_api import TigerGraphAPI
from tigergraphx.config import TigerGraphConnectionConfig


class TestTigerGraphAPI:
    def setup_graph(self):
        """Set up the graph and add nodes and edges."""
        graph_schema = {
            "graph_name": "ERGraph",
            "nodes": {
                "Entity": {
                    "primary_key": "id",
                    "attributes": {
                        "id": "STRING",
                        "entity_type": "STRING",
                        "description": "STRING",
                        "source_id": "STRING",
                    },
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
        self.tigergraph_connection_config = TigerGraphConnectionConfig(
            # username="tigergraph",
            # password="tigergraph",
            secret="rgtf030s4kfcsv2ahpnkljcafrclafos",
        )
        self.G = Graph(
            graph_schema=graph_schema,
            tigergraph_connection_config=self.tigergraph_connection_config,
        )

    @pytest.fixture(autouse=True)
    def init(self):
        """Add nodes and edges before each test case."""
        # Initialize the graph
        self.setup_graph()

        # Initialize the TigerGraphAPI
        self.api = TigerGraphAPI(self.tigergraph_connection_config)

        yield  # The test case runs here

        self.G.clear()

    @pytest.fixture(scope="class", autouse=True)
    def drop_graph(self):
        """Drop the graph after all tests are done in the session."""
        yield
        self.setup_graph()
        self.G.drop_graph()

    def test_connection_failure(self, mocker):
        """
        Test handling of a connection failure to the TigerGraph server.
        """
        mocker.patch.object(
            self.api.session,
            "request",
            side_effect=ConnectionError("Failed to connect"),
        )

        graph_name = "UserProductGraph"

        with pytest.raises(ConnectionError, match="Failed to connect to TigerGraph"):
            self.api.get_schema(graph_name)

    def test_gsql(self):
        """
        Integration test for the TigerGraph gsql endpoint.
        """
        result = self.api.gsql("ls")

        assert isinstance(result, dict), "Response should be a dictionary."
        assert "text" in result
        assert "Global vertices, edges, and all graphs" in result["text"]

    def test_ping(self):
        """
        Integration test for the TigerGraph ping endpoint.
        """
        result = self.api.ping()

        assert isinstance(result, dict), "Response should be a dictionary."
        assert "message" in result
        assert result["message"] == "pong", "Response should be 'pong'."

    def test_get_schema_integration(self):
        """
        Integration test for retrieving the schema of a graph.

        Assumes the TigerGraph instance is running and accessible with default settings.
        """

        graph_name = "ERGraph"
        result = self.api.get_schema(graph_name)

        # Assertions for structured response
        assert isinstance(result, dict), "Response should be a dictionary."

        # JSON response (schema)
        assert "GraphName" in result, "Schema should contain 'GraphName'."
        assert result["GraphName"] == graph_name, f"GraphName should be '{graph_name}'."
        assert "VertexTypes" in result, "Schema should contain 'VertexTypes'."
        assert "EdgeTypes" in result, "Schema should contain 'EdgeTypes'."

    def test_get_schema_graph_not_found(self):
        """
        Test behavior when retrieving a schema for a non-existent graph.
        """
        graph_name = "NonExistentGraph"

        with pytest.raises(
            ValueError,
            match="TigerGraph API Error: Graph 'NonExistentGraph' does not exist.",
        ):
            self.api.get_schema(graph_name)
