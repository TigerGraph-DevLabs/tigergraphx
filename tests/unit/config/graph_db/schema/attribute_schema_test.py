import pytest

from tigergraphx.config import (
    DataType,
    AttributeSchema,
)


class TestGraphSchema:
    def test_attribute_schema_valid(self):
        """Test creating a valid AttributeSchema."""
        attr = AttributeSchema(data_type=DataType.STRING, default_value="Hello")
        assert attr.data_type == DataType.STRING
        assert attr.default_value == "Hello"

    def test_attribute_schema_invalid_default(self):
        """Test AttributeSchema with invalid default value."""
        with pytest.raises(TypeError, match="must be of type <class 'str'>"):
            AttributeSchema(data_type=DataType.STRING, default_value=123)
