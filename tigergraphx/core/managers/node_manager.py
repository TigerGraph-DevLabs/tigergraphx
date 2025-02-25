# Copyright 2025 TigerGraph Inc.
# Licensed under the Apache License, Version 2.0.
# See the LICENSE file or https://www.apache.org/licenses/LICENSE-2.0
#
# Permission is granted to use, copy, modify, and distribute this software
# under the License. The software is provided "AS IS", without warranty.

import logging
from typing import Any, Dict, List, Optional, Set, Tuple

from .base_manager import BaseManager

from tigergraphx.core.graph_context import GraphContext


logger = logging.getLogger(__name__)


class NodeManager(BaseManager):
    def __init__(self, context: GraphContext):
        super().__init__(context)

    def add_node(self, node_id: str, node_type: str, **attr):
        try:
            self._connection.upsertVertex(node_type, node_id, attr)
        except Exception as e:
            logger.error(f"Error adding node {node_id}: {e}")
            return None

    def add_nodes_from(
        self,
        normalized_nodes: List[Tuple[str, Dict[str, Any]]],
        node_type: str,
    ) -> Optional[int]:
        # Call upsertVertices with the list of nodes and attributes
        try:
            result = self._connection.upsertVertices(
                vertexType=node_type, vertices=normalized_nodes
            )
            return result
        except Exception as e:
            logger.error(f"Error adding nodes: {e}")
            return None

    def remove_node(self, node_id: str, node_type: str) -> bool:
        try:
            if self._connection.delVerticesById(node_type, node_id) > 0:
                return True
            else:
                return False
        except Exception as e:
            logger.error(f"Error removing node {node_id}: {e}")
            return False

    def has_node(self, node_id: str, node_type: str) -> bool:
        try:
            result = self._connection.getVerticesById(node_type, node_id)
            return bool(result)
        except Exception:
            return False

    def get_node_data(self, node_id: str, node_type: str) -> Dict | None:
        """Retrieve node attributes by type and ID."""
        try:
            result = self._connection.getVerticesById(
                vertexType=node_type,
                vertexIds=node_id,
            )
            if isinstance(result, List) and result:
                return result[0].get("attributes", None)
            else:
                raise TypeError(f"Unsupported type for result: {type(result)}")
        except (TypeError, Exception):
            return None

    def get_node_edges(
        self,
        node_id: str,
        node_type: str,
        edge_types: Optional[Set[str]] = None,
    ) -> List:
        gsql_script = self._create_gsql_get_node_edges(node_type, edge_types)
        try:
            params = {
                "input": node_id,
            }
            result = self._connection.runInterpretedQuery(gsql_script, params)
            if result and isinstance(result, list):
                return result[0].get("edges")
        except Exception as e:
            logger.error(f"Error retrieving edges for node {node_id}: {e}")
        return []

    def clear(self) -> bool:
        try:
            # Attempt to delete vertices for each node type
            for node_type in self._graph_schema.nodes:
                self._connection.delVertices(node_type)
            return True
        except Exception as e:
            logger.error(f"Error clearing graph: {e}")
            return False

    def _create_gsql_get_node_edges(
        self, node_type: str, edge_types: Optional[Set[str]] = None
    ) -> str:
        """
        Core function to generate a GSQL query to get the edges of a node
        """
        graph_name = self._graph_schema.graph_name
        if not edge_types:
            from_clause = "FROM Nodes:s -(:e)- :t"
        else:
            if (isinstance(edge_types, list) and len(edge_types) == 1) or isinstance(
                edge_types, str
            ):
                edge_type = edge_types if isinstance(edge_types, str) else edge_types[0]
                from_clause = f"FROM Nodes:s -({edge_type}:e)- :t"
            else:
                edge_types_str = "|".join(edge_types)
                from_clause = f"FROM Nodes:s -({edge_types_str}:e)- :t"

        # Generate the query
        query = f"""
INTERPRET QUERY(VERTEX<{node_type}> input) FOR GRAPH {graph_name} {{
  SetAccum<EDGE> @@set_edge;
  Nodes = {{input}};
  Nodes =
    SELECT t
    {from_clause}
    ACCUM @@set_edge += e
  ;
  PRINT @@set_edge AS edges;
}}"""
        return query.strip()
