from typing import Optional
import logging

from pyTigerGraph import TigerGraphConnection
from tigergraphx.config import (
    TigerGraphConnectionConfig,
    GraphSchema,
)


class GraphContext:
    def __init__(
        self,
        graph_schema: GraphSchema,
        tigergraph_connection_config: Optional[TigerGraphConnectionConfig] = None,
    ):
        self.graph_schema = graph_schema

        # Set the default node type if there's only one node type
        nodes = graph_schema.nodes
        self.node_type = next(iter(nodes)) if len(nodes) == 1 else ""

        # Set the default edge type if there's only one edge type
        edges = graph_schema.edges
        self.edge_type = next(iter(edges)) if len(edges) == 1 else ""

        # Create a TigerGraph connection
        if tigergraph_connection_config is None:  # Set default options
            tigergraph_connection_config = TigerGraphConnectionConfig()
        self.connection = TigerGraphConnection(
            host=tigergraph_connection_config.host,
            graphname=self.graph_schema.graph_name,
            username=tigergraph_connection_config.user_name,
            password=tigergraph_connection_config.password,
            restppPort=tigergraph_connection_config.restpp_port,
            gsPort=tigergraph_connection_config.graph_studio_port,
        )
