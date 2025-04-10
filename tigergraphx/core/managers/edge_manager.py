# Copyright 2025 TigerGraph Inc.
# Licensed under the Apache License, Version 2.0.
# See the LICENSE file or https://www.apache.org/licenses/LICENSE-2.0
#
# Permission is granted to use, copy, modify, and distribute this software
# under the License. The software is provided "AS IS", without warranty.

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
            attributes = {key: {"value": value} for key, value in attr.items()}
            payload = {
                "edges": {
                    src_node_type: {
                        src_node_id: {
                            edge_type: {tgt_node_type: {tgt_node_id: attributes}}
                        }
                    }
                }
            }
            result = self._tigergraph_api.upsert_graph_data(self._graph_name, payload)
            return result[0].get("accepted_edges", 0)
        except Exception as e:
            logger.error(f"Error adding edge from {src_node_id} to {tgt_node_id}: {e}")
            return None

    def add_edges_from(
        self,
        normalized_edges: List[Tuple[str, str, Dict[str, Any]]],
        src_node_type: str,
        edge_type: str,
        tgt_node_type: str,
    ) -> Optional[int]:
        try:
            edges = {}
            for src_id, tgt_id, attributes in normalized_edges:
                attr_payload = {
                    key: {"value": value} for key, value in attributes.items()
                }
                # Navigate down to the right nested spot
                edges.setdefault(src_node_type, {}).setdefault(src_id, {}).setdefault(
                    edge_type, {}
                ).setdefault(tgt_node_type, {})[tgt_id] = attr_payload
            payload = {"edges": edges}

            result = self._tigergraph_api.upsert_graph_data(self._graph_name, payload)
            return result[0].get("accepted_edges", 0)
        except Exception as e:
            logger.error(f"Error adding edges: {e}")
            return None

    def has_edge(
        self,
        src_node_id: str,
        tgt_node_id: str,
        src_node_type: str,
        edge_type: str,
        tgt_node_type: str,
    ) -> bool:
        try:
            result = self._tigergraph_api.retrieve_a_edge(
                graph_name=self._graph_name,
                source_node_type=src_node_type,
                source_node_id=src_node_id,
                edge_type=edge_type,
                target_node_type=tgt_node_type,
                target_node_id=tgt_node_id,
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
    ) -> Dict | Dict[int | str, Dict] | None:
        try:
            result = self._tigergraph_api.retrieve_a_edge(
                graph_name=self._graph_name,
                source_node_type=src_node_type,
                source_node_id=src_node_id,
                edge_type=edge_type,
                target_node_type=tgt_node_type,
                target_node_id=tgt_node_id,
            )
            if isinstance(result, list) and result:
                # Ensure elements are dicts
                valid_edges = [edge for edge in result if isinstance(edge, dict)]
                if not valid_edges:
                    return None
                # Single edge case
                if len(valid_edges) == 1:
                    return valid_edges[0].get("attributes", None)
                # Multi-edge case
                multi_edge_data = {}
                for index, edge in enumerate(valid_edges):
                    edge_id = edge.get("discriminator", index)
                    multi_edge_data[edge_id] = edge.get("attributes", {})
                return multi_edge_data
            return None  # Return None if result is not a valid list or empty
        except Exception:
            return None  # Suppress errors (could log for debugging)
