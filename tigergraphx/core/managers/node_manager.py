import logging
from typing import Dict, List
from urllib.parse import urlencode, quote

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
        edge_types: List | str,
        num_edge_samples: int = 1000,
    ) -> List:
        try:
            params = {
                "input": node_id,
                "input.type": node_type,
                "edge_types": edge_types,
                "num_edge_samples": num_edge_samples,
            }
            params_str = urlencode(params, quote_via=quote)
            result = self._connection.runInstalledQuery("api_get_node_edges", params_str)
            if result:
                return result[0].get("edges")
        except Exception as e:
            logger.error(f"Error retrieving edges for node {node_id}: {e}")
        return []
