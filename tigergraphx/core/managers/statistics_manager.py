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
            params = {"input": node_id}
            result = self._connection.runInterpretedQuery(gsql_script, params)
            if not result or not isinstance(result, list):
                return 0
            return result[0].get("degree", 0)
        except Exception as e:
            logger.error(f"Error retrieving degree of node {node_id}: {e}")
        return 0

    def number_of_nodes(self, node_type: Optional[str | list] = None) -> int:
        """Return the number of nodes for the given node type(s)."""
        gsql_script = self._create_gsql_number_of_nodes(
            node_type, self._graph_schema.graph_name
        )
        try:
            result = self._connection.runInterpretedQuery(gsql_script)
            # Perform checks
            if not isinstance(result, list):
                raise ValueError(
                    f"Expected result to be a list, but got {type(result)}"
                )
            if len(result) == 0:
                raise ValueError("Result is an empty list")
            if not isinstance(result[0], dict):
                raise ValueError(
                    f"Expected the first item in the result to be a dictionary, but got {type(result[0])}"
                )
            if "number_of_nodes" not in result[0]:
                raise KeyError(
                    "The key 'number_of_nodes' is missing in the result dictionary"
                )
            return result[0]["number_of_nodes"]
        except Exception as e:
            logger.error(
                f"Error retrieving number of nodes for node type {node_type}: {e}"
            )
            return 0

    def number_of_edges(self, edge_type: Optional[str] = None) -> int:
        """Return the number of edges for the given edge type(s)."""
        gsql_script = self._create_gsql_number_of_edges(
            edge_type, self._graph_schema.graph_name
        )
        try:
            result = self._connection.runInterpretedQuery(gsql_script)
            # Perform checks
            if not isinstance(result, list):
                raise ValueError(
                    f"Expected result to be a list, but got {type(result)}"
                )
            if len(result) == 0:
                raise ValueError("Result is an empty list")
            if not isinstance(result[0], dict):
                raise ValueError(
                    f"Expected the first item in the result to be a dictionary, but got {type(result[0])}"
                )
            if "number_of_edges" not in result[0]:
                raise KeyError(
                    "The key 'number_of_edges' is missing in the result dictionary"
                )
            return result[0]["number_of_edges"]
        except Exception as e:
            logger.error(
                f"Error retrieving number of edges for edge type {edge_type}: {e}"
            )
            return 0

    # def number_of_edges(self, edge_type: Optional[str] = None) -> int:
    #     """Return the number of edges for the given edge type(s)."""
    #     try:
    #         if edge_type is None or edge_type == "":
    #             edge_type = "*"
    #         result = self._connection.getEdgeCount(edge_type)
    #         if isinstance(result, dict):
    #             return sum(result.values())
    #         return result
    #     except Exception as e:
    #         logger.error(
    #             f"Error retrieving number of edges for edge type {edge_type}: {e}"
    #         )
    #         return 0

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

    @staticmethod
    def _create_gsql_number_of_nodes(
        node_type: Optional[str | list], graph_name: str
    ) -> str:
        # Generate the query
        if node_type is None or node_type == "":
            query = f"""
INTERPRET QUERY() FOR GRAPH {graph_name} {{
  Nodes = {{ANY}};
  PRINT Nodes.size() AS number_of_nodes;
}}"""
        else:
            query = f"""
INTERPRET QUERY() FOR GRAPH {graph_name} {{
  Nodes = {{{node_type}.*}};
  PRINT Nodes.size() AS number_of_nodes;
}}"""
        return query.strip()

    @staticmethod
    def _create_gsql_number_of_edges(
        edge_type: Optional[str | list], graph_name: str
    ) -> str:
        # Generate the query
        if edge_type is None or edge_type == "":
            query = f"""
INTERPRET QUERY() FOR GRAPH {graph_name} {{
  SumAccum<INT> @@sum;
  Nodes = {{ANY}};
  Nodes =
    SELECT s
    FROM Nodes:s -()- :t
    ACCUM @@sum += 1
  ;
  PRINT @@sum AS number_of_edges;
}}"""
        else:
            query = f"""
INTERPRET QUERY() FOR GRAPH {graph_name} {{
  SumAccum<INT> @@sum;
  Nodes = {{ANY}};
  Nodes =
    SELECT s
    FROM Nodes:s -({edge_type})- :t
    ACCUM @@sum += 1
  ;
  PRINT @@sum AS number_of_edges;
}}"""
        return query.strip()
