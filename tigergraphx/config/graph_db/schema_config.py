from enum import Enum
from typing import ClassVar, Dict, Tuple, Type, Optional, Any
from pydantic import model_validator

from tigergraphx.config import BaseConfig


class DataType(Enum):
    INT = "INT"
    UINT = "UINT"
    FLOAT = "FLOAT"
    DOUBLE = "DOUBLE"
    BOOL = "BOOL"
    STRING = "STRING"
    DATETIME = "DATETIME"


class AttributeSchema(BaseConfig):
    data_type: DataType
    default_value: Optional[int | float | bool | str] = None

    # Class-level mapping of DataType to accepted Python types
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
        """Ensure the default value matches the expected type."""
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
    primary_key: str
    attributes: Dict[str, AttributeSchema]

    @model_validator(mode="before")
    def parse_attributes(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        """Parse shorthand attributes into full AttributeSchema."""

        attributes = values.get("attributes", {})
        if attributes:
            values["attributes"] = {
                k: create_attribute_schema(v) for k, v in attributes.items()
            }
        return values

    @model_validator(mode="after")
    def validate_primary_key_and_attributes(cls, values):
        """Validate that the primary key exists in attributes."""
        if values.primary_key not in values.attributes:
            raise ValueError(
                f"Primary key '{values.primary_key}' is not defined in attributes."
            )
        return values


class EdgeSchema(BaseConfig):
    is_directed_edge: bool
    from_node_type: str
    to_node_type: str
    attributes: Dict[str, AttributeSchema]

    @model_validator(mode="before")
    def parse_attributes(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        """Parse shorthand attributes into full AttributeSchema."""
        attributes = values.get("attributes", {})
        if attributes:
            values["attributes"] = {
                k: create_attribute_schema(v) for k, v in attributes.items()
            }
        return values

    @model_validator(mode="after")
    def validate_attributes(cls, values):
        """Validate default values of attributes in EdgeSchema."""
        return values


class GraphSchema(BaseConfig):
    graph_name: str
    nodes: Dict[str, NodeSchema]
    edges: Dict[str, EdgeSchema]

    @model_validator(mode="after")
    def validate_edge_references(cls, values):
        """
        Ensure all edges reference existing nodes in GraphSchema.
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
)
AttributesType = Dict[str, AttributeType]


# Helper function to convert string to DataType
def string_to_data_type(data_type_str: str) -> DataType:
    try:
        return DataType[data_type_str.upper()]
    except KeyError:
        raise ValueError(
            f"Invalid data type string: '{data_type_str}'. Expected one of {[dt.name for dt in DataType]}."
        )


# Helper function to create AttributeSchema with simpler syntax
def create_attribute_schema(attr: AttributeType) -> AttributeSchema:
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
    else:
        raise ValueError(
            f"Invalid attribute type: {attr}. Expected: str | DataType | tuple[str | DataType, Optional[int | float | bool | str]]."
        )


# Helper function to create NodeSchema with simpler syntax
def create_node_schema(
    primary_key: str,
    attributes: AttributesType,
) -> NodeSchema:
    """
    Helper function to simplify creation of NodeSchema by handling conversion to AttributeSchema.
    """
    attribute_schemas = {
        name: create_attribute_schema(attr) for name, attr in attributes.items()
    }
    return NodeSchema(primary_key=primary_key, attributes=attribute_schemas)


# Helper function to create EdgeSchema with simpler syntax
def create_edge_schema(
    is_directed_edge: bool,
    from_node_type: str,
    to_node_type: str,
    attributes: AttributesType = {},
) -> EdgeSchema:
    """
    Helper function to simplify creation of EdgeSchema by handling conversion to AttributeSchema.
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
