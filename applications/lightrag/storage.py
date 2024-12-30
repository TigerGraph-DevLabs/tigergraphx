import os
from dataclasses import dataclass
from typing import Dict, Any
import numpy as np

from lightrag.base import BaseGraphStorage
from lightrag.utils import logger
from tigergraphx import UndiGraph, TigerGraphConnectionConfig


@dataclass
class TigerGraphStorage(BaseGraphStorage):
    def __post_init__(self):
        try:
            # Retrieve connection configuration from environment variables
            connection_config = {
                "host": os.environ["TG_HOST"],
                "username": os.environ["TG_USERNAME"],
                "password": os.environ["TG_PASSWORD"],
            }
            logger.info("TigerGraph connection configuration retrieved successfully.")
            # Initialize the graph
            self._graph = UndiGraph(
                graph_name="LightRAG",
                node_type="MyNode",
                edge_type="MyEdge",
                node_primary_key="id",
                node_attributes={
                    "id": "STRING",
                    "entity_type": "STRING",
                    "description": "STRING",
                    "source_id": "STRING",
                },
                edge_attributes={
                    "weight": "DOUBLE",
                    "description": "STRING",
                    "keywords": "STRING",
                    "source_id": "STRING",
                },
                tigergraph_connection_config=TigerGraphConnectionConfig.ensure_config(
                    connection_config
                ),
            )
            logger.info(
                "Undirected graph initialized successfully with graph_name 'LightRAG'."
            )
        except KeyError as e:
            logger.error(f"Environment variable {str(e)} is missing.")
            raise
        except Exception as e:
            logger.error(f"An error occurred during initialization: {e}")
            raise

    @staticmethod
    def clean_quotes(value: str) -> str:
        """Remove leading and trailing &quot; from a string if present."""
        if value.startswith('"') and value.endswith('"'):
            return value[1:-1]
        return value

    async def has_node(self, node_id: str) -> bool:
        return self._graph.has_node(self.clean_quotes(node_id))

    async def has_edge(self, source_node_id: str, target_node_id: str) -> bool:
        return self._graph.has_edge(
            self.clean_quotes(source_node_id), self.clean_quotes(target_node_id)
        )

    async def node_degree(self, node_id: str) -> int:
        result = self._graph.degree(self.clean_quotes(node_id))
        return result

    async def edge_degree(self, src_id: str, tgt_id: str) -> int:
        return self._graph.degree(self.clean_quotes(src_id)) + self._graph.degree(
            self.clean_quotes(tgt_id)
        )

    async def get_node(self, node_id: str) -> dict | None:
        result = self._graph.get_node_data(self.clean_quotes(node_id))
        return result

    async def get_edge(self, source_node_id: str, target_node_id: str) -> dict | None:
        result = self._graph.get_edge_data(
            self.clean_quotes(source_node_id), self.clean_quotes(target_node_id)
        )
        return result

    async def get_node_edges(self, source_node_id: str) -> list[tuple[str, str]] | None:
        source_node_id = self.clean_quotes(source_node_id)
        if self._graph.has_node(source_node_id):
            edges = self._graph.get_node_edges(source_node_id)
            return list(edges)
        return None

    async def upsert_node(self, node_id: str, node_data: Dict[str, Any]):
        node_id = self.clean_quotes(node_id)
        self._graph.add_node(node_id, **node_data)

    async def upsert_edge(
        self, source_node_id: str, target_node_id: str, edge_data: Dict[str, Any]
    ):
        source_node_id = self.clean_quotes(source_node_id)
        target_node_id = self.clean_quotes(target_node_id)
        self._graph.add_edge(source_node_id, target_node_id, **edge_data)

    async def delete_node(self, node_id: str):
        if self._graph.has_node(node_id):
            self._graph.remove_node(node_id)
            logger.info(f"Node {node_id} deleted from the graph.")
        else:
            logger.warning(f"Node {node_id} not found in the graph for deletion.")

    async def embed_nodes(self, algorithm: str) -> tuple[np.ndarray, list[str]]:
        return np.array([]), []
