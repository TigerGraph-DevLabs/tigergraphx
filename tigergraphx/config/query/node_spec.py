from typing import List, Optional
from pydantic import Field

from ..base_config import BaseConfig


class NodeSpec(BaseConfig):
    """
    Specification for selecting nodes in a graph query.
    """

    node_type: Optional[str] = Field(None, description="The type of nodes to select.")
    all_node_types: bool = Field(
        False,
        description="If True, nodes of all types will be returned, "
        "and the value of `node_type` will be ignored.",
    )
    filter_expression: Optional[str] = Field(
        None, description="A string defining filtering logic for the node selection."
    )
    return_attributes: Optional[str | List[str]] = Field(
        None, description="List of attributes to include in the output."
    )
    limit: Optional[int] = Field(None, description="Maximum number of nodes to select.")
