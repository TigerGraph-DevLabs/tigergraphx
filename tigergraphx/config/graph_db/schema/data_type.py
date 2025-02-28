# Copyright 2025 TigerGraph Inc.
# Licensed under the Apache License, Version 2.0.
# See the LICENSE file or https://www.apache.org/licenses/LICENSE-2.0
#
# Permission is granted to use, copy, modify, and distribute this software
# under the License. The software is provided "AS IS", without warranty.

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
