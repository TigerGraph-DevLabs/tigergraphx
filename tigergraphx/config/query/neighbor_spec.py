from typing import List, Optional
from pydantic import Field

from ..base_config import BaseConfig


class NeighborSpec(BaseConfig):
    start_nodes: str | List[str] = Field(
        ..., description="List of starting node IDs."
    )
    start_node_type: str = Field(
        ..., description="A string defining the type of the start node."
    )
    edge_types: Optional[str | List[str]] = Field(
        None, description="List of allowed edge types for traversal."
    )
    target_node_types: Optional[str | List[str]] = Field(
        None, description="List of allowed target node types."
    )
    filter_expression: Optional[str] = Field(
        None, description="A string or callable defining complex filtering logic."
    )
    return_attributes: Optional[str | List[str]] = Field(
        None, description="List of attributes to include in the results."
    )
    limit: Optional[int] = Field(
        None, description="Maximum number of results to return."
    )
