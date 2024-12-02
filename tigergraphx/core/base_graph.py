import logging
from typing import Optional

from tigergraphx.config import (
    TigerGraphConnectionConfig,
    GraphSchema,
)
from tigergraphx.core.graph_context import GraphContext
from tigergraphx.core.gsql import (
    CREATE_QUERY_API_DEGREE,
    CREATE_QUERY_API_GET_NODE_EDGES,
)
from tigergraphx.core.managers import (
    NodeManager,
    EdgeManager,
    QueryManager,
    SchemaManager,
    StatisticsManager,
    DataManager,
)

logger = logging.getLogger(__name__)


class BaseGraph:
    def __init__(
        self,
        graph_schema: GraphSchema,
        tigergraph_connection_config: Optional[TigerGraphConnectionConfig] = None,
        drop_existing_graph: bool = False,
    ):
        # Set graph name
        self.name = graph_schema.graph_name

        # Initialize the graph context with the provided schema and connection config
        self._context = GraphContext(
            graph_schema=graph_schema,
            tigergraph_connection_config=tigergraph_connection_config,
        )
        # Initialize managers for handling different aspects of the graph
        self.schema_manager = SchemaManager(self._context)
        self.data_manager = DataManager(self._context)
        self.node_manager = NodeManager(self._context)
        self.edge_manager = EdgeManager(self._context)
        self.statistics_manager = StatisticsManager(self._context)
        self.query_manager = QueryManager(self._context)

        # Create the schema, drop the graph first if drop_existing_graph is True
        schema_is_created = self.schema_manager.create_schema(
            drop_existing_graph=drop_existing_graph
        )

        # Install queries
        if schema_is_created:
            gsql_script = self._create_gsql_install_queries(self.name)
            result = self._context.connection.gsql(gsql_script)
            if "Saved as draft query with type/semantic error" in result:
                error_msg = f"Query type/semantic error. GSQL response: {result}"
                logger.error(error_msg)
                raise RuntimeError(error_msg)

    @staticmethod
    def _create_gsql_install_queries(graph_name: str):
        gsql_script = f"""
USE GRAPH {graph_name}
{CREATE_QUERY_API_DEGREE}
{CREATE_QUERY_API_GET_NODE_EDGES}
INSTALL QUERY *
"""
        return gsql_script.strip()
