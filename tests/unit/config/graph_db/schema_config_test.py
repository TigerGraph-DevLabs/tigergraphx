import pytest
import json

from tigergraphx.config import (
    DataType,
    AttributeSchema,
    NodeSchema,
    EdgeSchema,
    GraphSchema,
)


class TestSchemaConfig:
    def test_attribute_schema_valid(self):
        """Test creating a valid AttributeSchema."""
        attr = AttributeSchema(data_type=DataType.STRING, default_value="Hello")
        assert attr.data_type == DataType.STRING
        assert attr.default_value == "Hello"

    def test_attribute_schema_invalid_default(self):
        """Test AttributeSchema with invalid default value."""
        with pytest.raises(TypeError, match="must be of type <class 'str'>"):
            AttributeSchema(data_type=DataType.STRING, default_value=123)

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

    def test_edge_schema_valid(self):
        """Test creating a valid EdgeSchema."""
        attributes = {
            "weight": AttributeSchema(data_type=DataType.DOUBLE),
        }
        edge = EdgeSchema(
            is_directed_edge=True,
            from_node_type="NodeA",
            to_node_type="NodeB",
            attributes=attributes,
        )
        assert edge.is_directed_edge is True
        assert edge.from_node_type == "NodeA"
        assert edge.to_node_type == "NodeB"

    def test_edge_schema_invalid_attribute(self):
        """Test EdgeSchema with invalid attribute default value."""
        with pytest.raises(TypeError, match="must be of type float or int"):
            EdgeSchema(
                is_directed_edge=True,
                from_node_type="NodeA",
                to_node_type="NodeB",
                attributes={
                    "weight": AttributeSchema(
                        data_type=DataType.DOUBLE, default_value="invalid"
                    ),
                },
            )

    def test_graph_schema_valid(self):
        """Test creating a valid GraphSchema."""
        nodes = {
            "NodeA": NodeSchema(
                primary_key="id",
                attributes={
                    "id": AttributeSchema(data_type=DataType.STRING),
                    "name": AttributeSchema(data_type=DataType.STRING),
                },
            ),
            "NodeB": NodeSchema(
                primary_key="id",
                attributes={
                    "id": AttributeSchema(data_type=DataType.STRING),
                    "value": AttributeSchema(data_type=DataType.INT),
                },
            ),
        }
        edges = {
            "edgeA": EdgeSchema(
                is_directed_edge=True,
                from_node_type="NodeA",
                to_node_type="NodeB",
                attributes={"weight": AttributeSchema(data_type=DataType.DOUBLE)},
            )
        }
        graph = GraphSchema(graph_name="TestGraph", nodes=nodes, edges=edges)
        assert graph.graph_name == "TestGraph"
        assert "NodeA" in graph.nodes
        assert "edgeA" in graph.edges

    def test_graph_schema_invalid_edge(self):
        """Test GraphSchema with an edge referencing missing nodes."""
        nodes = {
            "NodeA": NodeSchema(
                primary_key="id",
                attributes={"id": AttributeSchema(data_type=DataType.STRING)},
            )
        }
        edges = {
            "edgeA": EdgeSchema(
                is_directed_edge=True,
                from_node_type="NodeA",
                to_node_type="NodeB",  # NodeB does not exist
                attributes={"weight": AttributeSchema(data_type=DataType.DOUBLE)},
            )
        }
        with pytest.raises(
            ValueError, match="requires nodes 'NodeA' and 'NodeB' to be defined"
        ):
            GraphSchema(graph_name="InvalidGraph", nodes=nodes, edges=edges)

    def test_ensure_config_from_dict(self):
        """Test ensure_config with a dictionary input."""
        config_dict = {
            "graph_name": "TestGraph",
            "nodes": {
                "NodeA": {
                    "primary_key": "id",
                    "attributes": {"id": {"data_type": "STRING"}},
                }
            },
            "edges": {},
        }
        graph_schema = GraphSchema.ensure_config(config_dict)
        assert graph_schema.graph_name == "TestGraph"
        assert "NodeA" in graph_schema.nodes

    def test_ensure_config_from_yaml(self, tmp_path):
        """Test ensure_config with a YAML file."""
        yaml_content = """
        graph_name: TestGraph
        nodes:
          NodeA:
            primary_key: id
            attributes:
              id:
                data_type: STRING
        edges: {}
        """
        yaml_path = tmp_path / "config.yaml"
        yaml_path.write_text(yaml_content)

        graph_schema = GraphSchema.ensure_config(yaml_path)
        assert graph_schema.graph_name == "TestGraph"
        assert "NodeA" in graph_schema.nodes

    def test_ensure_config_from_json(self, tmp_path):
        """Test ensure_config with a JSON file."""
        json_content = {
            "graph_name": "TestGraph",
            "nodes": {
                "NodeA": {
                    "primary_key": "id",
                    "attributes": {"id": {"data_type": "STRING"}},
                }
            },
            "edges": {},
        }
        json_path = tmp_path / "config.json"
        json_path.write_text(json.dumps(json_content))

        graph_schema = GraphSchema.ensure_config(json_path)
        assert graph_schema.graph_name == "TestGraph"
        assert "NodeA" in graph_schema.nodes

    def test_ensure_config_with_existing_object(self):
        """Test ensure_config with an existing GraphSchema object."""
        existing_schema = GraphSchema(
            graph_name="ExistingGraph",
            nodes={},
            edges={},
        )
        result = GraphSchema.ensure_config(existing_schema)
        assert result == existing_schema


    def test_ensure_config_complex_schema(self):
        """Test ensure_config with a complex schema containing multiple nodes and edges."""
        complex_config = {
            "graph_name": "ComplexGraph",
            "nodes": {
                "User": {
                    "primary_key": "id",
                    "attributes": {
                        "id": {"data_type": "STRING"},
                        "name": {"data_type": "STRING"},
                        "age": {"data_type": "UINT"},
                    },
                },
                "Product": {
                    "primary_key": "id",
                    "attributes": {
                        "id": {"data_type": "STRING"},
                        "name": {"data_type": "STRING"},
                        "price": {"data_type": "DOUBLE"},
                    },
                },
            },
            "edges": {
                "purchased": {
                    "is_directed_edge": True,
                    "from_node_type": "User",
                    "to_node_type": "Product",
                    "attributes": {
                        "purchase_date": {"data_type": "DATETIME"},
                        "quantity": {"data_type": "UINT"},
                    },
                },
                "friend_of": {
                    "is_directed_edge": False,
                    "from_node_type": "User",
                    "to_node_type": "User",
                    "attributes": {
                        "since": {"data_type": "DATETIME"},
                    },
                },
            },
        }

        graph_schema = GraphSchema.ensure_config(complex_config)

        # Assertions for the graph name
        assert graph_schema.graph_name == "ComplexGraph"

        # Assertions for nodes
        assert "User" in graph_schema.nodes
        assert "Product" in graph_schema.nodes
        assert graph_schema.nodes["User"].primary_key == "id"
        assert "name" in graph_schema.nodes["User"].attributes
        assert graph_schema.nodes["Product"].attributes["price"].data_type == DataType.DOUBLE

        # Assertions for edges
        assert "purchased" in graph_schema.edges
        assert "friend_of" in graph_schema.edges
        assert graph_schema.edges["purchased"].is_directed_edge is True
        assert graph_schema.edges["purchased"].attributes["quantity"].data_type == DataType.UINT
        assert graph_schema.edges["friend_of"].is_directed_edge is False
