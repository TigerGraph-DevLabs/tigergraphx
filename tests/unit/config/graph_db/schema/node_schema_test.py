import pytest

from tigergraphx.config import (
    DataType,
    AttributeSchema,
    NodeSchema,
)


class TestNodeSchema:
    def test_node_schema_valid(self):
        """Test creating a valid NodeSchema."""
        attributes = {
            "id": AttributeSchema(data_type=DataType.STRING),
            "name": AttributeSchema(
                data_type=DataType.STRING, default_value="Default Name"
            ),
        }
        node = NodeSchema(primary_key="id", attributes=attributes)
        assert node.primary_key == "id"
        assert "id" in node.attributes
        assert node.attributes["name"].default_value == "Default Name"

    def test_node_schema_missing_primary_key(self):
        """Test NodeSchema with a missing primary key in attributes."""
        attributes = {
            "name": AttributeSchema(
                data_type=DataType.STRING, default_value="Default Name"
            ),
        }
        with pytest.raises(
            ValueError, match="Primary key 'id' is not defined in attributes."
        ):
            NodeSchema(primary_key="id", attributes=attributes)
