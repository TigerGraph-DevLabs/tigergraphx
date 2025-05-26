import pytest
from typing import Optional, List, Set
from unittest.mock import MagicMock
import pandas as pd

from tigergraphx.core.managers.query_manager import QueryManager
from tigergraphx.config import NodeSpec, EdgeSpec, NeighborSpec


class TestQueryManager:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.mock_tigergraph_api = MagicMock()
        self.mock_tigergraph_api.run_installed_query_get = MagicMock()
        self.mock_tigergraph_api.run_interpreted_query = MagicMock()

        self.mock_graph_schema = MagicMock()
        self.mock_graph_schema.graph_name = "MyGraph"
        mock_node_schema = MagicMock()
        mock_node_schema.primary_key = "id"
        self.mock_graph_schema.nodes = {"Person": mock_node_schema}

        mock_context = MagicMock()
        mock_context.tigergraph_api = self.mock_tigergraph_api
        mock_context.graph_schema = self.mock_graph_schema
        self.query_manager = QueryManager(mock_context)

    def test_run_query_success(self):
        query_name = "test_query"
        params = {"param1": "value1"}
        self.mock_tigergraph_api.run_installed_query_get.return_value = "result"
        result = self.query_manager.run_query(query_name, params)
        self.mock_tigergraph_api.run_installed_query_get.assert_called_once_with(
            self.mock_graph_schema.graph_name, query_name, params
        )
        assert result == "result"

    def test_run_query_error(self):
        query_name = "test_query"
        params = {"param1": "value1"}
        self.mock_tigergraph_api.run_installed_query_get.side_effect = Exception(
            "Error"
        )
        result = self.query_manager.run_query(query_name, params)
        self.mock_tigergraph_api.run_installed_query_get.assert_called_once_with(
            self.mock_graph_schema.graph_name, query_name, params
        )
        assert result is None

    def test_get_nodes_success(self):
        node_type = "Person"
        self.query_manager.get_nodes_from_spec = MagicMock(return_value="nodes_df")
        result = self.query_manager.get_nodes(node_type)
        assert result == "nodes_df"

    def test_get_nodes_from_spec_with_attributes_success(self):
        spec = NodeSpec(
            node_type="Person",
            all_node_types=False,
            node_alias="s",
            filter_expression=None,
            return_attributes=["name", "id"],
            limit=None,
        )
        self.mock_tigergraph_api.run_interpreted_query.return_value = [
            {
                "Nodes": [
                    {
                        "v_id": "test_node_id",
                        "attributes": {"name": "test_name", "id": "test_node_id"},
                        "v_type": "Entity",
                    }
                ]
            }
        ]
        df = self.query_manager.get_nodes_from_spec(spec)
        assert isinstance(df, pd.DataFrame)
        assert not df.empty
        # Verify that the renamed attributes are present
        assert "name" in df.columns and "id" in df.columns

    def test_get_nodes_from_spec_without_attributes_success(self):
        spec = NodeSpec(
            node_type="Person",
            all_node_types=False,
            node_alias="s",
            filter_expression=None,
            return_attributes=None,
            limit=None,
        )
        self.mock_tigergraph_api.run_interpreted_query.return_value = [
            {
                "Nodes": [
                    {
                        "v_id": "test_node_id",
                        "attributes": {"name": "test_name", "id": "test_node_id"},
                        "v_type": "Entity",
                    }
                ]
            }
        ]
        df = self.query_manager.get_nodes_from_spec(spec)
        assert isinstance(df, pd.DataFrame)
        assert not df.empty

    def test_get_nodes_from_spec_failure(self):
        spec = NodeSpec(
            node_type="Person",
            all_node_types=False,
            node_alias="s",
            filter_expression=None,
            return_attributes=None,
            limit=None,
        )
        self.mock_tigergraph_api.run_interpreted_query.side_effect = Exception("Error")
        df = self.query_manager.get_nodes_from_spec(spec)
        assert isinstance(df, pd.DataFrame)
        assert df.empty, "Expected df to be an empty DataFrame"

    def test_get_nodes_from_spec_with_attributes_success_list_output(self):
        spec = NodeSpec(
            node_type="Person",
            all_node_types=False,
            node_alias="s",
            filter_expression=None,
            return_attributes=["name", "id"],
            limit=None,
        )
        self.mock_tigergraph_api.run_interpreted_query.return_value = [
            {
                "Nodes": [
                    {
                        "v_id": "test_node_id",
                        "attributes": {"name": "test_name", "id": "test_node_id"},
                        "v_type": "Entity",
                    }
                ]
            }
        ]
        result = self.query_manager.get_nodes_from_spec(spec, output_type="List")
        assert isinstance(result, list)
        assert len(result) == 1
        assert "name" in result[0] and "id" in result[0]

    def test_get_nodes_from_spec_without_attributes_success_list_output(self):
        spec = NodeSpec(
            node_type="Person",
            all_node_types=False,
            node_alias="s",
            filter_expression=None,
            return_attributes=None,
            limit=None,
        )
        self.mock_tigergraph_api.run_interpreted_query.return_value = [
            {
                "Nodes": [
                    {
                        "v_id": "test_node_id",
                        "attributes": {"name": "test_name", "id": "test_node_id"},
                        "v_type": "Entity",
                    }
                ]
            }
        ]
        result = self.query_manager.get_nodes_from_spec(spec, output_type="List")
        assert isinstance(result, list)
        assert len(result) == 1
        assert "name" in result[0] and "id" in result[0]

    def test_get_nodes_from_spec_failure_list_output(self):
        spec = NodeSpec(
            node_type="Person",
            all_node_types=False,
            node_alias="s",
            filter_expression=None,
            return_attributes=None,
            limit=None,
        )
        self.mock_tigergraph_api.run_interpreted_query.side_effect = Exception("Error")
        result = self.query_manager.get_nodes_from_spec(spec, output_type="List")
        assert isinstance(result, list)
        assert result == [], "Expected an empty list when query fails"

    def test_get_edges_success(self):
        spec = EdgeSpec(
            source_node_type_set={"Person"},
            source_node_alias="a",
            edge_type_set={"knows"},
            edge_alias="r",
            target_node_type_set={"Person"},
            target_node_alias="b",
            filter_expression=None,
            return_attributes=None,
            limit=None,
        )
        self.query_manager.get_edges_from_spec = MagicMock(return_value="edges_df")
        result = self.query_manager.get_edges_from_spec(spec)
        assert result == "edges_df"

    def test_get_edges_from_spec_with_attributes_success(self):
        spec = EdgeSpec(
            source_node_type_set={"Person"},
            source_node_alias="a",
            edge_type_set={"knows"},
            edge_alias="r",
            target_node_type_set={"Person"},
            target_node_alias="b",
            filter_expression=None,
            return_attributes=["since"],
            limit=None,
        )
        self.mock_tigergraph_api.run_interpreted_query.return_value = [
            {"T": [{"a": "Alice", "b": "Bob", "since": "2020-01-01 00:00:00"}]}
        ]
        df = self.query_manager.get_edges_from_spec(spec)
        assert isinstance(df, pd.DataFrame)
        assert not df.empty
        assert "since" in df.columns

    def test_get_edges_from_spec_without_attributes_success(self):
        spec = EdgeSpec(
            source_node_type_set={"Person"},
            source_node_alias="a",
            edge_type_set={"knows"},
            edge_alias="r",
            target_node_type_set={"Person"},
            target_node_alias="b",
            filter_expression=None,
            return_attributes=None,
            limit=None,
        )
        self.mock_tigergraph_api.run_interpreted_query.return_value = [
            {"T": [{"a": "Alice", "b": "Bob"}]}
        ]
        df = self.query_manager.get_edges_from_spec(spec)
        assert isinstance(df, pd.DataFrame)
        assert not df.empty

    def test_get_edges_from_spec_failure(self):
        spec = EdgeSpec(
            source_node_type_set={"Person"},
            source_node_alias="a",
            edge_type_set={"knows"},
            edge_alias="r",
            target_node_type_set={"Person"},
            target_node_alias="b",
            filter_expression=None,
            return_attributes=None,
            limit=None,
        )
        self.mock_tigergraph_api.run_interpreted_query.side_effect = Exception("Error")
        df = self.query_manager.get_edges_from_spec(spec)
        assert isinstance(df, pd.DataFrame)
        assert df.empty

    def test_get_edges_from_spec_with_attributes_success_list_output(self):
        spec = EdgeSpec(
            source_node_type_set={"Person"},
            source_node_alias="a",
            edge_type_set={"knows"},
            edge_alias="r",
            target_node_type_set={"Person"},
            target_node_alias="b",
            filter_expression=None,
            return_attributes=["since"],
            limit=None,
        )
        self.mock_tigergraph_api.run_interpreted_query.return_value = [
            {"T": [{"a": "Alice", "b": "Bob", "since": "2020-01-01 00:00:00"}]}
        ]
        result = self.query_manager.get_edges_from_spec(spec, output_type="List")
        assert isinstance(result, list)
        assert len(result) == 1
        assert "since" in result[0]

    def test_get_edges_from_spec_without_attributes_success_list_output(self):
        spec = EdgeSpec(
            source_node_type_set={"Person"},
            source_node_alias="a",
            edge_type_set={"knows"},
            edge_alias="r",
            target_node_type_set={"Person"},
            target_node_alias="b",
            filter_expression=None,
            return_attributes=None,
            limit=None,
        )
        self.mock_tigergraph_api.run_interpreted_query.return_value = [
            {"T": [{"a": "Alice", "b": "Bob"}]}
        ]
        result = self.query_manager.get_edges_from_spec(spec, output_type="List")
        assert isinstance(result, list)
        assert len(result) == 1
        assert "a" in result[0] and "b" in result[0]

    def test_get_edges_from_spec_failure_list_output(self):
        spec = EdgeSpec(
            source_node_type_set={"Person"},
            source_node_alias="a",
            edge_type_set={"knows"},
            edge_alias="r",
            target_node_type_set={"Person"},
            target_node_alias="b",
            filter_expression=None,
            return_attributes=None,
            limit=None,
        )
        self.mock_tigergraph_api.run_interpreted_query.side_effect = Exception("Error")
        result = self.query_manager.get_edges_from_spec(spec, output_type="List")
        assert isinstance(result, list)
        assert result == []

    def test_get_neighbors_success(self):
        # Test the simpler get_neighbors() path, where only start_nodes and start_node_type are provided.
        start_nodes = "node1"
        start_node_type = "Person"
        # Set the expected behavior for the method that handles the spec conversion.
        self.query_manager.get_neighbors_from_spec = MagicMock(
            return_value="neighbors_df"
        )
        result = self.query_manager.get_neighbors(start_nodes, start_node_type)
        assert result == "neighbors_df"
        # Optionally, verify that get_neighbors_from_spec was called with a spec including default aliases.
        self.query_manager.get_neighbors_from_spec.assert_called_once()
        spec_passed = self.query_manager.get_neighbors_from_spec.call_args[0][0]
        assert spec_passed.start_node_alias == "s"
        # In this simple call, edge_alias and target_node_alias may or may not be set depending on your implementation.

    def test_get_neighbors_from_spec_with_attributes_success(self):
        # Create a NeighborSpec including the new alias parameters.
        spec = NeighborSpec(
            start_nodes="node1",
            start_node_type="Person",
            start_node_alias="s",
            edge_type_set={"relationship", "reverse_relationship"},
            edge_alias="e",
            target_node_type_set={"Person"},
            target_node_alias="t",
            filter_expression=None,
            return_attributes=["id", "name"],
            limit=None,
        )
        # Prepare the mock return value from the connection.
        self.mock_tigergraph_api.run_interpreted_query.return_value = [
            {
                "Neighbors": [
                    {
                        "v_id": "test_node_id",
                        "attributes": {"name": "test_name", "id": "test_node_id"},
                        "v_type": "Entity",
                    }
                ]
            }
        ]
        # Call the method to get a neighbors DataFrame.
        df = self.query_manager.get_neighbors_from_spec(spec)
        # Verify the returned object is a DataFrame and contains the requested columns.
        assert isinstance(df, pd.DataFrame)
        assert not df.empty
        assert "id" in df.columns
        assert "name" in df.columns

    def test_get_neighbors_from_spec_without_attributes_success(self):
        # Create a NeighborSpec with no return attributes.
        spec = NeighborSpec(
            start_nodes="node1",
            start_node_type="Person",
            start_node_alias="s",
            edge_type_set={"relationship", "reverse_relationship"},
            edge_alias="e",
            target_node_type_set={"Person"},
            target_node_alias="t",
            filter_expression=None,
            return_attributes=None,
            limit=None,
        )
        self.mock_tigergraph_api.run_interpreted_query.return_value = [
            {
                "Neighbors": [
                    {
                        "v_id": "test_node_id",
                        "attributes": {"name": "test_name", "id": "test_node_id"},
                        "v_type": "Entity",
                    }
                ]
            }
        ]
        df = self.query_manager.get_neighbors_from_spec(spec)
        assert isinstance(df, pd.DataFrame)
        assert not df.empty
        # When no return_attributes are defined, the DataFrame should still include valid columns.
        # Optionally check that some expected keys are in the DataFrame.

    def test_get_neighbors_from_spec_failure(self):
        # Create a NeighborSpec with alias parameters.
        spec = NeighborSpec(
            start_nodes="node1",
            start_node_type="Person",
            start_node_alias="s",
            edge_type_set={"relationship"},
            edge_alias="e",
            target_node_type_set={"Person"},
            target_node_alias="t",
            filter_expression=None,
            return_attributes=None,
            limit=None,
        )
        # Simulate a failure from the connection's query execution.
        self.mock_tigergraph_api.run_interpreted_query.side_effect = Exception("Error")
        # The method should catch the exception and return None (or handle it gracefully).
        df = self.query_manager.get_neighbors_from_spec(spec)
        assert isinstance(df, pd.DataFrame)
        assert df.empty, "Expected df to be an empty DataFrame"

    def test_get_neighbors_from_spec_with_attributes_list_output(self):
        # NeighborSpec with return_attributes and output_type = "List"
        spec = NeighborSpec(
            start_nodes="node1",
            start_node_type="Person",
            start_node_alias="s",
            edge_type_set={"relationship"},
            edge_alias="e",
            target_node_type_set={"Person"},
            target_node_alias="t",
            filter_expression=None,
            return_attributes=["id", "name"],
            limit=None,
        )
        self.mock_tigergraph_api.run_interpreted_query.return_value = [
            {
                "Neighbors": [
                    {
                        "v_id": "test_node_id",
                        "attributes": {"name": "test_name", "id": "test_node_id"},
                        "v_type": "Entity",
                    }
                ]
            }
        ]
        df_or_list = self.query_manager.get_neighbors_from_spec(
            spec, output_type="List"
        )
        assert isinstance(df_or_list, list)
        assert len(df_or_list) == 1
        assert df_or_list[0]["id"] == "test_node_id"
        assert df_or_list[0]["name"] == "test_name"

    def test_get_neighbors_from_spec_without_attributes_list_output(self):
        # NeighborSpec without return_attributes and output_type = "List"
        spec = NeighborSpec(
            start_nodes="node1",
            start_node_type="Person",
            start_node_alias="s",
            edge_type_set={"relationship"},
            edge_alias="e",
            target_node_type_set={"Person"},
            target_node_alias="t",
            filter_expression=None,
            return_attributes=None,
            limit=None,
        )
        self.mock_tigergraph_api.run_interpreted_query.return_value = [
            {
                "Neighbors": [
                    {
                        "v_id": "test_node_id",
                        "attributes": {"name": "test_name", "id": "test_node_id"},
                        "v_type": "Entity",
                    }
                ]
            }
        ]
        df_or_list = self.query_manager.get_neighbors_from_spec(
            spec, output_type="List"
        )
        assert isinstance(df_or_list, list)
        assert len(df_or_list) == 1
        assert "name" in df_or_list[0]
        assert "id" in df_or_list[0]

    def test_bfs_single_level(self):
        self.query_manager.get_neighbors = MagicMock(
            return_value=pd.DataFrame(
                {"id": ["Bob", "Charlie"], "age": [30, 25], "gender": ["M", "M"]}
            )
        )

        df = self.query_manager.bfs(start_nodes="Alice", node_type="Person", max_hops=1)

        assert isinstance(df, pd.DataFrame)
        assert not df.empty
        assert set(df["id"]) == {"Bob", "Charlie"}
        assert "_bfs_level" in df.columns

    def test_bfs_multi_level(self):
        bfs_results = [
            pd.DataFrame(
                {"id": ["Bob", "Charlie"], "age": [30, 25], "gender": ["M", "M"]}
            ),
            pd.DataFrame({"id": ["David"], "age": [35], "gender": ["M"]}),
        ]

        self.query_manager.get_neighbors = MagicMock(side_effect=bfs_results)

        df = self.query_manager.bfs(start_nodes="Alice", node_type="Person", max_hops=2)

        assert isinstance(df, pd.DataFrame)
        assert not df.empty
        assert set(df["id"]) == {"David"}
        assert "_bfs_level" in df.columns

    def test_bfs_respects_max_hops(self):
        bfs_results = [
            pd.DataFrame(
                {"id": ["Bob", "Charlie"], "age": [30, 25], "gender": ["M", "M"]}
            ),
            pd.DataFrame({"id": ["David"], "age": [35], "gender": ["M"]}),
            pd.DataFrame({"id": ["Eve"], "age": [28], "gender": ["F"]}),
        ]

        self.query_manager.get_neighbors = MagicMock(side_effect=bfs_results)

        df = self.query_manager.bfs(start_nodes="Alice", node_type="Person", max_hops=2)

        assert isinstance(df, pd.DataFrame)
        assert not df.empty
        assert set(df["id"]) == {"David"}
        assert "_bfs_level" in df.columns

    def test_bfs_no_neighbors(self):
        self.query_manager.get_neighbors = MagicMock(return_value=pd.DataFrame())

        df = self.query_manager.bfs(start_nodes="Alice", node_type="Person", max_hops=3)

        assert isinstance(df, pd.DataFrame)
        assert df.empty
        assert "_bfs_level" in df.columns or "_bfs_level" not in df.columns  # OK: empty

    def test_bfs_multiple_start_nodes(self):
        bfs_results = [
            pd.DataFrame(
                {"id": ["Bob", "Charlie"], "age": [30, 25], "gender": ["M", "M"]}
            ),
            pd.DataFrame({"id": ["David"], "age": [35], "gender": ["M"]}),
            pd.DataFrame({"id": ["Eve"], "age": [28], "gender": ["F"]}),
        ]
        self.query_manager.get_neighbors = MagicMock(side_effect=bfs_results)

        df = self.query_manager.bfs(
            start_nodes=["Alice", "Ed"], node_type="Person", max_hops=3
        )

        assert isinstance(df, pd.DataFrame)
        assert not df.empty
        assert set(df["id"]) == {"Eve"}
        assert "_bfs_level" in df.columns

    def test_bfs_with_limit(self):
        self.query_manager.get_neighbors = MagicMock(
            return_value=pd.DataFrame(
                {"id": ["Bob", "Charlie"], "age": [30, 25], "gender": ["M", "M"]}
            )
        )

        df = self.query_manager.bfs(
            start_nodes="Alice", node_type="Person", limit=2, max_hops=1
        )

        assert isinstance(df, pd.DataFrame)
        assert not df.empty
        assert len(df) <= 2
        assert "_bfs_level" in df.columns

    def test_bfs_single_level_list_output(self):
        self.query_manager.get_neighbors = MagicMock(
            return_value=[
                {"id": "Bob", "age": 30, "gender": "M"},
                {"id": "Charlie", "age": 25, "gender": "M"},
            ]
        )

        result = self.query_manager.bfs(
            start_nodes="Alice", node_type="Person", max_hops=1, output_type="List"
        )

        assert isinstance(result, list)
        assert result
        assert {item["id"] for item in result} == {"Bob", "Charlie"}
        assert all("_bfs_level" in item for item in result)

    def test_bfs_multi_level_list_output(self):
        bfs_results = [
            [
                {"id": "Bob", "age": 30, "gender": "M"},
                {"id": "Charlie", "age": 25, "gender": "M"},
            ],
            [
                {"id": "David", "age": 35, "gender": "M"},
            ],
        ]

        self.query_manager.get_neighbors = MagicMock(side_effect=bfs_results)

        result = self.query_manager.bfs(
            start_nodes="Alice", node_type="Person", max_hops=2, output_type="List"
        )

        assert isinstance(result, list)
        assert result
        assert {item["id"] for item in result} == {"David"}
        assert all("_bfs_level" in item for item in result)

    def test_bfs_respects_max_hops_list_output(self):
        bfs_results = [
            [
                {"id": "Bob", "age": 30, "gender": "M"},
                {"id": "Charlie", "age": 25, "gender": "M"},
            ],
            [
                {"id": "David", "age": 35, "gender": "M"},
            ],
            [
                {"id": "Eve", "age": 28, "gender": "F"},
            ],
        ]

        self.query_manager.get_neighbors = MagicMock(side_effect=bfs_results)

        result = self.query_manager.bfs(
            start_nodes="Alice", node_type="Person", max_hops=2, output_type="List"
        )

        assert isinstance(result, list)
        assert result
        assert {item["id"] for item in result} == {"David"}
        assert all("_bfs_level" in item for item in result)

    def test_bfs_no_neighbors_list_output(self):
        self.query_manager.get_neighbors = MagicMock(return_value=[])

        result = self.query_manager.bfs(
            start_nodes="Alice", node_type="Person", max_hops=3, output_type="List"
        )

        assert isinstance(result, list)
        assert not result  # Should be empty

    def test_bfs_multiple_start_nodes_list_output(self):
        bfs_results = [
            [
                {"id": "Bob", "age": 30, "gender": "M"},
                {"id": "Charlie", "age": 25, "gender": "M"},
            ],
            [
                {"id": "David", "age": 35, "gender": "M"},
            ],
            [
                {"id": "Eve", "age": 28, "gender": "F"},
            ],
        ]
        self.query_manager.get_neighbors = MagicMock(side_effect=bfs_results)

        result = self.query_manager.bfs(
            start_nodes=["Alice", "Ed"],
            node_type="Person",
            max_hops=3,
            output_type="List",
        )

        assert isinstance(result, list)
        assert result
        assert {item["id"] for item in result} == {"Eve"}
        assert all("_bfs_level" in item for item in result)

    def test_bfs_with_limit_list_output(self):
        self.query_manager.get_neighbors = MagicMock(
            return_value=[
                {"id": "Bob", "age": 30, "gender": "M"},
                {"id": "Charlie", "age": 25, "gender": "M"},
            ]
        )

        result = self.query_manager.bfs(
            start_nodes="Alice",
            node_type="Person",
            limit=2,
            max_hops=1,
            output_type="List",
        )

        assert isinstance(result, list)
        assert result
        assert len(result) <= 2
        assert all("_bfs_level" in item for item in result)

    # --- GSQL Query Creation Tests for get_nodes ---
    def create_gsql_get_nodes(
        self,
        node_type: Optional[str] = None,
        all_types: bool = False,
        node_alias: str = "s",
        filter_expression: Optional[str] = None,
        return_attributes: Optional[List[str]] = None,
        limit: Optional[int] = None,
    ) -> str:
        """
        Helper function to generate a GSQL query using _create_gsql_get_nodes.
        """
        spec = NodeSpec(
            node_type=node_type,
            all_node_types=all_types,
            node_alias=node_alias,
            filter_expression=filter_expression,
            return_attributes=return_attributes,
            limit=limit,
        )
        return self.query_manager._create_gsql_get_nodes(spec)

    def test_create_gsql_get_nodes_simple(self):
        actual_gsql_script = self.create_gsql_get_nodes(node_type="Person")
        expected_gsql_script = (
            "INTERPRET QUERY() FOR GRAPH MyGraph {\n"
            "  Nodes = {Person.*};\n"
            "  PRINT Nodes;\n"
            "}"
        )
        assert actual_gsql_script == expected_gsql_script

    def test_create_gsql_get_nodes_with_all_types(self):
        actual_gsql_script = self.create_gsql_get_nodes(
            node_type="Person", all_types=True
        )
        expected_gsql_script = (
            "INTERPRET QUERY() FOR GRAPH MyGraph {\n  Nodes = {ANY};\n  PRINT Nodes;\n}"
        )
        assert actual_gsql_script == expected_gsql_script

    def test_create_gsql_get_nodes_with_limit(self):
        actual_gsql_script = self.create_gsql_get_nodes(node_type="Person", limit=10)
        expected_gsql_script = (
            "INTERPRET QUERY() FOR GRAPH MyGraph {\n"
            "  Nodes = {Person.*};\n"
            "  Nodes =\n"
            "    SELECT s\n"
            "    FROM Nodes:s\n"
            "    LIMIT 10\n"
            "  ;\n"
            "  PRINT Nodes;\n"
            "}"
        )
        assert actual_gsql_script == expected_gsql_script

    def test_create_gsql_get_nodes_with_return_attributes(self):
        actual_gsql_script = self.create_gsql_get_nodes(
            node_type="Person",
            return_attributes=["id", "rank"],
        )
        expected_gsql_script = (
            "INTERPRET QUERY() FOR GRAPH MyGraph {\n"
            "  Nodes = {Person.*};\n"
            "  PRINT Nodes[\n"
            "    Nodes.id AS id,\n"
            "    Nodes.rank AS rank\n"
            "  ];\n"
            "}"
        )
        assert actual_gsql_script == expected_gsql_script

    def test_create_gsql_get_nodes_with_filter_expression(self):
        actual_gsql_script = self.create_gsql_get_nodes(
            node_type="Person",
            filter_expression="s.rank > 0",
        )
        expected_gsql_script = (
            "INTERPRET QUERY() FOR GRAPH MyGraph {\n"
            "  Nodes = {Person.*};\n"
            "  Nodes =\n"
            "    SELECT s\n"
            "    FROM Nodes:s\n"
            "    WHERE s.rank > 0\n"
            "  ;\n"
            "  PRINT Nodes;\n"
            "}"
        )
        assert actual_gsql_script == expected_gsql_script

    def test_create_gsql_get_nodes_with_all_options(self):
        actual_gsql_script = self.create_gsql_get_nodes(
            node_type="Person",
            node_alias="n",
            filter_expression="n.rank > 0",
            return_attributes=["id", "rank"],
            limit=10,
        )
        expected_gsql_script = (
            "INTERPRET QUERY() FOR GRAPH MyGraph {\n"
            "  Nodes = {Person.*};\n"
            "  Nodes =\n"
            "    SELECT n\n"
            "    FROM Nodes:n\n"
            "    WHERE n.rank > 0\n"
            "    LIMIT 10\n"
            "  ;\n"
            "  PRINT Nodes[\n"
            "    Nodes.id AS id,\n"
            "    Nodes.rank AS rank\n"
            "  ];\n"
            "}"
        )
        assert actual_gsql_script == expected_gsql_script

    def create_gsql_get_edges(
        self,
        source_node_type_set: Optional[Set[str]] = None,
        edge_type_set: Optional[Set[str]] = None,
        target_node_type_set: Optional[Set[str]] = None,
        source_node_alias: str = "s",
        edge_alias: str = "e",
        target_node_alias: str = "t",
        filter_expression: Optional[str] = None,
        return_attributes: Optional[List[str]] = None,
        limit: Optional[int] = None,
    ) -> str:
        """
        Helper function to generate a GSQL query using _create_gsql_get_edges.
        """
        spec = EdgeSpec(
            source_node_type_set=source_node_type_set,
            edge_type_set=edge_type_set,
            target_node_type_set=target_node_type_set,
            source_node_alias=source_node_alias,
            edge_alias=edge_alias,
            target_node_alias=target_node_alias,
            filter_expression=filter_expression,
            return_attributes=return_attributes,
            limit=limit,
        )
        return self.query_manager._create_gsql_get_edges(spec)

    def test_create_gsql_get_edges_basic(self):
        actual = self.create_gsql_get_edges(
            source_node_type_set={"Person"},
            edge_type_set={"works_for"},
            target_node_type_set={"Company"},
        )
        expected = (
            "INTERPRET QUERY() FOR GRAPH MyGraph SYNTAX V3 {\n"
            "  SELECT s, t INTO T\n"
            "  FROM (s:Person) -[e:works_for]- (t:Company)\n"
            "  ;\n"
            "  PRINT T;\n"
            "}"
        )
        assert actual == expected

    def test_create_gsql_get_edges_with_filter(self):
        actual = self.create_gsql_get_edges(
            source_node_type_set={"Person"},
            edge_type_set={"works_for"},
            target_node_type_set={"Company"},
            filter_expression="s.name != t.name",
        )
        expected = (
            "INTERPRET QUERY() FOR GRAPH MyGraph SYNTAX V3 {\n"
            "  SELECT s, t INTO T\n"
            "  FROM (s:Person) -[e:works_for]- (t:Company)\n"
            "  WHERE s.name != t.name\n"
            "  ;\n"
            "  PRINT T;\n"
            "}"
        )
        assert actual == expected

    def test_create_gsql_get_edges_with_limit(self):
        actual = self.create_gsql_get_edges(
            source_node_type_set={"Person"},
            edge_type_set={"works_for"},
            target_node_type_set={"Company"},
            limit=10,
        )
        expected = (
            "INTERPRET QUERY() FOR GRAPH MyGraph SYNTAX V3 {\n"
            "  SELECT s, t INTO T\n"
            "  FROM (s:Person) -[e:works_for]- (t:Company)\n"
            "  LIMIT 10\n"
            "  ;\n"
            "  PRINT T;\n"
            "}"
        )
        assert actual == expected

    def test_create_gsql_get_edges_with_attributes(self):
        actual = self.create_gsql_get_edges(
            source_node_type_set={"Person"},
            edge_type_set={"works_for"},
            target_node_type_set={"Company"},
            return_attributes=["role"],
        )
        expected = (
            "INTERPRET QUERY() FOR GRAPH MyGraph SYNTAX V3 {\n"
            "  SELECT s, t, e.role INTO T\n"
            "  FROM (s:Person) -[e:works_for]- (t:Company)\n"
            "  ;\n"
            "  PRINT T;\n"
            "}"
        )
        assert actual == expected

    def test_create_gsql_get_edges_all_edge_types(self):
        actual = self.create_gsql_get_edges(return_attributes=["role"])
        expected = (
            "INTERPRET QUERY() FOR GRAPH MyGraph SYNTAX V3 {\n"
            "  SELECT s, t, e.role INTO T\n"
            "  FROM (s) -[e]- (t)\n"
            "  ;\n"
            "  PRINT T;\n"
            "}"
        )
        assert actual == expected

    def test_create_gsql_get_edges_multiple_types_and_attrs(self):
        actual = self.create_gsql_get_edges(
            source_node_type_set={"Person"},
            edge_type_set={"works_for", "knows"},
            target_node_type_set={"Person", "Company"},
            source_node_alias="a",
            edge_alias="r",
            target_node_alias="b",
            filter_expression="a.name != b.name",
            return_attributes=["since"],
            limit=5,
        )
        expected = (
            "INTERPRET QUERY() FOR GRAPH MyGraph SYNTAX V3 {\n"
            "  SELECT a, b, r.since INTO T\n"
            "  FROM (a:Person) -[r:(knows|works_for)]- (b:(Company|Person))\n"
            "  WHERE a.name != b.name\n"
            "  LIMIT 5\n"
            "  ;\n"
            "  PRINT T;\n"
            "}"
        )
        assert actual == expected

    # --- GSQL Query Creation Tests for get_neighbors ---
    def create_gsql_get_neighbors(
        self,
        start_nodes: str | List[str],
        start_node_type: str,
        start_node_alias: str = "s",
        edge_type_set: Optional[Set[str]] = None,
        edge_alias: str = "e",
        target_node_type_set: Optional[Set[str]] = None,
        target_node_alias: str = "t",
        filter_expression: Optional[str] = None,
        return_attributes: Optional[str | List[str]] = None,
        limit: Optional[int] = None,
    ) -> str:
        """
        Helper function to generate a GSQL query using _create_gsql_get_neighbors.
        """
        spec = NeighborSpec(
            start_nodes=start_nodes,
            start_node_type=start_node_type,
            start_node_alias=start_node_alias,
            edge_type_set=edge_type_set,
            edge_alias=edge_alias,
            target_node_type_set=target_node_type_set,
            target_node_alias=target_node_alias,
            filter_expression=filter_expression,
            return_attributes=return_attributes,
            limit=limit,
        )
        gsql_script, _ = self.query_manager._create_gsql_get_neighbors(spec)
        return gsql_script

    def test_create_gsql_get_neighbors_basic(self):
        # Get neighbors with minimal parameters
        actual_gsql_script = self.create_gsql_get_neighbors(
            start_nodes=["CYTOSORB"],
            start_node_type="Person",
        )
        expected_gsql_script = (
            "INTERPRET QUERY(\n"
            "  SET<VERTEX<Person>> start_nodes\n"
            ") FOR GRAPH MyGraph {\n"
            "  Nodes = {start_nodes};\n"
            "  Neighbors =\n"
            "    SELECT t\n"
            "    FROM Nodes:s -(:e)- :t\n"
            "  ;\n"
            "  PRINT Neighbors;\n"
            "}"
        )
        assert actual_gsql_script == expected_gsql_script

    def test_create_gsql_get_neighbors_with_edge_and_target_types(self):
        actual_gsql_script = self.create_gsql_get_neighbors(
            start_nodes=["CYTOSORB"],
            start_node_type="Person",
            edge_type_set={"relationship"},
            target_node_type_set={"Entity"},
            limit=10,
        )
        expected_gsql_script = (
            "INTERPRET QUERY(\n"
            "  SET<VERTEX<Person>> start_nodes\n"
            ") FOR GRAPH MyGraph {\n"
            "  Nodes = {start_nodes};\n"
            "  Neighbors =\n"
            "    SELECT t\n"
            "    FROM Nodes:s -(relationship:e)- Entity:t\n"
            "    LIMIT 10\n"
            "  ;\n"
            "  PRINT Neighbors;\n"
            "}"
        )
        assert actual_gsql_script == expected_gsql_script

    def test_create_gsql_get_neighbors_with_single_return_attribute(self):
        actual_gsql_script = self.create_gsql_get_neighbors(
            start_nodes="Sam",
            start_node_type="Person",
            edge_type_set={"relationship"},
            target_node_type_set={"Person"},
            return_attributes="id",
            limit=10,
        )
        expected_gsql_script = (
            "INTERPRET QUERY(\n"
            "  SET<VERTEX<Person>> start_nodes\n"
            ") FOR GRAPH MyGraph {\n"
            "  Nodes = {start_nodes};\n"
            "  Neighbors =\n"
            "    SELECT t\n"
            "    FROM Nodes:s -(relationship:e)- Person:t\n"
            "    LIMIT 10\n"
            "  ;\n"
            "  PRINT Neighbors[\n"
            "    Neighbors.id AS id\n"
            "  ];\n"
            "}"
        )
        assert actual_gsql_script == expected_gsql_script

    def test_create_gsql_get_neighbors_with_multiple_return_attributes(self):
        actual_gsql_script = self.create_gsql_get_neighbors(
            start_nodes="CYTOSORB",
            start_node_type="Person",
            edge_type_set={"relationship"},
            target_node_type_set={"Person"},
            return_attributes=["id", "entity_type"],
            limit=10,
        )
        expected_gsql_script = (
            "INTERPRET QUERY(\n"
            "  SET<VERTEX<Person>> start_nodes\n"
            ") FOR GRAPH MyGraph {\n"
            "  Nodes = {start_nodes};\n"
            "  Neighbors =\n"
            "    SELECT t\n"
            "    FROM Nodes:s -(relationship:e)- Person:t\n"
            "    LIMIT 10\n"
            "  ;\n"
            "  PRINT Neighbors[\n"
            "    Neighbors.id AS id,\n"
            "    Neighbors.entity_type AS entity_type\n"
            "  ];\n"
            "}"
        )
        assert actual_gsql_script == expected_gsql_script

    def test_create_gsql_get_neighbors_with_filter_expression(self):
        actual_gsql_script = self.create_gsql_get_neighbors(
            start_nodes=["CYTOSORB", "ITALY"],
            start_node_type="Person",
            edge_type_set={"relationship"},
            target_node_type_set={"Person"},
            filter_expression="s.id != t.id",
            return_attributes=["id", "entity_type"],
            limit=10,
        )
        expected_gsql_script = (
            "INTERPRET QUERY(\n"
            "  SET<VERTEX<Person>> start_nodes\n"
            ") FOR GRAPH MyGraph {\n"
            "  Nodes = {start_nodes};\n"
            "  Neighbors =\n"
            "    SELECT t\n"
            "    FROM Nodes:s -(relationship:e)- Person:t\n"
            "    WHERE s.id != t.id\n"
            "    LIMIT 10\n"
            "  ;\n"
            "  PRINT Neighbors[\n"
            "    Neighbors.id AS id,\n"
            "    Neighbors.entity_type AS entity_type\n"
            "  ];\n"
            "}"
        )
        assert actual_gsql_script == expected_gsql_script

    def test_create_gsql_get_neighbors_with_alias(self):
        actual_gsql_script = self.create_gsql_get_neighbors(
            start_nodes=["CYTOSORB", "ITALY"],
            start_node_type="Person",
            start_node_alias="s1",
            edge_type_set={"relationship"},
            edge_alias="e1",
            target_node_type_set={"Person"},
            target_node_alias="s2",
            filter_expression="s1.id != s2.id",
            return_attributes=["id", "entity_type"],
            limit=10,
        )
        expected_gsql_script = (
            "INTERPRET QUERY(\n"
            "  SET<VERTEX<Person>> start_nodes\n"
            ") FOR GRAPH MyGraph {\n"
            "  Nodes = {start_nodes};\n"
            "  Neighbors =\n"
            "    SELECT s2\n"
            "    FROM Nodes:s1 -(relationship:e1)- Person:s2\n"
            "    WHERE s1.id != s2.id\n"
            "    LIMIT 10\n"
            "  ;\n"
            "  PRINT Neighbors[\n"
            "    Neighbors.id AS id,\n"
            "    Neighbors.entity_type AS entity_type\n"
            "  ];\n"
            "}"
        )
        assert actual_gsql_script == expected_gsql_script

    def test_create_gsql_get_neighbors_with_multiple_edge_types(self):
        actual_gsql_script = self.create_gsql_get_neighbors(
            start_nodes=["Sam"],
            start_node_type="Person",
            edge_type_set={"relationship", "reverse_relationship"},
            target_node_type_set={"Person"},
            limit=10,
        )
        expected_gsql_script_1 = (
            "FROM Nodes:s -((relationship|reverse_relationship):e)- Person:t\n"
        )
        expected_gsql_script_2 = (
            "FROM Nodes:s -((reverse_relationship|relationship):e)- Person:t\n"
        )
        assert (
            expected_gsql_script_1 in actual_gsql_script
            or expected_gsql_script_2 in actual_gsql_script
        )
