import logging
from typing import Dict, List

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

    def search(
        self,
        data: List[float],
        vector_attribute_name: str,
        node_type: str,
        limit: int = 10,
    ) -> List[Dict]:
        try:
            query_name = f"api_vector_search_{node_type}_{vector_attribute_name}"
            params = f"k={limit}&"
            params += "&".join([f"query_vector={value}" for value in data])
            result = self._connection.runInstalledQuery(query_name, params)

            # Error check to ensure the result has the expected structure
            if not result:
                logger.error("Query result is empty or None.")
                return []

            if "map_node_distance" not in result[0]:
                logger.error("'map_node_distance' key is missing in the query result.")
                return []

            if "Nodes" not in result[1]:
                logger.error("'Nodes' key is missing in the query result.")
                return []

            # Extract map_node_distance and Nodes
            node_distances = result[0]["map_node_distance"]
            nodes = result[1]["Nodes"]

            # Error check: Ensure map_node_distance and Nodes are in the expected formats
            if not isinstance(node_distances, dict):
                logger.error("'map_node_distance' should be a dictionary.")
                return []

            if not isinstance(nodes, list):
                logger.error("'Nodes' should be a list.")
                return []

            # Combine Nodes and map_node_distance
            combined_result = []
            for node in nodes:
                node_id = node.get("v_id")  # Safely get node ID
                if not node_id:
                    logger.error("Node ID is missing in one of the nodes.")
                    continue

                # Get the distance for this node from the map_node_distance
                distance = node_distances.get(node_id, None)

                # Check if the distance was found for the node
                if distance is None:
                    logger.warning(f"No distance found for node {node_id}.")

                # Create a combined dict with node attributes and distance
                combined_node = {
                    "id": node_id,
                    "distance": distance,
                    **node.get("attributes", {}),  # Safely add node attributes
                }
                combined_result.append(combined_node)

            # Now combined_result will contain the combined data
            return combined_result
        except Exception as e:
            logger.error(
                f"Error performing vector search for vector attribute "
                f"{vector_attribute_name} of node type {node_type}: {e}"
            )
        return []
