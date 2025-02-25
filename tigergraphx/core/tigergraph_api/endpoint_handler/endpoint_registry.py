# Copyright 2025 TigerGraph Inc.
# Licensed under the Apache License, Version 2.0.
# See the LICENSE file or https://www.apache.org/licenses/LICENSE-2.0
#
# Permission is granted to use, copy, modify, and distribute this software
# under the License. The software is provided "AS IS", without warranty.

from typing import Any, Dict, Literal, Optional
import yaml
from pathlib import Path

from tigergraphx.config import TigerGraphConnectionConfig

DEFAULT_ENDPOINT_PATH = (
    Path(__file__).resolve().parent.parent.parent.parent
    / "config/endpoint_definitions.yaml"
)


class EndpointRegistry:
    def __init__(
        self,
        config: TigerGraphConnectionConfig,
        endpoint_path: Optional[Path] = None,
    ):
        """
        Initializes the registry and precomputes endpoints.
        """
        endpoint_path = endpoint_path or DEFAULT_ENDPOINT_PATH
        with open(endpoint_path, "r") as file:
            self.raw_config = yaml.safe_load(file)

        self.config = config
        self.endpoints = self._precompute_endpoints()

    def _precompute_endpoints(self) -> Dict[str, Dict[str, Any]]:
        """
        Precomputes endpoints based on the YAML configuration and global settings.
        """
        endpoints = {}
        defaults = self.raw_config.get("defaults", {})
        default_method = defaults.get("method", "GET")
        default_port = defaults.get("port", "gsql_port")
        default_content_type = defaults.get("content_type", "application/json")

        for name, details in self.raw_config["endpoints"].items():
            # Retrieve path
            path = details.get("path", {})
            if isinstance(path, dict):
                paths = path  # Version-specific paths
            else:
                paths = {"3.x": path, "4.x": path}

            # Retrieve method
            method = details.get("method", default_method)
            if isinstance(method, dict):
                methods = method  # Version-specific methods
            else:
                methods = {"3.x": method, "4.x": method}

            # Retrieve port
            port = details.get("port", default_port)
            if isinstance(port, dict):
                ports = port  # Version-specific ports
            else:
                ports = {"3.x": port, "4.x": port}

            # Retrieve content_type
            content_type = details.get("content_type", default_content_type)
            if isinstance(content_type, dict):
                content_types = content_type  # Version-specific ports
            else:
                content_types = {"3.x": content_type, "4.x": content_type}

            endpoints[name] = {
                "paths": paths,
                "methods": methods,
                "ports": ports,
                "content_types": content_types,
            }

        return endpoints

    def get_endpoint(
        self, name: str, version: Literal["4.x", "3.x"] = "4.x", **kwargs
    ) -> Dict[str, Any]:
        """
        Retrieves the precomputed endpoint details for a given name and version.
        """
        if name not in self.endpoints:
            raise ValueError(f"Endpoint '{name}' not found in registry.")

        endpoint = self.endpoints[name]

        # Resolve path
        if version not in endpoint["paths"]:
            raise ValueError(
                f"Path not defined for version '{version}' in endpoint '{name}'."
            )
        path_template = endpoint["paths"][version]
        path = path_template.format(**kwargs)

        # Resolve method
        if version not in endpoint["methods"]:
            raise ValueError(
                f"Method not defined for version '{version}' in endpoint '{name}'."
            )
        method = endpoint["methods"][version]

        # Resolve port
        if version not in endpoint["ports"]:
            raise ValueError(
                f"Port not defined for version '{version}' in endpoint '{name}'."
            )
        port = endpoint["ports"][version]

        # Resolve content_type
        if version not in endpoint["content_types"]:
            raise ValueError(
                f"Content type not defined for version '{version}' in endpoint '{name}'."
            )
        content_type = endpoint["content_types"][version]

        return {"path": path, "method": method, "port": port, "content_type": content_type}
