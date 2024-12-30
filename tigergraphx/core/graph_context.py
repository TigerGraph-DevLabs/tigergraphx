from typing import Optional

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

        # Create a TigerGraph connection
        if tigergraph_connection_config is None:  # Set default options
            tigergraph_connection_config = TigerGraphConnectionConfig()
        self.connection = TigerGraphConnection(
            graphname=self.graph_schema.graph_name,
            host=str(tigergraph_connection_config.host),
            restppPort=tigergraph_connection_config.restpp_port,
            gsPort=tigergraph_connection_config.gsql_port,
            username=tigergraph_connection_config.username or "",
            password=tigergraph_connection_config.password or "",
            gsqlSecret=tigergraph_connection_config.secret or "",
            apiToken=tigergraph_connection_config.api_token or "",
        )
