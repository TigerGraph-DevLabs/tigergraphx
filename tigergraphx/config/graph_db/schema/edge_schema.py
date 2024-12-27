from typing import Any, Dict
from pydantic import Field, model_validator

from .attribute_schema import AttributeSchema, AttributesType, create_attribute_schema

from tigergraphx.config import BaseConfig


class EdgeSchema(BaseConfig):
    """
    Schema for a graph edge type.
    """

    is_directed_edge: bool = Field(description="Whether the edge is directed.")
    from_node_type: str = Field(description="The type of the source node.")
    to_node_type: str = Field(description="The type of the target node.")
    attributes: Dict[str, AttributeSchema] = Field(
        description="A dictionary of attribute names to their schemas."
    )

    @model_validator(mode="before")
    def parse_attributes(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parse shorthand attributes into full AttributeSchema.

        Args:
            values (Dict[str, Any]): Input values.

        Returns:
            Dict[str, Any]: Parsed values with attributes as AttributeSchema.
        """
        attributes = values.get("attributes", {})
        if attributes:
            values["attributes"] = {
                k: create_attribute_schema(v) for k, v in attributes.items()
            }
        return values

    @model_validator(mode="after")
    def validate_attributes(cls, values):
        """
        Validate attributes in the EdgeSchema.
        """
        return values


def create_edge_schema(
    is_directed_edge: bool,
    from_node_type: str,
    to_node_type: str,
    attributes: AttributesType = {},
) -> EdgeSchema:
    """
    Create an EdgeSchema with simplified syntax.

    Args:
        is_directed_edge (bool): Whether the edge is directed.
        from_node_type (str): The source node type.
        to_node_type (str): The target node type.
        attributes (AttributesType, optional): Attributes for the edge. Defaults to {}.

    Returns:
        EdgeSchema: The created edge schema.
    """
    attribute_schemas = {
        name: create_attribute_schema(attr) for name, attr in attributes.items()
    }
    return EdgeSchema(
        is_directed_edge=is_directed_edge,
        from_node_type=from_node_type,
        to_node_type=to_node_type,
        attributes=attribute_schemas,
    )
