import logging
from typing import Dict, List

from .base_manager import BaseManager

from tigergraphx.core.graph_context import GraphContext


logger = logging.getLogger(__name__)


class VectorManager(BaseManager):
    def __init__(self, context: GraphContext):
        super().__init__(context)

    def vector_search(
        self,
        query_vector: List[float],
        vector_attribute_name: str,
        node_type: str,
        k: int = 10,
    ) -> Dict[str, float]:
        try:
            query_name = f"api_vector_search_{node_type}_{vector_attribute_name}"
            params = {
                "k": k,
                "query_vector": query_vector,
            }
            result = self._connection.runInstalledQuery(query_name, params)
            if result:
                return result[0].get("map_node_distance")
        except Exception as e:
            logger.error(
                f"Error performing vector search for vector attribute "
                f"{vector_attribute_name} of node type {node_type}: {e}"
            )
        return {}
