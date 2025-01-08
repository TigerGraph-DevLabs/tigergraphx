from typing import Any, Dict, List, Optional, Set, Tuple
from pathlib import Path
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
        tigergraph_connection_config: Optional[
            TigerGraphConnectionConfig | Dict | str | Path
        ] = None,
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
        nodes_for_adding: List[str] | List[Tuple[str, Dict[str, Any]]],
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
        )
        result = [(edge["from_id"], edge["to_id"]) for edge in edges]
        return result

    # ------------------------------ Edge Operations ------------------------------
    def add_edge(self, src_node_id: str, tgt_node_id: str, **attr) -> None:
        """
        Add an edge to the graph.

        Args:
            src_node_id (str): Source node identifier.
            tgt_node_id (str): Target node identifier.
            **attr: Additional attributes for the edge.
        """
        self._add_edge(
            src_node_id,
            tgt_node_id,
            self.node_type,
            self.edge_type,
            self.node_type,
            **attr,
        )

    def add_edges_from(
        self,
        ebunch_to_add: List[Tuple[str, str]] | List[Tuple[str, str, Dict[str, Any]]],
        **attr,
    ):
        """
        Adds edges to the graph from a list of edge tuples.

        Args:
            ebunch_to_add (List[Tuple[str, str]] | List[Tuple[str, str, Dict[str, Any]]]):
                List of edges to add, where each edge is a tuple of source and target node IDs,
                optionally with attributes.
            **attr: Additional attributes to add to all edges.

        Returns:
            The result of adding the edges to the graph.
        """
        return self._add_edges_from(
            ebunch_to_add, self.node_type, self.edge_type, self.node_type, **attr
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
    def upsert(
        self,
        data: Dict | List[Dict],
    ):
        """
        Upsert nodes the graph.
        If data is a Dict, it processes one record, otherwise if it's a List, it processes multiple records.

        Args:
            data (Dict | List[Dict]): Data to be upserted, can either be a single record (Dict)
                or multiple records (List[Dict]).

        Returns:
            The result of the upsert operation or None if an error occurs.
        """
        return self._upsert(data, self.node_type)

    def fetch(self, node_id: str, node_type: str) -> Optional[Dict[str, List[float]]]:
        """
        Retrieve the node with vector attributes by ID and type.

        Args:
            node_id (str): The ID of the node to fetch.

        Returns:
            Optional[Dict[str, List[float]]]: A dictionary containing the node embeddings,
                or None if not found.
        """
        return self._fetch(node_id, node_type)

    def search(
        self,
        data: List[float],
        vector_attribute_name: str,
        limit: int = 10,
        return_attributes: Optional[str | List[str]] = None,
        candidate_ids: Optional[Set[str]] = None,
    ) -> List[Dict]:
        """
        Perform a vector search to find the most similar nodes based on a query vector for a
            single vector attribute and node type.

        Args:
            data (List[float]): The query vector to use for the search.
            vector_attribute_name (str): The vector attribute name to search against.
            limit (int, optional): The number of nearest neighbors to return. Defaults to 10.
            return_attributes (Optional[str | List[str]], optional): The attributes of the node to
                return. Defaults to None.
            candidate_ids (Optional[Set[str]], optional): A set of node IDs to limit the search to.
                Defaults to None.

        Returns:
            List[Dict]: A list of dictionaries containing the node IDs, distances, and attributes, ordered by distance.
        """
        return self._search(
            data=data,
            vector_attribute_name=vector_attribute_name,
            node_type=self.node_type,
            limit=limit,
            return_attributes=return_attributes,
            candidate_ids=candidate_ids,
        )

    def search_multi_vector_attributes(
        self,
        data: List[float],
        vector_attribute_names: List[str],
        limit: int = 10,
        return_attributes_list: Optional[List[List[str]]] = None,
    ) -> List[Dict]:
        """
        Perform a vector search to find the most similar nodes based on multiple query vectors for
            specified node types and vector attributes.

        Args:
            data (List[float]): The query vector to use for the search.
            vector_attribute_names (List[str]): List of vector attribute names to search against.
            limit (int, optional): The number of nearest neighbors to return. Defaults to 10.
            return_attributes_list (Optional[List[List[str]]], optional): A list of lists
                specifying which attributes to return for each node type.

        Returns:
            List[Dict]: A list of dictionaries containing the node IDs, distances, and attributes,
                ordered by distance.
        """
        new_node_types = []
        new_node_types = [self.node_type] * len(vector_attribute_names)
        return self._search_multi_vector_attributes(
            data=data,
            vector_attribute_names=vector_attribute_names,
            node_types=new_node_types,
            limit=limit,
            return_attributes_list=return_attributes_list,
        )

    def search_top_k_similar_nodes(
        self,
        node_id: str,
        vector_attribute_name: str,
        limit: int = 5,
        return_attributes: Optional[List[str]] = None,
    ) -> List[Dict]:
        """Retrieve the top-k similar nodes based on a source node's embedding.

        Args:
            node_id (str): The ID of the source node.
            vector_attribute_name (str): The name of the embedding attribute to use.
            limit (int, optional): The number of similar nodes to retrieve. Defaults to 5.
            return_attributes (Optional[List[str]], optional): Attributes to return for each node.
                Defaults to None.

        Returns:
            List[Dict]: A list of dictionaries containing the top-k similar nodes.
        """
        return self._search_top_k_similar_nodes(
            node_id=node_id,
            vector_attribute_name=vector_attribute_name,
            node_type=self.node_type,
            limit=limit,
            return_attributes=return_attributes,
        )
