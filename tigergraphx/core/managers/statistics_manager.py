import logging
from typing import List

from tigergraphx.core.base_manager import BaseManager
from tigergraphx.core.graph_context import GraphContext


logger = logging.getLogger(__name__)


class StatisticsManager(BaseManager):
    def __init__(self, context: GraphContext):
        super().__init__(context)

    def degree(self, node_id: str, node_type: str, edge_types: List | str) -> int:
        try:
            params = {
                "input": (node_id, node_type),
                "edge_types": edge_types,
            }
            result = self._connection.runInstalledQuery("api_degree", params)
            if result:
                return result[0].get("degree", 0)
        except Exception as e:
            logger.error(f"Error retrieving degree of node {node_id}: {e}")
        return 0
