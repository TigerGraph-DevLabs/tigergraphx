from typing import List, Optional
import pandas as pd

from .base_graph import BaseGraph


class Graph(BaseGraph):
    """
    One interface rules them all
    - UndiGraph
    - DiGraph
    - MultiGraph
    - DiMultiGraph
    """

    # ------------------------------ Node Operations ------------------------------
    def add_node(self, node_id: str, node_type: str = "", **attr) -> None:
        node_type = self._validate_node_type(node_type)
        self._add_node(node_id, node_type, **attr)

    def has_node(self, node_id: str, node_type: str = "") -> bool:
        node_type = self._validate_node_type(node_type)
        return self._has_node(node_id, node_type)

    def get_node_data(self, node_id: str, node_type: str = "") -> dict:
        node_type = self._validate_node_type(node_type)
        return self._get_node_data(node_id, node_type)

    def get_node_edges(
        self,
        node_id: str,
        node_type: str = "",
        edge_types: List | str = [],
        num_edge_samples: int = 1000,
    ):
        node_type = self._validate_node_type(node_type)
        return self._get_node_edges(
            node_id,
            node_type,
            edge_types,
            num_edge_samples,
        )

    # ------------------------------ Edge Operations ------------------------------
    def add_edge(
        self,
        src_node_id: str,
        tgt_node_id: str,
        src_node_type: str = "",
        edge_type: str = "",
        tgt_node_type: str = "",
        **attr,
    ) -> None:
        src_node_type, edge_type, tgt_node_type = self._validate_edge_type(
            src_node_type, edge_type, tgt_node_type
        )
        self._add_edge(
            src_node_id,
            tgt_node_id,
            src_node_type,
            edge_type,
            tgt_node_type,
            **attr,
        )

    def has_edge(
        self,
        src_node_id: str | int,
        tgt_node_id: str | int,
        src_node_type: str = "",
        edge_type: str = "",
        tgt_node_type: str = "",
    ) -> bool:
        src_node_type, edge_type, tgt_node_type = self._validate_edge_type(
            src_node_type, edge_type, tgt_node_type
        )
        return self._has_edge(
            src_node_id,
            tgt_node_id,
            src_node_type,
            edge_type,
            tgt_node_type,
        )

    def get_edge_data(
        self,
        src_node_id: str,
        tgt_node_id: str,
        src_node_type: str = "",
        edge_type: str = "",
        tgt_node_type: str = "",
    ) -> dict:
        src_node_type, edge_type, tgt_node_type = self._validate_edge_type(
            src_node_type, edge_type, tgt_node_type
        )
        return self._get_edge_data(
            src_node_id,
            tgt_node_id,
            src_node_type,
            edge_type,
            tgt_node_type,
        )

    # ------------------------------ Statistics Operations ------------------------------
    def degree(self, node_id: str, node_type: str = "", edge_types: List = []) -> int:
        node_type = self._validate_node_type(node_type)
        return self._degree(node_id, node_type, edge_types)

    def number_of_nodes(self, node_type: Optional[str] = None) -> int:
        if node_type:
            node_type = self._validate_node_type(node_type)
        return self._number_of_nodes(node_type)

    def number_of_edges(self, edge_type: Optional[str] = None) -> int:
        return self._number_of_edges(edge_type)

    # ------------------------------ Query Operations ------------------------------
    def get_nodes(
        self,
        node_type: str = "",
        filter_expression: Optional[str] = None,
        return_attributes: Optional[str | List[str]] = None,
        limit: Optional[int] = None,
    ) -> pd.DataFrame | None:
        node_type = self._validate_node_type(node_type)
        return self._get_nodes(
            node_type=node_type,
            filter_expression=filter_expression,
            return_attributes=return_attributes,
            limit=limit,
        )

    def get_neighbors(
        self,
        start_nodes: str | List[str],
        start_node_type: str = "",
        edge_types: Optional[str | List[str]] = None,
        target_node_types: Optional[str | List[str]] = None,
        filter_expression: Optional[str] = None,
        return_attributes: Optional[str | List[str]] = None,
        limit: Optional[int] = None,
    ) -> pd.DataFrame | None:
        start_node_type = self._validate_node_type(start_node_type)
        return self._get_neighbors(
            start_nodes=start_nodes,
            start_node_type=start_node_type,
            edge_types=edge_types,
            target_node_types=target_node_types,
            filter_expression=filter_expression,
            return_attributes=return_attributes,
            limit=limit,
        )

    # ------------------------------ Utilities ------------------------------
    def _validate_node_type(self, node_type: Optional[str]) -> str:
        """Validate and determine the effective node type."""
        if node_type:
            # Check if the specified node type is valid
            if node_type not in self.node_types:
                raise ValueError(
                    f"Invalid node type '{node_type}'. Must be one of {self.node_types}."
                )
            return node_type
        # Handle cases where node_type is not specified
        if len(self.node_types) == 0:
            raise ValueError("The graph has no node types defined.")
        if len(self.node_types) > 1:
            raise ValueError(
                "Multiple node types detected. Please specify a node type."
            )
        return next(iter(self.node_types))  # Return the single node type

    def _validate_edge_type(
        self,
        src_node_type: Optional[str],
        edge_type: Optional[str],
        tgt_node_type: Optional[str],
    ) -> tuple[str, str, str]:
        """Validate node types and edge type, and determine effective types."""
        # Validate source and target node types
        src_node_type = self._validate_node_type(src_node_type)
        tgt_node_type = self._validate_node_type(tgt_node_type)

        # Validate or determine edge type
        if edge_type:
            # Check if the specified edge type is valid
            if edge_type not in self.edge_types:
                raise ValueError(
                    f"Invalid edge type '{edge_type}'. Must be one of {self.edge_types}."
                )
        else:
            if len(self.edge_types) == 0:
                raise ValueError("The graph has no edge types defined.")
            if len(self.edge_types) > 1:
                raise ValueError(
                    "Multiple edge types detected. Please specify an edge type."
                )
            edge_type = next(iter(self.edge_types))  # Use the single edge type

        # Return effective types
        return src_node_type, edge_type, tgt_node_type
