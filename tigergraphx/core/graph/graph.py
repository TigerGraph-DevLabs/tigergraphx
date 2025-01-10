from typing import Any, Dict, List, Optional, Set, Tuple
from pathlib import Path
import pandas as pd

from .base_graph import BaseGraph

from tigergraphx.config import (
    GraphSchema,
    TigerGraphConnectionConfig,
)


class Graph(BaseGraph):
    """
    Represents a graph structure supporting both homogeneous and heterogeneous graphs.

    This class handles:

    - Undirected Homogeneous Graphs
    - Directed Homogeneous Graphs
    - Heterogeneous Graphs with multiple node and edge types
    """

    def __init__(
        self,
        graph_schema: GraphSchema | Dict | str | Path,
        tigergraph_connection_config: Optional[
            TigerGraphConnectionConfig | Dict | str | Path
        ] = None,
        drop_existing_graph: bool = False,
    ):
        """
        Initialize the Graph instance.

        Args:
            graph_schema (GraphSchema | Dict | str | Path): Graph schema.
            tigergraph_connection_config (optional, TigerGraphConnectionConfig | Dict | str | Path):
                TigerGraph connection configuration. Defaults to None.
            drop_existing_graph (bool, optional): Whether to drop the existing graph. Defaults to False.
        """
        super().__init__(
            graph_schema=graph_schema,
            tigergraph_connection_config=tigergraph_connection_config,
            drop_existing_graph=drop_existing_graph,
        )

    # ------------------------------ Node Operations ------------------------------
    def add_node(self, node_id: str, node_type: str = "", **attr) -> None:
        """
        Add a node to the graph.

        Args:
            node_id (str): The identifier of the node.
            node_type (str, optional): The type of the node. Defaults to "".
            **attr: Additional attributes for the node.
        """
        node_type = self._validate_node_type(node_type)
        self._add_node(node_id, node_type, **attr)

    def add_nodes_from(
        self,
        nodes_for_adding: List[str] | List[Tuple[str, Dict[str, Any]]],
        node_type: str = "",
        **attr,
    ):
        """
        Add nodes from the given list, with each node being either an ID or a tuple of ID and attributes.

        Args:
            nodes_for_adding: List of node IDs or tuples of node ID and attribute dictionaries.
            node_type: Type of the node (e.g., "MyNode").
            **attr: Common attributes to be added to all nodes.

        Returns:
            None if there was an error; otherwise, it calls `upsertVertices` on the connection.
        """
        node_type = self._validate_node_type(node_type)
        return self._add_nodes_from(nodes_for_adding, node_type, **attr)

    def remove_node(self, node_id: str, node_type: str = "") -> bool:
        """
        Remove a node from the graph.

        Args:
            node_id (str): The identifier of the node.
            node_type (str, optional): The type of the node. Defaults to "".

        Returns:
            bool: True if the node was removed, False otherwise.
        """
        node_type = self._validate_node_type(node_type)
        return self._remove_node(node_id, node_type)

    def has_node(self, node_id: str, node_type: str = "") -> bool:
        """
        Check if a node exists in the graph.

        Args:
            node_id (str): The identifier of the node.
            node_type (str, optional): The type of the node. Defaults to "".

        Returns:
            bool: True if the node exists, False otherwise.
        """
        node_type = self._validate_node_type(node_type)
        return self._has_node(node_id, node_type)

    def get_node_data(self, node_id: str, node_type: str = "") -> Dict | None:
        """
        Get data of a specific node.

        Args:
            node_id (str): The identifier of the node.
            node_type (str, optional): The type of the node. Defaults to "".

        Returns:
            Dict | None: The node data or None if not found.
        """
        node_type = self._validate_node_type(node_type)
        return self._get_node_data(node_id, node_type)

    def get_node_edges(
        self,
        node_id: str,
        node_type: str = "",
        edge_types: List | str = [],
        num_edge_samples: int = 1000,
    ) -> List:
        """
        Get edges connected to a specific node.

        Args:
            node_id (str): The identifier of the node.
            node_type (str, optional): The type of the node. Defaults to "".
            edge_types (List | str, optional): Types of edges to include. Defaults to [].
            num_edge_samples (int, optional): Number of edge samples to retrieve. Defaults to 1000.

        Returns:
            List: A list of edges.
        """
        node_type = self._validate_node_type(node_type)
        edges = self._get_node_edges(
            node_id,
            node_type,
            edge_types,
        )
        result = [(edge["from_id"], edge["to_id"]) for edge in edges]
        return result

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
        """
        Add an edge to the graph.

        Args:
            src_node_id (str): Source node identifier.
            tgt_node_id (str): Target node identifier.
            src_node_type (str, optional): Source node type. Defaults to "".
            edge_type (str, optional): Type of the edge. Defaults to "".
            tgt_node_type (str, optional): Target node type. Defaults to "".
            **attr (Dict[str, Any]): Additional attributes for the edge.
        """
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

    def add_edges_from(
        self,
        ebunch_to_add: List[Tuple[str, str]] | List[Tuple[str, str, Dict[str, Any]]],
        src_node_type: str,
        edge_type: str,
        tgt_node_type: str,
        **attr,
    ):
        """
        Adds edges to the graph from a list of edge tuples.

        Args:
            ebunch_to_add (List[Tuple[str, str]] | List[Tuple[str, str, Dict[str, Any]]]):
                List of edges to add, where each edge is a tuple of source and target node IDs,
                optionally with attributes.
            src_node_type (str): The source node type for the edges.
            edge_type (str): The type of the edge being added.
            tgt_node_type (str): The target node type for the edges.
            **attr: Additional attributes to add to all edges.

        Returns:
            The result of adding the edges to the graph.
        """
        src_node_type, edge_type, tgt_node_type = self._validate_edge_type(
            src_node_type, edge_type, tgt_node_type
        )
        return self._add_edges_from(
            ebunch_to_add, src_node_type, edge_type, tgt_node_type, **attr
        )

    def has_edge(
        self,
        src_node_id: str | int,
        tgt_node_id: str | int,
        src_node_type: str = "",
        edge_type: str = "",
        tgt_node_type: str = "",
    ) -> bool:
        """
        Check if an edge exists in the graph.

        Args:
            src_node_id (str | int): Source node identifier.
            tgt_node_id (str | int): Target node identifier.
            src_node_type (str, optional): Source node type. Defaults to "".
            edge_type (str, optional): Type of the edge. Defaults to "".
            tgt_node_type (str, optional): Target node type. Defaults to "".

        Returns:
            bool: True if the edge exists, False otherwise.
        """
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
    ) -> Dict | None:
        """
        Get data of a specific edge.

        Args:
            src_node_id (str): Source node identifier.
            tgt_node_id (str): Target node identifier.
            src_node_type (str, optional): Source node type. Defaults to "".
            edge_type (str, optional): Type of the edge. Defaults to "".
            tgt_node_type (str, optional): Target node type. Defaults to "".

        Returns:
            Dict | None: The edge data or None if not found.
        """
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
        """
        Get the degree of a node.

        Args:
            node_id (str): The identifier of the node.
            node_type (str, optional): The type of the node. Defaults to "".
            edge_types (List, optional): Types of edges to consider. Defaults to [].

        Returns:
            int: The degree of the node.
        """
        node_type = self._validate_node_type(node_type)
        return self._degree(node_id, node_type, edge_types)

    def number_of_nodes(self, node_type: Optional[str] = None) -> int:
        """
        Get the number of nodes in the graph.

        Args:
            node_type (Optional[str], optional): The type of nodes to count. Defaults to None.

        Returns:
            int: The number of nodes.
        """
        if node_type:
            node_type = self._validate_node_type(node_type)
        return self._number_of_nodes(node_type)

    def number_of_edges(self, edge_type: Optional[str] = None) -> int:
        """
        Get the number of edges in the graph.

        Args:
            edge_type (Optional[str], optional): The type of edges to count. Defaults to None.

        Returns:
            int: The number of edges.
        """
        return self._number_of_edges(edge_type)

    # ------------------------------ Query Operations ------------------------------
    def get_nodes(
        self,
        node_type: str = "",
        filter_expression: Optional[str] = None,
        return_attributes: Optional[str | List[str]] = None,
        limit: Optional[int] = None,
    ) -> pd.DataFrame | None:
        """
        Retrieve nodes from the graph.

        Args:
            node_type (str, optional): The type of nodes to retrieve. Defaults to "".
            filter_expression (Optional[str], optional): Filter expression. Defaults to None.
            return_attributes (Optional[str | List[str]], optional): Attributes to return. Defaults to None.
            limit (Optional[int], optional): Limit the number of results. Defaults to None.

        Returns:
            pd.DataFrame | None: DataFrame of nodes or None.
        """
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
        """
        Get neighbors of specified nodes.

        Args:
            start_nodes (str | List[str]): Starting node(s).
            start_node_type (str, optional): Type of starting nodes. Defaults to "".
            edge_types (Optional[str | List[str]], optional): Types of edges to consider. Defaults to None.
            target_node_types (Optional[str | List[str]], optional): Types of target nodes. Defaults to None.
            filter_expression (Optional[str], optional): Filter expression. Defaults to None.
            return_attributes (Optional[str | List[str]], optional): Attributes to return. Defaults to None.
            limit (Optional[int], optional): Maximum number of neighbors to retrieve. Defaults to None.

        Returns:
            pd.DataFrame | None: DataFrame of neighbors or None.
        """
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

    # ------------------------------ Vector Operations ------------------------------
    def upsert(
        self,
        data: Dict | List[Dict],
        node_type: str = "",
    ):
        """
        Upsert nodes to the specified node type in the graph.
        If data is a Dict, it processes one record, otherwise if it's a List, it processes multiple records.

        Args:
            data (Dict | List[Dict]): Data to be upserted, can either be a single record (Dict)
                or multiple records (List[Dict]).
            node_type (str): The node type for the upsert operation.

        Returns:
            The result of the upsert operation or None if an error occurs.
        """
        node_type = self._validate_node_type(node_type)
        return self._upsert(data, node_type)

    def fetch_node(
        self, node_id: str, vector_attribute_name: str, node_type: str = ""
    ) -> Optional[List[float]]:
        """
        Fetch the embedding for a single node by its ID and type.

        Args:
            node_id (str): The ID of the node to fetch.
            vector_attribute_name (str): Name of the vector attribute to retrieve.
            node_type (str, optional): The type of the node. Defaults to "".

        Returns:
            Optional[List[float]]: The embedding vector for the node, or None if not found.
        """
        node_type = self._validate_node_type(node_type)
        return self._fetch_node(node_id, vector_attribute_name, node_type)

    def fetch_nodes(
        self, node_ids: List[str], vector_attribute_name: str, node_type: str = ""
    ) -> Dict[str, List[float]]:
        """
        Fetch embeddings for multiple nodes by their IDs and type.

        Args:
            node_ids (List[str]): List of node IDs to fetch.
            vector_attribute_name (str): Name of the vector attribute to retrieve.
            node_type (str, optional): Type of the nodes. Defaults to "".

        Returns:
            Dict[str, List[float]]: A dictionary where keys are node IDs and values are embedding vectors.
        """
        node_type = self._validate_node_type(node_type)
        return self._fetch_nodes(node_ids, vector_attribute_name, node_type)

    def search(
        self,
        data: List[float],
        vector_attribute_name: str,
        node_type: str = "",
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
            node_type (str, optional): The node type to search. Defaults to "".
            limit (int, optional): The number of nearest neighbors to return. Defaults to 10.
            return_attributes (Optional[str | List[str]], optional): The attributes of the node to
                return. Defaults to None.
            candidate_ids (Optional[Set[str]], optional): A set of node IDs to limit the search to.
                Defaults to None.

        Returns:
            List[Dict]: A list of dictionaries containing the node IDs, distances, and attributes, ordered by distance.
        """
        node_type = self._validate_node_type(node_type)
        return self._search(
            data=data,
            vector_attribute_name=vector_attribute_name,
            node_type=node_type,
            limit=limit,
            return_attributes=return_attributes,
            candidate_ids=candidate_ids,
        )

    def search_multi_vector_attributes(
        self,
        data: List[float],
        vector_attribute_names: List[str],
        node_types: Optional[List[str]] = None,
        limit: int = 10,
        return_attributes_list: Optional[List[List[str]]] = None,
    ) -> List[Dict]:
        """
        Perform a vector search to find the most similar nodes based on multiple query vectors for
            specified node types and vector attributes.

        Args:
            data (List[float]): The query vector to use for the search.
            vector_attribute_names (List[str]): List of vector attribute names to search against.
            node_types (Optional[List[str]], optional): List of node types corresponding to the
                vector attributes. Defaults to None.
            limit (int, optional): The number of nearest neighbors to return. Defaults to 10.
            return_attributes_list (Optional[List[List[str]]], optional): A list of lists
                specifying which attributes to return for each node type.

        Returns:
            List[Dict]: A list of dictionaries containing the node IDs, distances, and attributes,
                ordered by distance.
        """
        new_node_types = []
        if node_types is not None:
            for node_type in node_types:
                new_node_type = self._validate_node_type(node_type)
                new_node_types.append(new_node_type)
        elif len(self.node_types) == 1:
            new_node_types = [next(iter(self.node_types))] * len(vector_attribute_names)
        else:
            raise ValueError("Invalid input: node_types must be provided.")
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
        node_type: str = "",
        limit: int = 5,
        return_attributes: Optional[List[str]] = None,
    ) -> List[Dict]:
        """Retrieve the top-k similar nodes based on a source node's embedding.

        Args:
            node_id (str): The ID of the source node.
            vector_attribute_name (str): The name of the embedding attribute to use.
            node_type (str, optional): The type of nodes to search within. Defaults to "".
            limit (int, optional): The number of similar nodes to retrieve. Defaults to 5.
            return_attributes (Optional[List[str]], optional): Attributes to return for each node.
                Defaults to None.

        Returns:
            List[Dict]: A list of dictionaries containing the top-k similar nodes.
        """
        node_type = self._validate_node_type(node_type)
        return self._search_top_k_similar_nodes(
            node_id=node_id,
            vector_attribute_name=vector_attribute_name,
            node_type=node_type,
            limit=limit,
            return_attributes=return_attributes,
        )

    # ------------------------------ Utilities ------------------------------
    def _validate_node_type(self, node_type: Optional[str]) -> str:
        """
        Validate and determine the effective node type.

        Args:
            node_type (Optional[str]): The node type to validate.

        Returns:
            str: The validated node type.

        Raises:
            ValueError: If the node type is invalid or not specified correctly.
        """
        if node_type:
            if node_type not in self.node_types:
                raise ValueError(
                    f"Invalid node type '{node_type}'. Must be one of {self.node_types}."
                )
            return node_type
        if len(self.node_types) == 0:
            raise ValueError("The graph has no node types defined.")
        if len(self.node_types) > 1:
            raise ValueError(
                "Multiple node types detected. Please specify a node type."
            )
        return next(iter(self.node_types))

    def _validate_edge_type(
        self,
        src_node_type: Optional[str],
        edge_type: Optional[str],
        tgt_node_type: Optional[str],
    ) -> tuple[str, str, str]:
        """
        Validate node types and edge type, and determine effective types.

        Args:
            src_node_type (Optional[str]): Source node type.
            edge_type (Optional[str]): Edge type.
            tgt_node_type (Optional[str]): Target node type.

        Returns:
            tuple[str, str, str]: Validated source node type, edge type, and target node type.

        Raises:
            ValueError: If the edge type is invalid or not specified correctly.
        """
        src_node_type = self._validate_node_type(src_node_type)
        tgt_node_type = self._validate_node_type(tgt_node_type)

        if edge_type:
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
            edge_type = next(iter(self.edge_types))

        return src_node_type, edge_type, tgt_node_type
