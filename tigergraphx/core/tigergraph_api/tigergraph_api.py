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
    NodeAPI,
    EdgeAPI,
    QueryAPI,
    UpsertAPI,
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
        self._node_api = NodeAPI(config, self.endpoint_registry, self.session)
        self._edge_api = EdgeAPI(config, self.endpoint_registry, self.session)
        self._query_api = QueryAPI(config, self.endpoint_registry, self.session)
        self._upsert_api = UpsertAPI(config, self.endpoint_registry, self.session)

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

    # ------------------------------ Node ------------------------------
    def retrieve_a_node(self, graph_name: str, node_type: str, node_id: str) -> List:
        return self._node_api.retrieve_a_node(graph_name, node_type, node_id)

    def delete_a_node(self, graph_name: str, node_type: str, node_id: str) -> Dict:
        return self._node_api.delete_a_node(graph_name, node_type, node_id)

    def delete_nodes(self, graph_name: str, node_type: str) -> Dict:
        return self._node_api.delete_nodes(graph_name, node_type)

    # ------------------------------ Edge ------------------------------
    def retrieve_a_edge(
        self,
        graph_name: str,
        source_node_type: str,
        source_node_id: str,
        edge_type: str,
        target_node_type: str,
        target_node_id: str,
    ) -> List:
        return self._edge_api.retrieve_a_edge(
            graph_name=graph_name,
            source_node_type=source_node_type,
            source_node_id=source_node_id,
            edge_type=edge_type,
            target_node_type=target_node_type,
            target_node_id=target_node_id,
        )

    # ------------------------------ Query ------------------------------
    def create_query(self, graph_name: str, gsql_query: str) -> str:
        return self._query_api.create_query(graph_name, gsql_query)

    def install_query(self, graph_name: str, query_names: str | List[str]) -> str:
        return self._query_api.install_query(graph_name, query_names)

    def drop_query(self, graph_name: str, query_name: str) -> Dict:
        return self._query_api.drop_query(graph_name, query_name)

    def run_interpreted_query(
        self, gsql_query: str, params: Optional[Dict[str, Any]] = None
    ) -> List:
        return self._query_api.run_interpreted_query(gsql_query, params)

    def run_installed_query_get(
        self, graph_name: str, query_name: str, params: Optional[Dict[str, Any]] = None
    ) -> List:
        return self._query_api.run_installed_query_get(graph_name, query_name, params)

    def run_installed_query_post(
        self, graph_name: str, query_name: str, params: Optional[Dict[str, Any]] = None
    ) -> List:
        return self._query_api.run_installed_query_post(graph_name, query_name, params)

    # ------------------------------ Upsert ------------------------------
    def upsert_graph_data(self, graph_name: str, payload: Dict) -> List:
        return self._upsert_api.upsert_graph_data(graph_name, payload)

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
