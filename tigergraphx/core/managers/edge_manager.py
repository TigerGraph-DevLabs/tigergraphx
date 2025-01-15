import logging
from typing import Any, Dict, List, Optional, Tuple

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
            self._connection.upsertEdge(
                src_node_type, src_node_id, edge_type, tgt_node_type, tgt_node_id, attr
            )
        except Exception as e:
            logger.error(f"Error adding from {src_node_id} to {tgt_node_id}: {e}")
            return None

    def add_edges_from(
        self,
        ebunch_to_add: List[Tuple[str, str]] | List[Tuple[str, str, Dict[str, Any]]],
        src_node_type: str,
        edge_type: str,
        tgt_node_type: str,
        **attr,
    ) -> Optional[int]:
        edges_to_upsert = []

        # Process each edge
        for edge in ebunch_to_add:
            if isinstance(edge, tuple) and len(edge) == 2:
                src_node_id, tgt_node_id = edge
                attributes = {}
            elif isinstance(edge, tuple) and len(edge) == 3:
                src_node_id, tgt_node_id, attributes = edge
                if not isinstance(attributes, dict):
                    logger.error(
                        f"Attributes for edge {src_node_id} -> {tgt_node_id} should be a dictionary."
                    )
                    return None
            else:
                logger.error(
                    f"Invalid node format: {edge}. Expected Tuple[str, str] or Tuple[str, str, Dict[str, Any]]."
                )
                return None

            # Combine edge-specific attributes with the common attributes
            edge_data = {**attributes, **attr}

            # Append to edge list
            edges_to_upsert.append((src_node_id, tgt_node_id, edge_data))

        # Call upsertEdges with the list of edges and attributes
        try:
            result = self._connection.upsertEdges(
                sourceVertexType=src_node_type,
                edgeType=edge_type,
                targetVertexType=tgt_node_type,
                edges=edges_to_upsert,
            )
            return result
        except Exception as e:
            logger.error(f"Error adding edges: {e}")
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
        except Exception:
            return False

    def get_edge_data(
        self,
        src_node_id: str,
        tgt_node_id: str,
        src_node_type: str,
        edge_type: str,
        tgt_node_type: str,
    ) -> Dict | None:
        try:
            result = self._connection.getEdges(
                src_node_type, src_node_id, edge_type, tgt_node_type, tgt_node_id
            )
            if isinstance(result, List) and result: # pyright: ignore
                return result[0].get("attributes", None) # pyright: ignore
            else:
                raise TypeError(f"Unsupported type for result: {type(result)}")
        except Exception:
            return None
