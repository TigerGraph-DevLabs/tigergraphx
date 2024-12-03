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

    def degree(self, node_id: str, node_type: str = "", edge_types: List = []) -> int:
        node_type = self._validate_node_type(node_type)
        return self._degree(node_id, node_type, edge_types)

    def get_nodes(
        self,
        node_type: str,
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

    def _validate_node_type(self, node_type: str) -> str:
        """Validate and determine the effective node type.

        Args:
            node_type (str): The node type provided by the user.

        Returns:
            str: The effective node type to be used.

        Raises:
            ValueError: If both node_type and self.node_type are empty.
        """
        if not node_type and not self.node_type:
            raise ValueError(
                "Please specify a node type, as the graph has multiple node types."
            )
        return node_type if node_type else self.node_type

    def _validate_edge_type(
        self, src_node_type: str = "", edge_type: str = "", tgt_node_type: str = ""
    ):
        """Validate node types and edge type, and determine effective types.

        Args:
            src_node_type (str): The source node type.
            tgt_node_type (str): The target node type.
            edge_type (str): The edge type.

        Returns:
            Tuple[str, str, str]: Effective source node type, effective target node type, and edge type.

        Raises:
            ValueError: If both source and target node types are not specified, or if the edge type is not specified.
        """
        # Check for node type of the source node
        if not src_node_type and not self.node_type:
            raise ValueError(
                "Please specify a node type for the source node, as the graph has multiple node types."
            )

        # Check for edge type
        if not edge_type and not self._context.edge_type:
            raise ValueError(
                "Please specify an edge type, as the graph has multiple edge types."
            )

        # Check for node type of the target node
        if not tgt_node_type and not self.node_type:
            raise ValueError(
                "Please specify a node type for the target node, as the graph has multiple node types."
            )

        # Determine and return effective types
        return (
            src_node_type if src_node_type else self.node_type,
            edge_type if edge_type else self._context.edge_type,
            tgt_node_type if tgt_node_type else self.node_type,
        )
