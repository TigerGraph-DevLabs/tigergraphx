from enum import Enum


class DataType(Enum):
    """
    Enumeration of supported data types.
    """

    INT = "INT"
    """Represents an integer type."""

    UINT = "UINT"
    """Represents an unsigned integer type."""

    FLOAT = "FLOAT"
    """Represents a floating-point type."""

    DOUBLE = "DOUBLE"
    """Represents a double-precision floating-point type."""

    BOOL = "BOOL"
    """Represents a boolean type."""

    STRING = "STRING"
    """Represents a string type."""

    DATETIME = "DATETIME"
    """Represents a datetime type."""
