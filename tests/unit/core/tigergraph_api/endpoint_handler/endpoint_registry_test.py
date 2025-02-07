import pytest
import yaml
from pathlib import Path

from tigergraphx.core.tigergraph_api import EndpointRegistry
from tigergraphx.config import TigerGraphConnectionConfig


class TestEndpointRegistry:
    @pytest.fixture
    def mock_config(self):
        """Fixture for TigerGraphConnectionConfig."""
        return TigerGraphConnectionConfig()

    @pytest.fixture
    def create_temp_yaml(self, tmp_path):
        """Fixture to create temporary YAML files."""

        def _create_yaml(content: dict):
            yaml_file = tmp_path / "endpoint_definitions.yaml"
            with yaml_file.open("w") as file:
                yaml.dump(content, file)
            return yaml_file

        return _create_yaml

    def test_missing_version_path(self, mock_config, create_temp_yaml):
        """Test error raised when path is missing for a specific version."""
        yaml_content = {
            "endpoints": {
                "get_schema": {
                    "path": {"3.x": "/gsqlserver/gsql/schema"},
                    "method": "POST",
                    "port": "gsql_port",
                }
            },
            "defaults": {
                "method": "GET",
                "port": "gsql_port",
            },
        }
        yaml_file = create_temp_yaml(yaml_content)
        registry = EndpointRegistry(endpoint_path=Path(yaml_file), config=mock_config)

        with pytest.raises(
            ValueError,
            match="Path not defined for version '4.x' in endpoint 'get_schema'.",
        ):
            registry.get_endpoint("get_schema", version="4.x")

    def test_missing_version_method(self, mock_config, create_temp_yaml):
        """Test error raised when method is missing for a specific version."""
        yaml_content = {
            "endpoints": {
                "set_schema": {
                    "path": {
                        "3.x": "/gsqlserver/gsql/set_schema",
                        "4.x": "/gsql/v1/set_schema/graphs/{graph}",
                    },
                    "method": {"3.x": "POST"},
                    "port": {"3.x": "gsql_port", "4.x": "restpp_port"},
                }
            },
            "defaults": {
                "method": "GET",
                "port": "gsql_port",
            },
        }
        yaml_file = create_temp_yaml(yaml_content)
        registry = EndpointRegistry(endpoint_path=Path(yaml_file), config=mock_config)

        with pytest.raises(
            ValueError,
            match="Method not defined for version '4.x' in endpoint 'set_schema'.",
        ):
            registry.get_endpoint("set_schema", version="4.x", graph="MyGraph")

    def test_missing_version_port(self, mock_config, create_temp_yaml):
        """Test error raised when port is missing for a specific version."""
        yaml_content = {
            "endpoints": {
                "set_schema": {
                    "path": {
                        "3.x": "/gsqlserver/gsql/set_schema",
                        "4.x": "/gsql/v1/set_schema/graphs/{graph}",
                    },
                    "method": {"3.x": "POST", "4.x": "GET"},
                    "port": {"3.x": "gsql_port"},
                }
            },
            "defaults": {
                "method": "GET",
                "port": "gsql_port",
            },
        }
        yaml_file = create_temp_yaml(yaml_content)
        registry = EndpointRegistry(endpoint_path=Path(yaml_file), config=mock_config)

        with pytest.raises(
            ValueError,
            match="Port not defined for version '4.x' in endpoint 'set_schema'.",
        ):
            registry.get_endpoint("set_schema", version="4.x", graph="MyGraph")
