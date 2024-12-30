from typing import Dict, List
from pathlib import Path
import logging
import pandas as pd

from .base_vector_db import BaseVectorDB

from tigergraphx.config import TigerVectorConfig
from tigergraphx.core import Graph

logger = logging.getLogger(__name__)


class TigerVectorManager(BaseVectorDB):
    """Manages vector database operations for TigerGraph."""

    config: TigerVectorConfig

    def __init__(self, config: TigerVectorConfig | Dict | str | Path, graph: Graph):
        """
        Initialize the TigerVectorManager.

        Args:
            config (TigerVectorConfig | Dict | str | Path): Configuration for the vector
                database connection, either as a config object, dictionary, string, or path
                to configuration file.
        """
        config = TigerVectorConfig.ensure_config(config)
        super().__init__(config)
        self._graph = graph

    def insert_data(self, data: pd.DataFrame) -> None:
        """
        Insert data into TigerGraph

        Args:
            data (pd.DataFrame): Data to be inserted.
        """
        nodes_for_adding = []
        for _, row in data.iterrows():
            # Create a dictionary for node attributes
            node_attributes = {
                self.config.vector_attribute_name: row["__vector__"],
            }

            # Add the node ID as the first element in the tuple
            nodes_for_adding.append((row["__id__"], node_attributes))

        # Call the add_nodes_from method to add nodes to the graph
        if len(nodes_for_adding) > 0:
            self._graph.add_nodes_from(
                nodes_for_adding=nodes_for_adding, node_type="Entity"
            )

    def query(self, query_embedding: List[float], k: int = 10) -> List[str]:
        """
        Perform k-NN search on the vector database.

        Args:
            query_embedding (List[float]): The query embedding vector.
            k (int): The number of nearest neighbors to return.

        Returns:
            List[str]: List of identifiers for the nearest neighbors.
        """
        # Perform the vector search using the vector_search method
        search_results = self._graph.vector_search(
            query_vector=query_embedding,
            vector_attribute_name=self.config.vector_attribute_name,
            k=k,
        )

        # Extract the node identifiers (keys of the search result dictionary)
        nearest_neighbors = list(search_results.keys())

        return nearest_neighbors
