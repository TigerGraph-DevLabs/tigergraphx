from typing import List, Optional
from pydantic import Field

from ..base_config import BaseConfig


class NodeSpec(BaseConfig):
    node_type: Optional[str] = Field(
        ..., description="The type of nodes to select."
    )
    filter_expression: Optional[str] = Field(
        None, description="A string defining filtering logic for the node selection."
    )
    return_attributes: Optional[str | List[str]] = Field(
        None, description="List of attributes to include in the output."
    )
    limit: Optional[int] = Field(None, description="Maximum number of nodes to select.")
