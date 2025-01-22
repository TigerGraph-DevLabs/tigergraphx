from typing import ClassVar, Dict, Optional, Tuple, Type
from pydantic import Field, model_validator

from .data_type import DataType

from tigergraphx.config import BaseConfig


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
    def validate_default_value(self) -> "AttributeSchema":
        """
        Validate that the default value matches the expected data type.

        Returns:
            The validated AttributeSchema.

        Raises:
            TypeError: If the default value does not match the expected data type.
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
        data_type_str: String representation of the data type.

    Returns:
        The corresponding DataType.

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
        attr: Input attribute definition.

    Returns:
        The created AttributeSchema.

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
        default_value = attr.get("default_value", None)
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
