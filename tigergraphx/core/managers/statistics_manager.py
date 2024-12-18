import logging
from typing import List, Optional
from urllib.parse import urlencode, quote

from .base_manager import BaseManager

from tigergraphx.core.graph_context import GraphContext


logger = logging.getLogger(__name__)


class StatisticsManager(BaseManager):
    def __init__(self, context: GraphContext):
        super().__init__(context)

    def degree(self, node_id: str, node_type: str, edge_types: List | str) -> int:
        try:
            params = {
                "input": node_id,
                "input.type": node_type,
                "edge_types": edge_types,
            }
            params_str = urlencode(params, quote_via=quote)
            result = self._connection.runInstalledQuery("api_degree", params_str)
            if result:
                return result[0].get("degree", 0)
        except Exception as e:
            logger.error(f"Error retrieving degree of node {node_id}: {e}")
        return 0

    def number_of_nodes(
        self, node_type: Optional[str | list] = None
    ) -> int:
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

    def number_of_edges(
        self, edge_type: Optional[str] = None
    ) -> int:
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
