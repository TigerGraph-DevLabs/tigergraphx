from typing import Optional, List
import pandas as pd

from .base_graph import BaseGraph

from tigergraphx.config import (
    NodeSchema,
    EdgeSchema,
    GraphSchema,
    TigerGraphConnectionConfig,
)


class HomoGraph(BaseGraph):
    def __init__(
        self,
        graph_name: str,
        node_type: str,
        node_schema: NodeSchema,
        edge_type: str,
        edge_schema: EdgeSchema,
        tigergraph_connection_config: Optional[TigerGraphConnectionConfig] = None,
        drop_existing_graph: bool = False,
    ):
        if not node_type:
            raise ValueError("node_type cannot be an empty string.")
        if not edge_type:
            raise ValueError("edge_type cannot be an empty string.")
        schema_config = GraphSchema(
            graph_name=graph_name,
            nodes={node_type: node_schema},
            edges={edge_type: edge_schema},
        )
        super().__init__(
            graph_schema=schema_config,
            tigergraph_connection_config=tigergraph_connection_config,
            drop_existing_graph=drop_existing_graph,
        )

    # ------------------------------ Node Operations ------------------------------
    def add_node(self, node_id: str, **attr):
        self._add_node(node_id, self.node_type, **attr)

    def add_edge(self, src_node_id: str, tgt_node_id: str, **attr):
        self._add_edge(
            src_node_id,
            tgt_node_id,
            self.node_type,
            self.edge_type,
            self.node_type,
            **attr,
        )

    def has_node(self, node_id: str) -> bool:
        return self._has_node(node_id, self.node_type)

    def get_nodes(
        self,
        filter_expression: Optional[str] = None,
        return_attributes: Optional[str | List[str]] = None,
        limit: Optional[int] = None,
    ) -> pd.DataFrame | None:
        return self._get_nodes(
            node_type=self.node_type,
            filter_expression=filter_expression,
            return_attributes=return_attributes,
            limit=limit,
        )

    # ------------------------------ Edge Operations ------------------------------
    def has_edge(self, src_node_id: str | int, tgt_node_id: str | int) -> bool:
        return self._has_edge(
            src_node_id, tgt_node_id, self.node_type, self.edge_type, self.node_type
        )

    def get_node_data(self, node_id: str) -> dict:
        return self._get_node_data(node_id, self.node_type)

    def get_edge_data(self, src_node_id: str, tgt_node_id: str) -> dict:
        return self._get_edge_data(
            src_node_id, tgt_node_id, self.node_type, self.edge_type, self.node_type
        )

    # ------------------------------ Statistics Operations ------------------------------
    def degree(self, node_id: str) -> int:
        return self._degree(node_id, self.node_type, self.edge_type)

    def number_of_nodes(self) -> int:
        return self._number_of_nodes()

    # ------------------------------ Query Operations ------------------------------
    def get_node_edges(
        self,
        node_id: str,
        num_edge_samples: int = 1000,
    ):
        edges = self._get_node_edges(
            node_id,
            self.node_type,
            self.edge_type,
            num_edge_samples,
        )
        result = [(edge["from_id"], edge["to_id"]) for edge in edges]
        return result

    def get_neighbors(
        self,
        start_nodes: str | List[str],
        edge_types: Optional[str | List[str]] = None,
        target_node_types: Optional[str | List[str]] = None,
        filter_expression: Optional[str] = None,
        return_attributes: Optional[str | List[str]] = None,
        limit: Optional[int] = None,
    ) -> pd.DataFrame | None:
        return self._get_neighbors(
            start_nodes=start_nodes,
            start_node_type=self.node_type,
            edge_types=edge_types,
            target_node_types=target_node_types,
            filter_expression=filter_expression,
            return_attributes=return_attributes,
            limit=limit,
        )
