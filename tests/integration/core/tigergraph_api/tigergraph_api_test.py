import pytest
from requests.exceptions import ConnectionError
from pydantic import HttpUrl
from pathlib import Path
import yaml

from tigergraphx.core import Graph
from tigergraphx.core.tigergraph_api import TigerGraphAPI, TigerGraphAPIError
from tigergraphx.config import TigerGraphConnectionConfig


class TestTigerGraphAPI:
    def setup_graph(self):
        """Set up the graph and add nodes and edges."""
        self.graph_name = "ERGraph"
        graph_schema = {
            "graph_name": self.graph_name,
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
        # Load config from YAML
        config_path = (
            Path(__file__).parent.parent / "config" / "tigergraph_connection.yaml"
        )
        with open(config_path, "r") as f:
            config_dict = yaml.safe_load(f)

        # Parse with TigerGraphConnectionConfig
        self.tigergraph_connection_config = TigerGraphConnectionConfig(
            host=HttpUrl(config_dict["host"]),
            username=config_dict["username"],
            password=config_dict["password"],
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

        # Add nodes
        self.G.add_node(
            "Entity_1",
            "Entity",
            entity_type="Type1",
            description="Desc1",
            source_id="Source1",
        )

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

    # ------------------------------ Admin ------------------------------
    def test_ping(self):
        """
        Integration test for the TigerGraph ping endpoint.
        """
        result = self.api.ping()

        assert isinstance(result, str), "Response should be a str."
        assert result == "pong", "Response should be 'pong'."

    # ------------------------------ GSQL ------------------------------
    def test_gsql(self):
        """
        Integration test for the TigerGraph gsql endpoint.
        """
        result = self.api.gsql("ls")

        assert isinstance(result, str), "Response should be a string."
        assert "Global vertices, edges, and all graphs" in result

    # ------------------------------ Schema ------------------------------
    def test_get_schema_integration(self):
        """
        Integration test for retrieving the schema of a graph.

        Assumes the TigerGraph instance is running and accessible with default settings.
        """

        result = self.api.get_schema(self.graph_name)

        # Assertions for structured response
        assert isinstance(result, dict), "Response should be a dictionary."

        # JSON response (schema)
        assert "GraphName" in result, "Schema should contain 'GraphName'."
        assert result["GraphName"] == self.graph_name, (
            f"GraphName should be '{self.graph_name}'."
        )
        assert "VertexTypes" in result, "Schema should contain 'VertexTypes'."
        assert "EdgeTypes" in result, "Schema should contain 'EdgeTypes'."

    def test_get_schema_graph_not_found(self):
        """
        Test behavior when retrieving a schema for a non-existent graph.
        """
        graph_name = "NonExistentGraph"

        with pytest.raises(
            TigerGraphAPIError,
            match="Graph 'NonExistentGraph' does not exist.",
        ):
            self.api.get_schema(graph_name)

    # ------------------------------ Data Source ------------------------------
    def test_data_source_CRUD(self):
        data_source_name = "data_source_test"
        data_source_type = "s3"

        # Create initial data source
        result = self.api.create_data_source(
            name=data_source_name,
            data_source_type=data_source_type,
        )
        assert isinstance(result, str), f"Expected str, got {type(result)}"
        assert f"Data source {data_source_name} is created" in result, (
            f"Unexpected response: {result}"
        )

        try:
            # Get data source
            result = self.api.get_data_source(data_source_name)
            assert isinstance(result, dict), f"Expected dict, got {type(result)}"
            assert result.get("name") == data_source_name, (
                f"Expected name '{data_source_name}', got {result.get('name')}"
            )
            assert result.get("type") == data_source_type.upper(), (
                f"Expected type '{data_source_type}', got {result.get('type')}"
            )

            # Get all data sources
            all_sources = self.api.get_all_data_sources()
            assert isinstance(all_sources, list), (
                f"Expected list, got {type(all_sources)}"
            )
            assert any(ds["name"] == data_source_name for ds in all_sources), (
                "Created data source not found in list"
            )

            # Update the data source
            result = self.api.update_data_source(
                name=data_source_name,
                data_source_type=data_source_type,
                access_key="aaaaaaaaaaaaaaaaaaaa",
                secret_key="",
            )
            assert isinstance(result, str)
            assert (
                f"Data source {data_source_name} is created" in result
                or "updated" in result.lower()
            )

        finally:
            # Drop data source
            drop_result = self.api.drop_all_data_sources()
            assert isinstance(drop_result, str), (
                f"Expected str, got {type(drop_result)}"
            )
            assert "All data sources is dropped successfully." in drop_result, (
                f"Unexpected drop response: {drop_result}"
            )

    @pytest.mark.skip(
        reason="""
    Skipped by default. To enable this test, manually configure the data source by setting 
    values for data_source_type, access_key, secret_key, extra_config, and sample_path 
    (the path to the file to sample).
    """
    )
    def test_preview_sample_data(self):
        data_source_name = "data_source_1"
        data_source_type = "s3"
        access_key = ""
        secret_key = ""
        extra_config = {
            "file.reader.settings.fs.s3a.aws.credentials.provider": "org.apache.hadoop.fs.s3a.AnonymousAWSCredentialsProvider"
        }
        sample_path = "s3a://<YOUR_FILE_PATH>"

        # Create data source
        result = self.api.create_data_source(
            name=data_source_name,
            data_source_type=data_source_type,
            access_key=access_key,
            secret_key=secret_key,
            extra_config=extra_config,
        )
        assert isinstance(result, str), f"Expected str, got {type(result)}"
        assert f"Data source {data_source_name} is created" in result, (
            f"Unexpected response: {result}"
        )

        try:
            # Preview sample data
            preview_result = self.api.preview_sample_data(
                path=sample_path,
                data_source_type=data_source_type,
                data_source=data_source_name,
                data_format="csv",
                size=5,
                has_header=True,
                separator=",",
                eol="\\n",
                quote='"',
            )
            assert isinstance(preview_result, dict), (
                f"Expected dict, got {type(preview_result)}"
            )
            assert "data" in preview_result, "Key 'data' not found in preview result"
            assert isinstance(preview_result["data"], list), (
                f"Expected 'data' to be list, got {type(preview_result['data'])}"
            )
            assert len(preview_result["data"]) <= 5, (
                f"Preview data has more rows than expected: {len(preview_result['data'])}"
            )

        finally:
            # Drop data source
            drop_result = self.api.drop_data_source(name=data_source_name)
            assert isinstance(drop_result, str), (
                f"Expected str, got {type(drop_result)}"
            )
            assert f"Data source {data_source_name} is dropped" in drop_result, (
                f"Unexpected drop response: {drop_result}"
            )

    # ------------------------------ Query ------------------------------
    def test_create_install_and_drop_query(self):
        """
        Integration test for creating query and dropping query successfully.
        """
        gsql_query = """
CREATE QUERY q1(VERTEX input) for Graph ERGraph {
  Nodes = {input};
  PRINT Nodes;
}
""".strip()
        result = self.api.create_query(self.graph_name, gsql_query)

        assert isinstance(result, str), "Response should be a str."
        assert "Successfully created queries" in result

        result = self.api.install_query(self.graph_name, "q1")
        assert "Query installed successfully" in result

        result = self.api.drop_query(self.graph_name, "q1")

        assert isinstance(result, dict), "Response should be a dict."
        assert "failedToDrop" in result
        assert result["failedToDrop"] == []
        assert "dropped" in result
        assert result["dropped"] == ["q1"]

    def test_create_query_syntax_error(self):
        """
        Integration test for creating query with syntax errors.
        """
        gsql_query = """
CREATE QUERY q2(VERTEX input) for Graph ERGraph {
  Nodes = {input}
  PRINT Nodes;
}
"""

        with pytest.raises(
            TigerGraphAPIError,
            match="Saved as draft query with type/semantic error",
        ):
            self.api.create_query(self.graph_name, gsql_query)

    def test_run_interpreted_query_success(self):
        """
        Integration test for running an interpreted query successfully.
        """
        gsql_query = """
INTERPRET QUERY(VERTEX<Entity> input) for Graph ERGraph {
  Nodes = {input};
  PRINT Nodes;
}
"""
        params = {"input": "Entity_1"}
        result = self.api.run_interpreted_query(gsql_query, params)

        assert isinstance(result, list), "Response should be a list."

    def test_run_interpreted_query_syntax_error(self):
        """
        Test behavior when running an interpreted query with syntax errors.
        """
        gsql_query = """
INTERPRET QUERY(VERTEX<Entity> input) for Graph ERGraph {
  Nodes = {input}
  PRINT Nodes;
}
"""
        with pytest.raises(
            TigerGraphAPIError,
            match="line 5:2 no viable alternative at input ",
        ):
            self.api.run_interpreted_query(gsql_query)
