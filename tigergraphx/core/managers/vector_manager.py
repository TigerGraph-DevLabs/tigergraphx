# Copyright 2025 TigerGraph Inc.
# Licensed under the Apache License, Version 2.0.
# See the LICENSE file or https://www.apache.org/licenses/LICENSE-2.0
#
# Permission is granted to use, copy, modify, and distribute this software
# under the License. The software is provided "AS IS", without warranty.

import logging
from typing import Dict, List, Optional, Set

from .base_manager import BaseManager

from tigergraphx.core.graph_context import GraphContext


logger = logging.getLogger(__name__)


class VectorManager(BaseManager):
    def __init__(self, context: GraphContext):
        super().__init__(context)

    def upsert(
        self,
        data: Dict | List[Dict],
        node_type: str,
    ):
        nodes_to_upsert = []
        node_schema = self._graph_schema.nodes.get(node_type)

        if not node_schema:
            logger.error(f"Node type '{node_type}' does not exist in the graph schema.")
            return None

        # Ensure primary key is available in the schema
        primary_key = node_schema.primary_key

        # Check if data is a dictionary (single record)
        if isinstance(data, dict):
            node_id = data.get(primary_key)
            if not node_id:
                logger.error(
                    f"Primary key '{primary_key}' is missing in the node data: {data}"
                )
                return None

            # Separate node data from the primary key
            node_data = {
                key: value for key, value in data.items() if key != primary_key
            }
            nodes_to_upsert.append((node_id, node_data))

        # Check if data is a list of dictionaries (multiple records)
        else:
            for record in data:
                if not isinstance(record, dict):
                    logger.error(
                        f"Invalid record format: {record}. Expected a dictionary."
                    )
                    return None

                node_id = record.get(primary_key)
                if not node_id:
                    logger.error(
                        f"Primary key '{primary_key}' is missing in the node data: {record}"
                    )
                    return None

                # Separate node data from the primary key
                node_data = {
                    key: value for key, value in record.items() if key != primary_key
                }
                nodes_to_upsert.append((node_id, node_data))

        # Attempt to upsert the nodes into the graph
        try:
            result = self._connection.upsertVertices(
                vertexType=node_type, vertices=nodes_to_upsert
            )
            return result
        except Exception as e:
            logger.error(f"Error adding nodes: {e}")
            return None

    def fetch_node(
        self, node_id: str, vector_attribute_name: str, node_type: str
    ) -> Optional[List[float]]:
        """
        Retrieve the embedding vector of a single node by its ID and type.
        """
        result = self.fetch_nodes([node_id], vector_attribute_name, node_type)
        return result.get(node_id)

    def fetch_nodes(
        self, node_ids: List[str], vector_attribute_name: str, node_type: str
    ) -> Dict[str, List[float]]:
        """
        Retrieve the embedding vectors of multiple nodes by their IDs and type.
        """
        try:
            params = {"input": [(node_id, node_type) for node_id in node_ids]}
            result = self._connection.runInstalledQuery("api_fetch", params)

            if not result or not isinstance(result, list):
                logger.error("Query result is empty or invalid.")
                return {}

            # Process result
            nodes = result[0].get("Nodes", [])
            if not nodes:
                logger.warning("No nodes found in the query result.")
                return {}

            embeddings = {}
            for node in nodes:
                node_id = node.get("v_id")
                node_embeddings = node.get("Embeddings", {})
                if vector_attribute_name not in node_embeddings:
                    logger.warning(
                        f"'{vector_attribute_name}' not found for node_id: '{node_id}'."
                    )
                    continue

                emb_vector = node_embeddings[vector_attribute_name]
                if isinstance(emb_vector, list) and all(
                    isinstance(x, float) for x in emb_vector
                ):
                    embeddings[node_id] = emb_vector
                else:
                    logger.warning(
                        f"Invalid embedding format for node_id: '{node_id}'. Expected a list of floats."
                    )

            return embeddings

        except Exception as e:
            logger.error(f"Error during fetch_nodes operation: {str(e)}")
            return {}

    def search(
        self,
        data: List[float],
        vector_attribute_name: str,
        node_type: str,
        limit: int = 10,
        return_attributes: Optional[str | List[str]] = None,
        candidate_ids: Optional[Set[str]] = None,
    ) -> List[Dict]:
        try:
            query_name = f"api_search_{node_type}_{vector_attribute_name}"
            set_candidate = []
            if candidate_ids:
                set_candidate = [
                    {"id": candidate_id, "type": node_type}
                    for candidate_id in candidate_ids
                ]
            params = {"k": limit, "query_vector": data, "set_candidate": set_candidate}

            result = self._execute_search_query(query_name, params)
            if result is None:
                return []

            combined_result = self._process_search_results(result, return_attributes)
            return combined_result
        except Exception as e:
            logger.error(
                f"Error performing vector search for vector attribute "
                f"{vector_attribute_name} of node type {node_type}: {e}"
            )
            return []

    def search_multi_vector_attributes(
        self,
        data: List[float],
        vector_attribute_names: List[str],
        node_types: List[str],
        limit: int = 10,
        return_attributes_list: Optional[List[List[str]]] = None,
    ) -> List[Dict]:
        if len(vector_attribute_names) != len(node_types):
            logger.error(
                "The number of vector_attribute_names must be equal to the number of node_types."
            )
            return []

        combined_results = []

        if return_attributes_list and len(return_attributes_list) != len(
            vector_attribute_names
        ):
            logger.error(
                "The number of return_attributes_list must match the number of vector_attribute_names."
            )
            return []

        for idx, (vector_attribute_name, node_type) in enumerate(
            zip(vector_attribute_names, node_types)
        ):
            return_attributes = (
                return_attributes_list[idx] if return_attributes_list else None
            )
            result = self.search(
                data=data,
                vector_attribute_name=vector_attribute_name,
                node_type=node_type,
                limit=limit,
                return_attributes=return_attributes,
            )
            combined_results.extend(result)

        # Sort by distance
        combined_results.sort(key=lambda x: x["distance"])

        # Keep only the first occurrence of each unique node_id
        unique_results = []
        seen_node_ids = set()

        for item in combined_results:
            node_id = item.get("id")
            if node_id not in seen_node_ids:
                unique_results.append(item)
                seen_node_ids.add(node_id)
            if len(unique_results) >= limit:
                break

        return unique_results

    def search_top_k_similar_nodes(
        self,
        node_id: str,
        vector_attribute_name: str,
        node_type: str = "",
        limit: int = 5,
        return_attributes: Optional[List[str]] = None,
    ) -> List[Dict]:
        """
        Retrieve the top-k similar nodes based on a source node's specified embedding.
        """
        query_vector = self.fetch_node(node_id, vector_attribute_name, node_type)
        if not query_vector:
            logger.error(
                f"Embedding '{vector_attribute_name}' not found for node_id: '{node_id}', "
                f"node_type: '{node_type}'."
            )
            return []

        results = self.search(
            data=query_vector,
            vector_attribute_name=vector_attribute_name,
            node_type=node_type,
            limit=limit + 1,
            return_attributes=return_attributes,
        )

        filtered_results = [result for result in results if result.get("id") != node_id]
        return filtered_results[:limit]

    def _execute_search_query(
        self,
        query_name: str,
        params: Dict,
    ) -> Optional[List[Dict]]:
        """
        Executes the search query and performs initial error checks.
        """
        try:
            result = self._connection.runInstalledQuery(
                query_name, params, usePost=True
            )
        except Exception as e:
            logger.error(f"Error executing query {query_name}: {e}")
            return None

        # Perform basic error checks
        if not result:
            logger.error("Query result is empty or None.")
            return None

        if "map_node_distance" not in result[0]:
            logger.error("'map_node_distance' key is missing in the query result.")
            return None

        if "Nodes" not in result[1]:
            logger.error("'Nodes' key is missing in the query result.")
            return None

        return result

    def _process_search_results(
        self,
        result: List[Dict],
        return_attributes: Optional[str | List[str]] = None,
    ) -> List[Dict]:
        """
        Processes the raw search results into a combined and formatted list.
        """
        node_distances = result[0]["map_node_distance"]
        nodes = result[1]["Nodes"]

        # Validate result formats
        if not isinstance(node_distances, dict):
            logger.error("'map_node_distance' should be a dictionary.")
            return []

        if not isinstance(nodes, list):
            logger.error("'Nodes' should be a list.")
            return []

        combined_result = []
        for node in nodes:
            node_id = node.get("v_id")
            if not node_id:
                logger.error("Node ID is missing in one of the nodes.")
                continue

            distance = node_distances.get(node_id)
            if distance is None:
                logger.warning(f"No distance found for node {node_id}.")

            # Handle return_attributes logic
            if return_attributes is not None:
                if isinstance(return_attributes, str):
                    return_attributes = [return_attributes]
                if not return_attributes:
                    node_data = {}
                else:
                    node_data = {
                        key: value
                        for key, value in node.get("attributes", {}).items()
                        if key in return_attributes
                    }
            else:
                node_data = node.get("attributes", {})

            combined_node = {
                "id": node_id,
                "distance": distance,
                **node_data,
            }
            combined_result.append(combined_node)

        return combined_result
