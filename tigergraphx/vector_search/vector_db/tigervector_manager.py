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
        Initialize TigerVectorManager.

        Args:
            config: Config for the vector database connection, given as a config 
                object, dictionary, string, or path to a configuration file.
            graph: Graph instance for managing nodes.
        """
        config = TigerVectorConfig.ensure_config(config)
        super().__init__(config)
        self._graph = graph

    def insert_data(self, data: pd.DataFrame) -> None:
        """
        Insert data into TigerGraph.

        Args:
            data: DataFrame containing data to be inserted.
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
                nodes_for_adding=nodes_for_adding, node_type=self.config.node_type
            )

    def query(self, query_embedding: List[float], k: int = 10) -> List[str]:
        """
        Perform k-NN search on the vector database.

        Args:
            query_embedding: The query embedding vector.
            k: The number of nearest neighbors to return.

        Returns:
            List of identifiers from the search results.
        """
        # Perform the vector search using the vector_search method
        search_results = self._graph.search(
            data=query_embedding,
            vector_attribute_name=self.config.vector_attribute_name,
            node_type=self.config.node_type,
            limit=k,
        )

        # Extract the node ids
        return [result["id"] for result in search_results]
