from typing import Dict
from pydantic import Field, model_validator

from .node_schema import NodeSchema
from .edge_schema import EdgeSchema

from tigergraphx.config import BaseConfig


class GraphSchema(BaseConfig):
    """
    Schema for a graph, including nodes and edges.
    """

    graph_name: str = Field(description="The name of the graph.")
    nodes: Dict[str, NodeSchema] = Field(
        description="A dictionary of node type names to their schemas."
    )
    edges: Dict[str, EdgeSchema] = Field(
        description="A dictionary of edge type names to their schemas."
    )

    @model_validator(mode="after")
    def validate_edge_references(self) -> "GraphSchema":
        """
        Ensure all edges reference existing nodes in the graph schema.

        Returns:
            The validated graph schema.

        Raises:
            ValueError: If any edge references undefined node types.
        """
        node_types = set(self.nodes.keys())
        missing_node_edges = [
            f"Edge '{edge_type}' requires nodes '{edge.from_node_type}' and '{edge.to_node_type}' "
            f"to be defined"
            for edge_type, edge in self.edges.items()
            if edge.from_node_type not in node_types or edge.to_node_type not in node_types
        ]
        if missing_node_edges:
            raise ValueError(
                f"Invalid edges in schema for graph '{self.graph_name}': {'; '.join(missing_node_edges)}"
            )
        return self
