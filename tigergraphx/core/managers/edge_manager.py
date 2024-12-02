import logging
from typing import Dict, List

from .base_manager import BaseManager

from tigergraphx.core.graph_context import GraphContext


logger = logging.getLogger(__name__)


class EdgeManager(BaseManager):
    def __init__(self, context: GraphContext):
        super().__init__(context)

    def add_edge(
        self,
        src_node_id: str,
        tgt_node_id: str,
        src_node_type: str,
        edge_type: str,
        tgt_node_type: str,
        **attr,
    ):
        try:
            result = self._connection.upsertEdge(
                src_node_type, src_node_id, edge_type, tgt_node_type, tgt_node_id, attr
            )
        except Exception as e:
            logger.error(f"Error adding from {src_node_id} to {tgt_node_id}: {e}")
            return None

    def has_edge(
        self,
        src_node_id: str | int,
        tgt_node_id: str | int,
        src_node_type: str,
        edge_type: str,
        tgt_node_type: str,
    ) -> bool:
        try:
            result = self._connection.getEdgeCountFrom(
                src_node_type, src_node_id, edge_type, tgt_node_type, tgt_node_id
            )
            return bool(result)
        except Exception as e:
            logger.error(
                f"Error checking existence of edge from {src_node_id} to {tgt_node_type}: {e}"
            )
            return False

    def get_edge_data(
        self,
        src_node_id: str,
        tgt_node_id: str,
        src_node_type: str,
        edge_type: str,
        tgt_node_type: str,
    ) -> Dict:
        try:
            result = self._connection.getEdges(
                src_node_type, src_node_id, edge_type, tgt_node_type, tgt_node_id
            )
            if isinstance(result, List) and result:
                return result[0].get("attributes", {})
            else:
                raise TypeError(f"Unsupported type for result: {type(result)}")
        except Exception as e:
            logger.error(
                f"Error retrieving edge from {src_node_id} to {tgt_node_id}: {e}"
            )
            return {}
