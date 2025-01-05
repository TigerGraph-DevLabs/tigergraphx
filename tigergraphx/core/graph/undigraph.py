from typing import Dict, Optional
from pathlib import Path

from .homograph import HomoGraph
from tigergraphx.config import (
    AttributesType,
    create_node_schema,
    create_edge_schema,
    TigerGraphConnectionConfig,
)


class UndiGraph(HomoGraph):
    """
    Represents an undirected graph with a single node and edge type.
    """

    def __init__(
        self,
        graph_name: str,
        node_type: str = "MyNode",
        edge_type: str = "MyEdge",
        node_primary_key: str = "id",
        node_attributes: AttributesType = {
            "id": "STRING",
            "entity_type": "STRING",
            "description": "STRING",
        },
        edge_attributes: AttributesType = {
            "weight": "DOUBLE",
            "description": "STRING",
        },
        tigergraph_connection_config: Optional[
            TigerGraphConnectionConfig | Dict | str | Path
        ] = None,
        drop_existing_graph: bool = False,
    ):
        """
        Initialize an UndiGraph instance.

        Args:
            graph_name (str): The name of the graph.
            node_type (str, optional): The type of nodes in the graph. Defaults to "MyNode".
            edge_type (str, optional): The type of edges in the graph. Defaults to "MyEdge".
            node_primary_key (str, optional): The primary key for nodes. Defaults to "id".
            node_attributes (AttributesType, optional): Attributes for nodes. Defaults to:
                ```python
                {
                    "id": "STRING",
                    "entity_type": "STRING",
                    "description": "STRING",
                }
                ```
            edge_attributes (AttributesType, optional): Attributes for edges. Defaults to:
                ```python
                {
                    "weight": "DOUBLE",
                    "description": "STRING",
                }
                ```
            tigergraph_connection_config (Optional[TigerGraphConnectionConfig | Dict | str | Path]):
                Configuration for TigerGraph connection. Defaults to None.
            drop_existing_graph (bool, optional): Whether to drop the existing graph if it exists. Defaults to False.
        """
        node_schema = create_node_schema(
            primary_key=node_primary_key,
            attributes=node_attributes,
        )
        edge_schema = create_edge_schema(
            is_directed_edge=False,
            from_node_type=node_type,
            to_node_type=node_type,
            attributes=edge_attributes,
        )
        super().__init__(
            graph_name=graph_name,
            node_type=node_type,
            node_schema=node_schema,
            edge_type=edge_type,
            edge_schema=edge_schema,
            tigergraph_connection_config=tigergraph_connection_config,
            drop_existing_graph=drop_existing_graph,
        )
