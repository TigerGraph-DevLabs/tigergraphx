import logging
from typing import List, Optional

from .base_manager import BaseManager

from tigergraphx.core.graph_context import GraphContext


logger = logging.getLogger(__name__)


class StatisticsManager(BaseManager):
    def __init__(self, context: GraphContext):
        super().__init__(context)

    def degree(self, node_id: str, node_type: str, edge_types: List | str) -> int:
        gsql_script = self._create_gsql_degree(
            node_type, edge_types, self._graph_schema.graph_name
        )
        try:
            params = {
                "input": node_id
            }
            result = self._connection.runInterpretedQuery(gsql_script, params)
            if not result or not isinstance(result, list):
                return 0
            return result[0].get("degree", 0)
        except Exception as e:
            logger.error(f"Error retrieving degree of node {node_id}: {e}")
        return 0

    def number_of_nodes(self, node_type: Optional[str | list] = None) -> int:
        """Return the number of nodes for the given node type(s)."""
        try:
            if node_type is None or node_type == "":
                node_type = "*"
            result = self._connection.getVertexCount(node_type)
            if isinstance(result, dict):
                return sum(result.values())
            return result
        except Exception as e:
            logger.error(
                f"Error retrieving number of nodes for node type {node_type}: {e}"
            )
            return 0

    def number_of_edges(self, edge_type: Optional[str] = None) -> int:
        """Return the number of edges for the given edge type(s)."""
        try:
            if edge_type is None or edge_type == "":
                edge_type = "*"
            result = self._connection.getEdgeCount(edge_type)
            if isinstance(result, dict):
                return sum(result.values())
            return result
        except Exception as e:
            logger.error(
                f"Error retrieving number of edges for edge type {edge_type}: {e}"
            )
            return 0

    @staticmethod
    def _create_gsql_degree(
        node_type: str, edge_types: List | str, graph_name: str
    ) -> str:
        """
        Core function to generate a GSQL query to get the degree of a node
        """
        if not edge_types:
            from_clause = "FROM Nodes:s -()- :t"
        else:
            if (isinstance(edge_types, list) and len(edge_types) == 1) or isinstance(
                edge_types, str
            ):
                edge_type = edge_types if isinstance(edge_types, str) else edge_types[0]
                from_clause = f"FROM Nodes:s -({edge_type})- :t"
            else:
                edge_types_str = "|".join(edge_types)
                from_clause = f"FROM Nodes:s -({edge_types_str})- :t"

        # Generate the query
        query = f"""
INTERPRET QUERY(VERTEX<{node_type}> input) FOR GRAPH {graph_name} {{
  SumAccum<INT> @@sum_degree;
  Nodes = {{input}};
  Nodes =
    SELECT s
    {from_clause}
    ACCUM  @@sum_degree += 1
  ;
  PRINT @@sum_degree AS degree;
}}"""
        return query.strip()
