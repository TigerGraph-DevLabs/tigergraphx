# Copyright 2025 TigerGraph Inc.
# Licensed under the Apache License, Version 2.0.
# See the LICENSE file or https://www.apache.org/licenses/LICENSE-2.0
#
# Permission is granted to use, copy, modify, and distribute this software
# under the License. The software is provided "AS IS", without warranty.

from typing import Any, Dict, List, Optional
from requests import Session
from requests.auth import AuthBase, HTTPBasicAuth

from .endpoint_handler.endpoint_registry import EndpointRegistry
from .api import (
    AdminAPI,
    GSQLAPI,
    SchemaAPI,
    QueryAPI,
)

from tigergraphx.config import TigerGraphConnectionConfig


class BearerAuth(AuthBase):
    """Custom authentication class for handling Bearer tokens."""

    def __init__(self, token):
        self.token = token

    def __call__(self, r):
        r.headers["Authorization"] = f"Bearer {self.token}"
        return r


class TigerGraphAPI:
    def __init__(self, config: TigerGraphConnectionConfig):
        """
        Initialize TigerGraphAPI with configuration, endpoint registry, and session.

        Args:
            config: Configuration object for TigerGraph connection.
            endpoint_config_path: Path to the YAML file defining endpoints.
        """
        self.config = config

        # Initialize the EndpointRegistry
        self.endpoint_registry = EndpointRegistry(config=config)

        # Create a shared session
        self.session = self._initialize_session()

        # Initialize API classes
        self._admin_api = AdminAPI(config, self.endpoint_registry, self.session)
        self._gsql_api = GSQLAPI(config, self.endpoint_registry, self.session)
        self._schema_api = SchemaAPI(config, self.endpoint_registry, self.session)
        self._query_api = QueryAPI(config, self.endpoint_registry, self.session)

    # ------------------------------ Admin ------------------------------
    def ping(self) -> str:
        return self._admin_api.ping()

    # ------------------------------ GSQL ------------------------------
    def gsql(self, command: str) -> str:
        return self._gsql_api.gsql(command)

    # ------------------------------ Schema ------------------------------
    def get_schema(self, graph_name: str) -> Dict:
        """
        Retrieve the schema of a graph.

        Args:
            graph_name: The name of the graph.

        Returns:
            The schema as JSON.
        """
        return self._schema_api.get_schema(graph_name)

    # ------------------------------ Query ------------------------------
    def run_interpreted_query(
        self, query: str, params: Optional[Dict[str, Any]] = None
    ) -> List:
        return self._query_api.run_interpreted_query(query, params)

    # def run_installed_query_get(
    #     self, query_name: str, params: Optional[Dict[str, Any]] = None
    # ) -> List:
    #     return self._query_api.run_installed_query_get(query_name, params)
    #
    # def run_installed_query_post(
    #     self, query_name: str, params: Optional[Dict[str, Any]] = None
    # ) -> List:
    #     return self._query_api.run_installed_query_post(query_name, params)

    def _initialize_session(self) -> Session:
        """
        Create a shared requests.Session with retries and default headers.

        Returns:
            A configured session object.
        """
        session = Session()

        # Set authentication
        session.auth = self._get_auth()
        return session

    def _get_auth(self):
        """
        Generate authentication object for the session.

        Returns:
            HTTPBasicAuth for username/password, BearerAuth for tokens, or None.
        """
        if self.config.secret:
            return HTTPBasicAuth("__GSQL__secret", self.config.secret)
        elif self.config.username and self.config.password:
            return HTTPBasicAuth(self.config.username, self.config.password)
        elif self.config.token:
            return BearerAuth(self.config.token)  # Use custom class for Bearer token
        return None  # No authentication needed
