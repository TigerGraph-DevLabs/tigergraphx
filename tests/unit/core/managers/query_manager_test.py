import pytest
from typing import Optional, List
from unittest.mock import MagicMock
import pandas as pd

from tigergraphx.core.managers.query_manager import QueryManager
from tigergraphx.config import (
    NodeSpec,
    NeighborSpec,
)


class TestQueryManager:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.mock_connection = MagicMock()
        self.mock_connection.runInstalledQuery = MagicMock()

        mock_context = MagicMock()
        mock_context.connection = self.mock_connection
        self.query_manager = QueryManager(mock_context)

    def test_run_query_success(self):
        query_name = "test_query"
        params = {"param1": "value1"}
        self.mock_connection.runInstalledQuery.return_value = "result"
        result = self.query_manager.run_query(query_name, params)
        self.mock_connection.runInstalledQuery.assert_called_once_with(
            queryName=query_name, params=params
        )
        assert result == "result"

    def test_run_query_error(self):
        query_name = "test_query"
        params = {"param1": "value1"}
        self.mock_connection.runInstalledQuery.side_effect = Exception("Error")
        result = self.query_manager.run_query(query_name, params)
        self.mock_connection.runInstalledQuery.assert_called_once_with(
            queryName=query_name, params=params
        )
        assert result is None

    def test_get_nodes_success(self):
        node_type = "Person"
        self.query_manager.get_nodes_from_spec = MagicMock(return_value="nodes_df")
        result = self.query_manager.get_nodes(node_type)
        assert result == "nodes_df"

    def test_get_nodes_from_spec_with_attributes_success(self, setup):
        spec = NodeSpec(
            node_type="test_type",
            filter_expression=None,
            return_attributes=["name", "id"],
            limit=None,
        )
        self.mock_connection.runInterpretedQuery = MagicMock(
            return_value=[
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
        )
        df = self.query_manager.get_nodes_from_spec(spec)
        assert isinstance(df, pd.DataFrame)
        assert not df.empty

    def test_get_nodes_from_spec_without_attributes_success(self, setup):
        spec = NodeSpec(
            node_type="test_type",
            filter_expression=None,
            return_attributes=None,
            limit=None,
        )
        self.mock_connection.runInterpretedQuery = MagicMock(
            return_value=[
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
        )
        df = self.query_manager.get_nodes_from_spec(spec)
        assert isinstance(df, pd.DataFrame)
        assert not df.empty

    def test_get_nodes_from_spec_failure(self, setup):
        spec = NodeSpec(
            node_type="test_type",
            filter_expression=None,
            return_attributes=None,
            limit=None,
        )
        self.mock_connection.runInterpretedQuery = MagicMock(
            side_effect=Exception("Error")
        )
        df = self.query_manager.get_nodes_from_spec(spec)
        assert df is None

    def test_get_neighbors_success(self):
        start_nodes = "node1"
        start_node_type = "Person"
        self.query_manager.get_neighbors_from_spec = MagicMock(
            return_value="neighbors_df"
        )
        result = self.query_manager.get_neighbors(start_nodes, start_node_type)
        assert result == "neighbors_df"

    def test_get_neighbors_from_spec_with_attributes_success(self, setup):
        spec = NeighborSpec(
            start_nodes="node1",
            start_node_type="type1",
            edge_types=None,
            target_node_types=None,
            filter_expression=None,
            return_attributes=["id", "name"],
            limit=None,
        )
        self.mock_connection.runInterpretedQuery = MagicMock(
            return_value=[
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
        )
        df = self.query_manager.get_neighbors_from_spec(spec)
        assert isinstance(df, pd.DataFrame)
        assert not df.empty

    def test_get_neighbors_from_spec_without_attributes_success(self, setup):
        spec = NeighborSpec(
            start_nodes="node1",
            start_node_type="type1",
            edge_types=None,
            target_node_types=None,
            filter_expression=None,
            return_attributes=None,
            limit=None,
        )
        self.mock_connection.runInterpretedQuery = MagicMock(
            return_value=[
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
        )
        df = self.query_manager.get_neighbors_from_spec(spec)
        assert isinstance(df, pd.DataFrame)
        assert not df.empty

    def test_get_neighbors_from_spec_failure(self, setup):
        spec = NeighborSpec(
            start_nodes="node1",
            start_node_type="type1",
            edge_types=None,
            target_node_types=None,
            filter_expression=None,
            return_attributes=None,
            limit=None,
        )
        self.mock_connection.runInterpretedQuery = MagicMock(
            side_effect=Exception("Error")
        )
        df = self.query_manager.get_neighbors_from_spec(spec)
        assert df is None

    def create_gsql_get_nodes(
        self,
        node_type: Optional[str] = None,
        filter_expression: Optional[str] = None,
        return_attributes: Optional[List[str]] = None,
        limit: Optional[int] = None,
    ) -> str:
        """
        High-level function to generate a GSQL query for node selection.
        Converts parameters into a NodeSpec and delegates to `_create_gsql_get_nodes`.
        """
        spec = NodeSpec(
            node_type=node_type,
            filter_expression=filter_expression,
            return_attributes=return_attributes,
            limit=limit,
        )
        return QueryManager._create_gsql_get_nodes("MyGraph", spec)

    def test_create_gsql_get_nodes_simple(self):
        actual_gsql_script = self.create_gsql_get_nodes(node_type="Community")
        expected_gsql_script = """
INTERPRET QUERY() FOR GRAPH MyGraph {
  Nodes = {Community.*};
  PRINT Nodes;
}
""".strip()
        assert actual_gsql_script == expected_gsql_script

    def test_create_gsql_get_nodes_with_limit(self):
        actual_gsql_script = self.create_gsql_get_nodes(node_type="Community", limit=10)
        expected_gsql_script = """
INTERPRET QUERY() FOR GRAPH MyGraph {
  Nodes = {Community.*};
  Nodes =
    SELECT s
    FROM Nodes:s
    LIMIT 10
  ;
  PRINT Nodes;
}
""".strip()
        assert actual_gsql_script == expected_gsql_script

    def test_create_gsql_get_nodes_with_return_attributes(self):
        actual_gsql_script = self.create_gsql_get_nodes(
            node_type="Community",
            return_attributes=["id", "rank"],
        )
        expected_gsql_script = """
INTERPRET QUERY() FOR GRAPH MyGraph {
  Nodes = {Community.*};
  PRINT Nodes[
    Nodes.id AS id,
    Nodes.rank AS rank
  ];
}
""".strip()
        assert actual_gsql_script == expected_gsql_script

    def test_create_gsql_get_nodes_with_filter_expression(self):
        actual_gsql_script = self.create_gsql_get_nodes(
            node_type="Community",
            filter_expression="s.rank > 0",
        )
        expected_gsql_script = """
INTERPRET QUERY() FOR GRAPH MyGraph {
  Nodes = {Community.*};
  Nodes =
    SELECT s
    FROM Nodes:s
    WHERE s.rank > 0
  ;
  PRINT Nodes;
}
""".strip()
        assert actual_gsql_script == expected_gsql_script

    def test_create_gsql_get_nodes_with_node_type_none(self):
        actual_gsql_script = self.create_gsql_get_nodes(node_type=None)
        expected_gsql_script = """
INTERPRET QUERY() FOR GRAPH MyGraph {
  Nodes = {ANY};
  PRINT Nodes;
}
""".strip()
        assert actual_gsql_script == expected_gsql_script

    def test_create_gsql_get_nodes_with_all_options(self):
        actual_gsql_script = self.create_gsql_get_nodes(
            node_type="Community",
            filter_expression="s.rank > 0",
            return_attributes=["id", "rank"],
            limit=10,
        )
        expected_gsql_script = """
INTERPRET QUERY() FOR GRAPH MyGraph {
  Nodes = {Community.*};
  Nodes =
    SELECT s
    FROM Nodes:s
    WHERE s.rank > 0
    LIMIT 10
  ;
  PRINT Nodes[
    Nodes.id AS id,
    Nodes.rank AS rank
  ];
}
""".strip()
        assert actual_gsql_script == expected_gsql_script

    def create_gsql_get_neighbors(
        self,
        start_nodes: str | List[str],
        start_node_type: str,
        edge_types: Optional[str | List[str]] = None,
        target_node_types: Optional[str | List[str]] = None,
        filter_expression: Optional[str] = None,
        return_attributes: Optional[str | List[str]] = None,
        limit: Optional[int] = None,
    ) -> str:
        """
        High-level function to retrieve neighbors with multiple parameters.
        Converts parameters into a NeighborSpec and delegates to `_get_neighbors_from_spec`.
        """
        spec = NeighborSpec(
            start_nodes=start_nodes,
            start_node_type=start_node_type,
            edge_types=edge_types,
            target_node_types=target_node_types,
            filter_expression=filter_expression,
            return_attributes=return_attributes,
            limit=limit,
        )
        gsql_script, _ = QueryManager._create_gsql_get_neighbors("MyGraph", spec)
        return gsql_script

    def test_create_gsql_get_neighbors_basic(self):
        # Get neighbors with minimal parameters
        actual_gsql_script = self.create_gsql_get_neighbors(
            start_nodes=["CYTOSORB"],
            start_node_type="Entity",
        )
        expected_gsql_script = """
INTERPRET QUERY(
  SET<VERTEX<Entity>> start_nodes
) FOR GRAPH MyGraph {
  Nodes = {start_nodes};
  Neighbors =
    SELECT t
    FROM Nodes:s -(:e)- :t
  ;
  PRINT Neighbors;
}
    """.strip()
        assert actual_gsql_script == expected_gsql_script

    def test_create_gsql_get_neighbors_with_edge_and_target_types(self):
        # Get neighbors with edge types, target node types, and limit
        actual_gsql_script = self.create_gsql_get_neighbors(
            start_nodes=["CYTOSORB"],
            start_node_type="Entity",
            edge_types=["relationship", "reverse_relationship"],
            target_node_types=["Entity"],
            limit=10,
        )
        expected_gsql_script = """
INTERPRET QUERY(
  SET<VERTEX<Entity>> start_nodes
) FOR GRAPH MyGraph {
  Nodes = {start_nodes};
  Neighbors =
    SELECT t
    FROM Nodes:s -((relationship|reverse_relationship):e)- Entity:t
    LIMIT 10
  ;
  PRINT Neighbors;
}
""".strip()
        assert actual_gsql_script == expected_gsql_script

    def test_create_gsql_get_neighbors_with_single_return_attribute(self):
        # Get neighbors with edge types, target node types, and a single return attribute
        actual_gsql_script = self.create_gsql_get_neighbors(
            start_nodes="CYTOSORB",
            start_node_type="Entity",
            edge_types=["relationship", "reverse_relationship"],
            target_node_types="Entity",
            return_attributes="id",
            limit=10,
        )
        expected_gsql_script = """
INTERPRET QUERY(
  SET<VERTEX<Entity>> start_nodes
) FOR GRAPH MyGraph {
  Nodes = {start_nodes};
  Neighbors =
    SELECT t
    FROM Nodes:s -((relationship|reverse_relationship):e)- Entity:t
    LIMIT 10
  ;
  PRINT Neighbors[
    Neighbors.id AS id
  ];
}
""".strip()
        assert actual_gsql_script == expected_gsql_script

    def test_create_gsql_get_neighbors_with_multiple_return_attributes(self):
        # Get neighbors with edge types, target node types, and multiple return attributes
        actual_gsql_script = self.create_gsql_get_neighbors(
            start_nodes="CYTOSORB",
            start_node_type="Entity",
            edge_types=["relationship", "reverse_relationship"],
            target_node_types="Entity",
            return_attributes=["id", "entity_type"],
            limit=10,
        )
        expected_gsql_script = """
INTERPRET QUERY(
  SET<VERTEX<Entity>> start_nodes
) FOR GRAPH MyGraph {
  Nodes = {start_nodes};
  Neighbors =
    SELECT t
    FROM Nodes:s -((relationship|reverse_relationship):e)- Entity:t
    LIMIT 10
  ;
  PRINT Neighbors[
    Neighbors.id AS id,
    Neighbors.entity_type AS entity_type
  ];
}
""".strip()
        assert actual_gsql_script == expected_gsql_script

    def test_create_gsql_get_neighbors_with_filter_expression(self):
        # Get neighbors with edge types, target node types, filter expression, and multiple return attributes
        actual_gsql_script = self.create_gsql_get_neighbors(
            start_nodes=["CYTOSORB", "ITALY"],
            start_node_type="Entity",
            edge_types=["relationship", "reverse_relationship"],
            target_node_types="Entity",
            filter_expression="s.id != t.id",
            return_attributes=["id", "entity_type"],
            limit=10,
        )
        expected_gsql_script = """
INTERPRET QUERY(
  SET<VERTEX<Entity>> start_nodes
) FOR GRAPH MyGraph {
  Nodes = {start_nodes};
  Neighbors =
    SELECT t
    FROM Nodes:s -((relationship|reverse_relationship):e)- Entity:t
    WHERE s.id != t.id
    LIMIT 10
  ;
  PRINT Neighbors[
    Neighbors.id AS id,
    Neighbors.entity_type AS entity_type
  ];
}
""".strip()
        assert actual_gsql_script == expected_gsql_script
