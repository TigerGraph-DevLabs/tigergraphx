import pytest
from pydantic import ValidationError

from tigergraphx.config.graph_db.schema.vector_attribute_schema import (
    VectorAttributeSchema,
    create_vector_attribute_schema,
)


class TestVectorAttributeSchema:
    """
    Unit tests for the VectorAttributeSchema and create_vector_attribute_schema function.
    """

    def test_vector_attribute_schema_default_values(self):
        # Test default values for VectorAttributeSchema
        schema = VectorAttributeSchema(dimension=1024)

        assert schema.dimension == 1024
        assert schema.index_type == "HNSW"
        assert schema.data_type == "FLOAT"
        assert schema.metric == "COSINE"

    def test_vector_attribute_schema_with_all_fields(self):
        # Test creating a VectorAttributeSchema with all fields
        schema = VectorAttributeSchema(
            dimension=512, index_type="HNSW", data_type="FLOAT", metric="L2"
        )

        assert schema.dimension == 512
        assert schema.index_type == "HNSW"
        assert schema.data_type == "FLOAT"
        assert schema.metric == "L2"

    def test_invalid_dimension(self):
        # Test invalid dimension (less than 1)
        with pytest.raises(ValidationError):
            VectorAttributeSchema(dimension=0)  # Should raise ValidationError

    def test_create_vector_attribute_schema_with_int(self):
        # Test passing an integer (dimension)
        schema = create_vector_attribute_schema(256)

        assert schema.dimension == 256
        assert schema.index_type == "HNSW"
        assert schema.data_type == "FLOAT"
        assert schema.metric == "COSINE"

    def test_create_vector_attribute_schema_with_dict(self):
        # Test passing a dictionary
        attr = {
            "dimension": 512,
            "index_type": "HNSW",
            "data_type": "FLOAT",
            "metric": "IP",
        }
        schema = create_vector_attribute_schema(attr)

        assert schema.dimension == 512
        assert schema.index_type == "HNSW"
        assert schema.data_type == "FLOAT"
        assert schema.metric == "IP"

    def test_create_vector_attribute_schema_with_missing_keys(self):
        # Test dictionary with missing optional keys (uses defaults)
        attr = {"dimension": 1024}
        schema = create_vector_attribute_schema(attr)

        assert schema.dimension == 1024
        assert schema.index_type == "HNSW"
        assert schema.data_type == "FLOAT"
        assert schema.metric == "COSINE"

    def test_create_vector_attribute_schema_invalid_dimension(self):
        # Test dictionary with invalid dimension (non-integer)
        attr = {
            "dimension": "invalid"  # Invalid dimension type
        }
        with pytest.raises(ValueError):
            create_vector_attribute_schema(attr)

    def test_create_vector_attribute_schema_with_unexpected_fields(self):
        # Test dictionary with unexpected fields
        attr = {
            "dimension": 256,
            "unexpected_field": "value",  # Should be ignored
        }
        schema = create_vector_attribute_schema(attr)

        assert schema.dimension == 256
        assert schema.index_type == "HNSW"  # Default value
        assert schema.data_type == "FLOAT"  # Default value
        assert schema.metric == "COSINE"  # Default value
