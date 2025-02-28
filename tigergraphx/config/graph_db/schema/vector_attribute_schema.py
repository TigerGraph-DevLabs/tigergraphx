# Copyright 2025 TigerGraph Inc.
# Licensed under the Apache License, Version 2.0.
# See the LICENSE file or https://www.apache.org/licenses/LICENSE-2.0
#
# Permission is granted to use, copy, modify, and distribute this software
# under the License. The software is provided "AS IS", without warranty.

from typing import Any, Dict, Literal
from pydantic import Field, PositiveInt

from tigergraphx.config import BaseConfig


class VectorAttributeSchema(BaseConfig):
    """
    Schema for a vector attribute.
    """

    dimension: PositiveInt = Field(
        ge=1,
        default=1536,
        description="The dimension of the vector attribute. Must be at least 1.",
    )
    index_type: Literal["HNSW"] = Field(
        default="HNSW",
        description='The index type for the vector attribute. Currently only "HNSW" is supported.',
    )
    data_type: Literal["FLOAT"] = Field(
        default="FLOAT",
        description='The data type of the attribute. Currently only "FLOAT" is supported. '
        'Future types may include "DOUBLE", "HALF", or "BYTE".',
    )
    metric: Literal["COSINE", "IP", "L2"] = Field(
        default="COSINE",
        description='The metric used for distance calculations. Can be "COSINE", "IP" (inner product), or "L2".',
    )


VectorAttributeType = VectorAttributeSchema | int | Dict[str, Any]
VectorAttributesType = Dict[str, VectorAttributeType]


def create_vector_attribute_schema(attr: VectorAttributeType) -> VectorAttributeSchema:
    """
    Create a VectorAttributeSchema from various input formats.

    Args:
        attr: Input vector attribute definition.

    Returns:
        The created VectorAttributeSchema.

    Raises:
        ValueError: If the input format is invalid.
    """
    if isinstance(attr, VectorAttributeSchema):
        return attr
    elif isinstance(attr, int):
        return VectorAttributeSchema(dimension=attr)
    elif isinstance(attr, Dict):
        dimension = attr.get("dimension", 1536)
        index_type = attr.get("index_type", "HNSW")
        data_type = attr.get("data_type", "FLOAT")
        metric = attr.get("metric", "COSINE")
        return VectorAttributeSchema(
            dimension=dimension,
            index_type=index_type,
            data_type=data_type,
            metric=metric,
        )
    else:
        raise ValueError(
            f"Invalid attribute type: {attr}. Expected: VectorAttributeSchema | int | Dict[str, Any]"
        )
