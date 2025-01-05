from typing import Any, Dict, Optional
from pydantic import Field, model_validator

from .attribute_schema import AttributeSchema, AttributesType, create_attribute_schema
from .vector_attribute_schema import (
    VectorAttributeSchema,
    VectorAttributesType,
    create_vector_attribute_schema,
)

from tigergraphx.config import BaseConfig


class NodeSchema(BaseConfig):
    """
    Schema for a graph node type.
    """

    primary_key: str = Field(description="The primary key for the node type.")
    attributes: Dict[str, AttributeSchema] = Field(
        default_factory=dict,
        description="A dictionary of attribute names to their schemas.",
    )
    vector_attributes: Dict[str, VectorAttributeSchema] = Field(
        default_factory=dict,
        description="A dictionary of vector attribute names to their schemas.",
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
        vector_attributes = values.get("vector_attributes", {})
        if vector_attributes:
            values["vector_attributes"] = {
                k: create_vector_attribute_schema(v)
                for k, v in vector_attributes.items()
            }
        return values

    @model_validator(mode="after")
    def validate_primary_key_and_attributes(cls, values):
        """
        Validate that the primary key is present in attributes.
        """
        if values.primary_key not in values.attributes:
            raise ValueError(
                f"Primary key '{values.primary_key}' is not defined in attributes."
            )
        return values


def create_node_schema(
    primary_key: str,
    attributes: AttributesType,
    vector_attributes: Optional[VectorAttributesType] = None,
) -> NodeSchema:
    """
    Create a NodeSchema with simplified syntax.

    Args:
        primary_key (str): The primary key for the node type.
        attributes (AttributesType): Attributes for the node.
        vector_attributes (VectorAttributesType): Vector attributes for the node.

    Returns:
        NodeSchema: The created node schema.
    """
    attribute_schemas = {
        name: create_attribute_schema(attr) for name, attr in attributes.items()
    }
    vector_attribute_schemas = {}
    if vector_attributes:
        vector_attribute_schemas = {
            name: create_vector_attribute_schema(attr)
            for name, attr in vector_attributes.items()
        }
    return NodeSchema(
        primary_key=primary_key,
        attributes=attribute_schemas,
        vector_attributes=vector_attribute_schemas,
    )
