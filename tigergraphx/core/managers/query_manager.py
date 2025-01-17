import logging
from typing import List, Dict, Optional, Tuple
import pandas as pd

from tigergraphx.config import (
    NodeSpec,
    NeighborSpec,
)

from .base_manager import BaseManager

from tigergraphx.core.graph_context import GraphContext


logger = logging.getLogger(__name__)


class QueryManager(BaseManager):
    def __init__(self, context: GraphContext):
        super().__init__(context)

    def run_query(self, query_name: str, params: Dict = {}):
        try:
            return self._connection.runInstalledQuery(
                queryName=query_name, params=params
            )
        except Exception as e:
            logger.error(f"Error running query {query_name}: {e}")
            return None

    def get_nodes(
        self,
        node_type: str,
        all_node_types: bool = False,
        node_alias: str = "s",
        filter_expression: Optional[str] = None,
        return_attributes: Optional[str | List[str]] = None,
        limit: Optional[int] = None,
    ) -> pd.DataFrame | None:
        """
        High-level function to retrieve nodes with multiple parameters.
        Converts parameters into a NodeSpec and delegates to `_get_nodes_from_spec`.
        """
        spec = NodeSpec(
            node_type=node_type,
            all_node_types=all_node_types,
            node_alias=node_alias,
            filter_expression=filter_expression,
            return_attributes=return_attributes,
            limit=limit,
        )
        return self.get_nodes_from_spec(spec)

    def get_nodes_from_spec(self, spec: NodeSpec) -> pd.DataFrame | None:
        """
        Core function to retrieve nodes based on a NodeSpec object.
        """
        gsql_script = self._create_gsql_get_nodes(self._graph_schema.graph_name, spec)
        try:
            result = self._connection.runInterpretedQuery(gsql_script)
            if not result or not isinstance(result, list):
                return None
            nodes = result[0].get("Nodes")
            if not nodes or not isinstance(nodes, list):
                return None
            df = pd.DataFrame(pd.json_normalize(nodes))
            if df.empty:
                return None
            attribute_columns = [
                col for col in df.columns if col.startswith("attributes.")
            ]
            if spec.return_attributes is None:
                rename_map = {
                    col: col.replace("attributes.", "") for col in attribute_columns
                }
                reordered_columns = []
            else:
                rename_map = {
                    f"attributes.{attr}": attr for attr in spec.return_attributes
                }
                reordered_columns = [
                    attr
                    for attr in spec.return_attributes
                    if attr in rename_map.values()
                ]
            df.rename(columns=rename_map, inplace=True)
            drop_columns = []
            if spec.return_attributes is not None:
                drop_columns = ["v_id"]
                if spec.node_type is not None and "v_type" in df.columns:
                    drop_columns.append("v_type")
            df.drop(columns=drop_columns, inplace=True)
            remaining_columns = [
                col for col in df.columns if col not in reordered_columns
            ]
            return pd.DataFrame(df[reordered_columns + remaining_columns])
        except Exception as e:
            logger.error(f"Error retrieving nodes for type {spec.node_type}: {e}")
        return None

    def get_neighbors(
        self,
        start_nodes: str | List[str],
        start_node_type: str,
        start_node_alias: str = "s",
        edge_types: Optional[str | List[str]] = None,
        edge_alias: str = "e",
        target_node_types: Optional[str | List[str]] = None,
        target_node_alias: str = "t",
        filter_expression: Optional[str] = None,
        return_attributes: Optional[str | List[str]] = None,
        limit: Optional[int] = None,
    ) -> pd.DataFrame | None:
        """
        High-level function to retrieve neighbors with multiple parameters.
        Converts parameters into a NeighborSpec and delegates to `_get_neighbors_from_spec`.
        """
        spec = NeighborSpec(
            start_nodes=start_nodes,
            start_node_type=start_node_type,
            start_node_alias=start_node_alias,
            edge_types=edge_types,
            edge_alias=edge_alias,
            target_node_types=target_node_types,
            target_node_alias=target_node_alias,
            filter_expression=filter_expression,
            return_attributes=return_attributes,
            limit=limit,
        )
        return self.get_neighbors_from_spec(spec)

    def get_neighbors_from_spec(self, spec: NeighborSpec) -> pd.DataFrame | None:
        """
        Core function to retrieve neighbors based on a NeighborSpec object.
        """
        gsql_script, params = self._create_gsql_get_neighbors(
            self._graph_schema.graph_name, spec
        )
        try:
            result = self._connection.runInterpretedQuery(gsql_script, params)
            if not result or not isinstance(result, list):
                return None
            neighbors = result[0].get("Neighbors")
            if not neighbors or not isinstance(neighbors, list):
                return None
            df = pd.DataFrame(pd.json_normalize(neighbors))
            if df.empty:
                return None
            attribute_columns = [
                col for col in df.columns if col.startswith("attributes.")
            ]
            if spec.return_attributes is None:
                rename_map = {
                    col: col.replace("attributes.", "") for col in attribute_columns
                }
                reordered_columns = []
            else:
                rename_map = {
                    f"attributes.{attr}": attr for attr in spec.return_attributes
                }
                reordered_columns = [
                    attr
                    for attr in spec.return_attributes
                    if attr in rename_map.values()
                ]
            df.rename(columns=rename_map, inplace=True)
            drop_columns = [col for col in ["v_id", "v_type"] if col in df.columns]
            df.drop(columns=drop_columns, inplace=True)
            remaining_columns = [
                col for col in df.columns if col not in reordered_columns
            ]
            return pd.DataFrame(df[reordered_columns + remaining_columns])
        except Exception as e:
            logger.error(
                f"Error retrieving neighbors for node(s) {spec.start_nodes}: {e}"
            )
        return None

    @staticmethod
    def _create_gsql_get_nodes(graph_name: str, spec: NodeSpec) -> str:
        """
        Core function to generate a GSQL query based on a NodeSpec object.
        """
        node_type_str = f"{spec.node_type}.*" if not spec.all_node_types else "ANY"
        filter_expression_str = (
            f"WHERE {spec.filter_expression}" if spec.filter_expression else ""
        )
        limit_clause = f"LIMIT {spec.limit}" if spec.limit else ""
        return_attributes = spec.return_attributes or []

        # Generate the base query
        query = f"""
INTERPRET QUERY() FOR GRAPH {graph_name} {{
  Nodes = {{{node_type_str}}};
"""
        # Add SELECT block only if filter or limit is specified
        if filter_expression_str or limit_clause:
            query += f"""  Nodes =
    SELECT {spec.node_alias}
    FROM Nodes:{spec.node_alias}
"""
            if filter_expression_str:
                query += f"    {filter_expression_str}\n"
            if limit_clause:
                query += f"    {limit_clause}\n"
            query += "  ;\n"

        # Add PRINT statement
        if return_attributes:
            prefixed_attributes = ",\n    ".join(
                [f"Nodes.{attr} AS {attr}" for attr in return_attributes]
            )
            query += f"  PRINT Nodes[\n    {prefixed_attributes}\n  ];"
        else:
            query += "  PRINT Nodes;"

        query += "\n}"
        return query.strip()

    @staticmethod
    def _create_gsql_get_neighbors(
        graph_name: str, spec: NeighborSpec
    ) -> Tuple[str, str]:
        """
        Core function to generate a GSQL query based on a NeighborSpec object.
        """
        # Normalize fields to lists
        params = "&".join(
            [
                f"start_nodes={node}"
                for node in (
                    [spec.start_nodes]
                    if isinstance(spec.start_nodes, str)
                    else spec.start_nodes
                )
            ]
        )
        edge_types = (
            [spec.edge_types] if isinstance(spec.edge_types, str) else spec.edge_types
        )
        target_node_types = (
            [spec.target_node_types]
            if isinstance(spec.target_node_types, str)
            else spec.target_node_types
        )
        return_attributes = (
            [spec.return_attributes]
            if isinstance(spec.return_attributes, str)
            else spec.return_attributes
        )

        # Handle filter expression
        filter_expression = spec.filter_expression
        filter_expression_str = (
            filter_expression if isinstance(filter_expression, str) else None
        )

        # Prepare components
        start_node_type = spec.start_node_type
        edge_types_str = (
            f"(({'|'.join(edge_types or [])}):{spec.edge_alias})"
            if edge_types and len(edge_types) > 1
            else f"({'|'.join(edge_types or [])}:{spec.edge_alias})"
            if edge_types
            else f"(:{spec.edge_alias})"
        )
        target_node_types_str = (
            f"(({'|'.join(target_node_types or [])}))"
            if target_node_types and len(target_node_types) > 1
            else f"{'|'.join(target_node_types or [])}"
        )

        where_clause = (
            f"    WHERE {filter_expression_str}" if filter_expression_str else ""
        )
        limit_clause = f"    LIMIT {spec.limit}" if spec.limit else ""

        # Generate the query
        s_alias = spec.start_node_alias
        t_alias = spec.target_node_alias
        query = f"""
INTERPRET QUERY(
  SET<VERTEX<{start_node_type}>> start_nodes
) FOR GRAPH {graph_name} {{
  Nodes = {{start_nodes}};
  Neighbors =
    SELECT {t_alias}
    FROM Nodes:{s_alias} -{edge_types_str}- {target_node_types_str}:{t_alias}
"""
        if where_clause:
            query += f"{where_clause}\n"
        if limit_clause:
            query += f"{limit_clause}\n"

        query += "  ;\n"

        # Add PRINT statement
        if return_attributes:
            prefixed_attributes = ",\n    ".join(
                [f"Neighbors.{attr} AS {attr}" for attr in return_attributes]
            )
            query += f"  PRINT Neighbors[\n    {prefixed_attributes}\n  ];"
        else:
            query += "  PRINT Neighbors;"

        query += "\n}"
        return (query.strip(), params)
