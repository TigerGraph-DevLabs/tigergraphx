from enum import Enum
from typing import ClassVar, Dict, Tuple, Type, Optional, Any
from pydantic import Field, model_validator

from tigergraphx.config import BaseConfig


class DataType(Enum):
    """
    Enumeration of supported data types.
    """

    INT = "INT"
    UINT = "UINT"
    FLOAT = "FLOAT"
    DOUBLE = "DOUBLE"
    BOOL = "BOOL"
    STRING = "STRING"
    DATETIME = "DATETIME"


class AttributeSchema(BaseConfig):
    """
    Schema for a graph attribute.
    """

    data_type: DataType = Field(description="The data type of the attribute.")
    default_value: Optional[int | float | bool | str] = Field(
        default=None, description="The default value for the attribute."
    )

    PYTHON_TYPES: ClassVar[Dict[DataType, Type | Tuple[Type, ...]]] = {
        DataType.INT: int,
        DataType.UINT: int,
        DataType.FLOAT: (float, int),
        DataType.DOUBLE: (float, int),
        DataType.BOOL: bool,
        DataType.STRING: str,
        DataType.DATETIME: str,
    }

    @model_validator(mode="after")
    def validate_default_value(self):
        """
        Validate that the default value matches the expected data type.
        """
        if self.default_value is not None:
            expected_types = self.PYTHON_TYPES[self.data_type]
            if not isinstance(self.default_value, expected_types):
                raise TypeError(
                    f"Default value for {self.data_type.name} must be of type "
                    f"{expected_types if isinstance(expected_types, type) else ' or '.join(t.__name__ for t in expected_types)}, "
                    f"but got {type(self.default_value).__name__}."
                )
        return self


class NodeSchema(BaseConfig):
    """
    Schema for a graph node type.
    """

    primary_key: str = Field(description="The primary key for the node type.")
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
    def validate_primary_key_and_attributes(cls, values):
        """
        Validate that the primary key is present in attributes.
        """
        if values.primary_key not in values.attributes:
            raise ValueError(
                f"Primary key '{values.primary_key}' is not defined in attributes."
            )
        return values


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
    def validate_edge_references(cls, values):
        """
        Ensure all edges reference existing nodes in the graph schema.
        """
        node_types = set(values.nodes.keys())
        missing_node_edges = [
            f"Edge '{edge_type}' requires nodes '{edge.from_node_type}' and '{edge.to_node_type}' "
            f"to be defined"
            for edge_type, edge in values.edges.items()
            if edge.from_node_type not in node_types
            or edge.to_node_type not in node_types
        ]
        if missing_node_edges:
            raise ValueError(
                f"Invalid edges in schema for graph '{values.graph_name}': {'; '.join(missing_node_edges)}"
            )
        return values


AttributeType = (
    AttributeSchema
    | DataType
    | str
    | tuple[DataType | str, Optional[int | float | bool | str]]
    | Dict[str, str]
)
AttributesType = Dict[str, AttributeType]


def string_to_data_type(data_type_str: str) -> DataType:
    """
    Convert a string to a DataType.

    Args:
        data_type_str (str): String representation of the data type.

    Returns:
        DataType: The corresponding DataType.

    Raises:
        ValueError: If the string is not a valid DataType.
    """
    try:
        return DataType[data_type_str.upper()]
    except KeyError:
        raise ValueError(
            f"Invalid data type string: '{data_type_str}'. Expected one of {[dt.name for dt in DataType]}."
        )


def create_attribute_schema(attr: AttributeType) -> AttributeSchema:
    """
    Create an AttributeSchema from various input formats.

    Args:
        attr (AttributeType): Input attribute definition.

    Returns:
        AttributeSchema: The created schema.

    Raises:
        ValueError: If the input format is invalid.
    """
    if isinstance(attr, AttributeSchema):
        return attr
    elif isinstance(attr, DataType):
        return AttributeSchema(data_type=attr)
    elif isinstance(attr, str):
        return AttributeSchema(data_type=string_to_data_type(attr))
    elif isinstance(attr, tuple) and len(attr) > 0:
        data_type = (
            string_to_data_type(attr[0]) if isinstance(attr[0], str) else attr[0]
        )
        default_value = attr[1] if len(attr) > 1 else None
        return AttributeSchema(data_type=data_type, default_value=default_value)
    elif (
        isinstance(attr, Dict)
        and "data_type" in attr
        and isinstance(attr["data_type"], str)
    ):
        data_type = string_to_data_type(attr["data_type"])
        default_value = attr["default_value"] if "default_value" in attr else None
        return AttributeSchema(data_type=data_type, default_value=default_value)
    else:
        raise ValueError(
            f"""Invalid attribute type: {attr}. Expected: 
    AttributeSchema
    | DataType
    | str
    | tuple[DataType | str, Optional[int | float | bool | str]]
    | Dict[str, str]."""
        )


def create_node_schema(
    primary_key: str,
    attributes: AttributesType,
) -> NodeSchema:
    """
    Create a NodeSchema with simplified syntax.

    Args:
        primary_key (str): The primary key for the node type.
        attributes (AttributesType): Attributes for the node.

    Returns:
        NodeSchema: The created node schema.
    """
    attribute_schemas = {
        name: create_attribute_schema(attr) for name, attr in attributes.items()
    }
    return NodeSchema(primary_key=primary_key, attributes=attribute_schemas)


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
