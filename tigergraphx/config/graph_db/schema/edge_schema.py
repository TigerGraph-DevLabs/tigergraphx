from typing import Any, Dict, Set
from pydantic import Field, model_validator

from .attribute_schema import AttributeSchema, AttributesType, create_attribute_schema

from tigergraphx.config import BaseConfig


class EdgeSchema(BaseConfig):
    """
    Schema for a graph edge type.
    """

    is_directed_edge: bool = Field(
        default=False,
        description="Whether the edge is directed.")
    from_node_type: str = Field(description="The type of the source node.")
    to_node_type: str = Field(description="The type of the target node.")
    edge_identifier: Set[str] | str = Field(
        default_factory=set,
        description="An attribute or set of attributes that uniquely identifies an edge in a graph,"
        "distinguishing it from other edges with the same source and target.",
    )
    attributes: Dict[str, AttributeSchema] = Field(
        default_factory=dict,
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
        # Convert edge_identifier to a set if it's a string
        if isinstance(values.get("edge_identifier"), str):
            values["edge_identifier"] = {values["edge_identifier"]}

        attributes = values.get("attributes", {})
        if attributes:
            values["attributes"] = {
                k: create_attribute_schema(v) for k, v in attributes.items()
            }
        return values

    @model_validator(mode="after")
    def validate_edge_identifier_and_attributes(cls, values):
        """
        Validate that the every edge_identifier is present in attributes.
        """
        if isinstance(values.edge_identifier, str):
            if values.edge_identifier not in values.attributes:
                raise ValueError(
                    f"Edge identifier '{values.edge_identifier}' is not defined in attributes."
                )
        else:
            for attribute in values.edge_identifier:
                if attribute not in values.attributes:
                    raise ValueError(
                        f"Edge identifier '{attribute}' is not defined in attributes."
                    )
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
