# Copyright 2025 TigerGraph Inc.
# Licensed under the Apache License, Version 2.0.
# See the LICENSE file or https://www.apache.org/licenses/LICENSE-2.0
#
# Permission is granted to use, copy, modify, and distribute this software
# under the License. The software is provided "AS IS", without warranty.

from typing import List, Optional, Set
from pydantic import Field

from ..base_config import BaseConfig


class NeighborSpec(BaseConfig):
    """
    Specification for selecting neighbors in a graph query.
    """

    start_nodes: str | List[str] | int | List[int] = Field(..., description="List of starting node IDs.")
    start_node_type: str = Field(..., description="The type of the start node.")
    start_node_alias: str = Field("s", description="Alias for the source node.")
    edge_type_set: Optional[Set[str]] = Field(
        None, description="Set of allowed edge types for traversal."
    )
    edge_alias: str = Field("e", description="Alias for the edge.")
    target_node_type_set: Optional[Set[str]] = Field(
        None, description="Set of allowed target node types."
    )
    target_node_alias: str = Field("t", description="Alias for the target node.")
    filter_expression: Optional[str] = Field(
        None, description="A string defining complex filtering logic."
    )
    return_attributes: Optional[str | List[str]] = Field(
        None, description="List of attributes to include in the results."
    )
    limit: Optional[int] = Field(
        None, description="Maximum number of results to return."
    )
