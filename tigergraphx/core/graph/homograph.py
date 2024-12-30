from typing import Any, Dict, List, Optional, Tuple
import pandas as pd

from .base_graph import BaseGraph

from tigergraphx.config import (
    NodeSchema,
    EdgeSchema,
    GraphSchema,
    TigerGraphConnectionConfig,
)


class HomoGraph(BaseGraph):
    """
    Represents a homogeneous graph with a single node and edge type.
    """

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
        """
        Initialize a HomoGraph instance.

        Args:
            graph_name (str): The name of the graph.
            node_type (str): The type of nodes in the graph.
            node_schema (NodeSchema): The schema for the nodes.
            edge_type (str): The type of edges in the graph.
            edge_schema (EdgeSchema): The schema for the edges.
            tigergraph_connection_config (Optional[TigerGraphConnectionConfig], optional): Configuration for TigerGraph connection. Defaults to None.
            drop_existing_graph (bool, optional): Whether to drop the existing graph if it exists. Defaults to False.
        """
        if not node_type:
            raise ValueError("node_type cannot be an empty string.")
        if not edge_type:
            raise ValueError("edge_type cannot be an empty string.")
        graph_schema = GraphSchema(
            graph_name=graph_name,
            nodes={node_type: node_schema},
            edges={edge_type: edge_schema},
        )
        super().__init__(
            graph_schema=graph_schema,
            tigergraph_connection_config=tigergraph_connection_config,
            drop_existing_graph=drop_existing_graph,
        )

    # ------------------------------ Node Operations ------------------------------
    def add_node(self, node_id: str, **attr) -> None:
        """
        Add a node to the graph.

        Args:
            node_id (str): The identifier of the node.
            **attr (Dict[str, Any]): Additional attributes for the node.
        """
        self._add_node(node_id, self.node_type, **attr)

    def add_nodes_from(
        self,
        nodes_for_adding: List[str | Tuple[str, Dict[str, Any]]],
        **attr,
    ):
        """
        Add nodes from the given list, with each node being either an ID or a tuple of ID and attributes.

        Args:
            nodes_for_adding: List of node IDs or tuples of node ID and attribute dictionaries.
            **attr: Common attributes to be added to all nodes.

        Returns:
            None if there was an error; otherwise, it calls `upsertVertices` on the connection.
        """
        return self._add_nodes_from(nodes_for_adding, self.node_type, **attr)

    def remove_node(self, node_id: str) -> bool:
        """
        Remove a node from the graph.

        Args:
            node_id (str): The identifier of the node.

        Returns:
            bool: True if the node was removed, False otherwise.
        """
        return self._remove_node(node_id, self.node_type)

    def has_node(self, node_id: str) -> bool:
        """
        Check if a node exists in the graph.

        Args:
            node_id (str): The identifier of the node.

        Returns:
            bool: True if the node exists, False otherwise.
        """
        return self._has_node(node_id, self.node_type)

    def get_node_data(self, node_id: str) -> Dict | None:
        """
        Retrieve data of a specific node.

        Args:
            node_id (str): The identifier of the node.

        Returns:
            Dict | None: The node data or None if not found.
        """
        return self._get_node_data(node_id, self.node_type)

    def get_node_edges(
        self,
        node_id: str,
        num_edge_samples: int = 1000,
    ) -> List:
        """
        Get edges connected to a specific node.

        Args:
            node_id (str): The identifier of the node.
            num_edge_samples (int, optional): Number of edge samples to retrieve. Defaults to 1000.

        Returns:
            List: A list of edges as tuples.
        """
        edges = self._get_node_edges(
            node_id,
            self.node_type,
            self.edge_type,
            num_edge_samples,
        )
        result = [(edge["from_id"], edge["to_id"]) for edge in edges]
        return result

    # ------------------------------ Edge Operations ------------------------------
    def add_edge(
        self, src_node_id: str, tgt_node_id: str, **attr
    ) -> None:
        """
        Add an edge to the graph.

        Args:
            src_node_id (str): Source node identifier.
            tgt_node_id (str): Target node identifier.
            **attr (Dict[str, Any]): Additional attributes for the edge.
        """
        self._add_edge(
            src_node_id,
            tgt_node_id,
            self.node_type,
            self.edge_type,
            self.node_type,
            **attr,
        )

    def has_edge(self, src_node_id: str | int, tgt_node_id: str | int) -> bool:
        """
        Check if an edge exists in the graph.

        Args:
            src_node_id (str | int): Source node identifier.
            tgt_node_id (str | int): Target node identifier.

        Returns:
            bool: True if the edge exists, False otherwise.
        """
        return self._has_edge(
            src_node_id, tgt_node_id, self.node_type, self.edge_type, self.node_type
        )

    def get_edge_data(self, src_node_id: str, tgt_node_id: str) -> Dict | None:
        """
        Retrieve data of a specific edge.

        Args:
            src_node_id (str): Source node identifier.
            tgt_node_id (str): Target node identifier.

        Returns:
            Dict | None: The edge data or None if not found.
        """
        return self._get_edge_data(
            src_node_id, tgt_node_id, self.node_type, self.edge_type, self.node_type
        )

    # ------------------------------ Statistics Operations ------------------------------
    def degree(self, node_id: str) -> int:
        """
        Get the degree of a node.

        Args:
            node_id (str): The identifier of the node.

        Returns:
            int: The degree of the node.
        """
        return self._degree(node_id, self.node_type, self.edge_type)

    def number_of_nodes(self) -> int:
        """
        Get the total number of nodes in the graph.

        Returns:
            int: The number of nodes.
        """
        return self._number_of_nodes()

    def number_of_edges(self) -> int:
        """
        Get the total number of edges in the graph.

        Returns:
            int: The number of edges.
        """
        return self._number_of_edges()

    # ------------------------------ Query Operations ------------------------------
    def get_nodes(
        self,
        filter_expression: Optional[str] = None,
        return_attributes: Optional[str | List[str]] = None,
        limit: Optional[int] = None,
    ) -> pd.DataFrame | None:
        """
        Retrieve nodes from the graph.

        Args:
            filter_expression (Optional[str], optional): Filter expression to apply. Defaults to None.
            return_attributes (Optional[str | List[str]], optional): Attributes to return. Defaults to None.
            limit (Optional[int], optional): Maximum number of nodes to retrieve. Defaults to None.

        Returns:
            pd.DataFrame | None: DataFrame of nodes or None.
        """
        return self._get_nodes(
            node_type=self.node_type,
            filter_expression=filter_expression,
            return_attributes=return_attributes,
            limit=limit,
        )

    def get_neighbors(
        self,
        start_nodes: str | List[str],
        edge_types: Optional[str | List[str]] = None,
        target_node_types: Optional[str | List[str]] = None,
        filter_expression: Optional[str] = None,
        return_attributes: Optional[str | List[str]] = None,
        limit: Optional[int] = None,
    ) -> pd.DataFrame | None:
        """
        Get neighbors of specified nodes.

        Args:
            start_nodes (str | List[str]): Starting node(s).
            edge_types (Optional[str | List[str]], optional): Types of edges to consider. Defaults to None.
            target_node_types (Optional[str | List[str]], optional): Types of target nodes. Defaults to None.
            filter_expression (Optional[str], optional): Filter expression to apply. Defaults to None.
            return_attributes (Optional[str | List[str]], optional): Attributes to return. Defaults to None.
            limit (Optional[int], optional): Maximum number of neighbors to retrieve. Defaults to None.

        Returns:
            pd.DataFrame | None: DataFrame of neighbors or None.
        """
        return self._get_neighbors(
            start_nodes=start_nodes,
            start_node_type=self.node_type,
            edge_types=edge_types,
            target_node_types=target_node_types,
            filter_expression=filter_expression,
            return_attributes=return_attributes,
            limit=limit,
        )

    # ------------------------------ Vector Operations ------------------------------
    def vector_search(
        self,
        query_vector: List[float],
        vector_attribute_name: str,
        k: int = 10,
    ) -> Dict[str, float]:
        """
        Perform a vector search to find the nearest nodes based on a query vector.

        Args:
            vector_attribute_name (str): The name of the vector attribute to search against.
            query_vector (List[float]): The query vector to use for the search.
            k (int, optional): The number of nearest neighbors to return. Defaults to 10.

        Returns:
            Dict[str, float]: A dictionary where keys are node names and values are the distances
            from the query vector to each node.
        """
        return self._vector_search(
            vector_attribute_name=vector_attribute_name,
            query_vector=query_vector,
            node_type=self.node_type,
            k=k,
        )
