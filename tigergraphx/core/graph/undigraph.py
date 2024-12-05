from typing import Optional

from .homograph import HomoGraph
from tigergraphx.config import (
    DataType,
    AttributesType,
    create_node_schema,
    create_edge_schema,
    TigerGraphConnectionConfig,
)


class UndiGraph(HomoGraph):
    def __init__(
        self,
        graph_name: str,
        node_type: str = "MyNode",
        edge_type: str = "MyEdge",
        node_primary_key: str = "id",
        node_attributes: AttributesType = {
            "id": DataType.STRING,
            "entity_type": DataType.STRING,
            "description": DataType.STRING,
        },
        edge_attributes: AttributesType = {
            "weight": DataType.DOUBLE,
            "description": DataType.STRING,
        },
        tigergraph_connection_config: Optional[TigerGraphConnectionConfig] = None,
        drop_existing_graph: bool = False,
    ):
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
