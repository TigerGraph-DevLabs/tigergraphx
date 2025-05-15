# Copyright 2025 TigerGraph Inc.
# Licensed under the Apache License, Version 2.0.
# See the LICENSE file or https://www.apache.org/licenses/LICENSE-2.0
#
# Permission is granted to use, copy, modify, and distribute this software
# under the License. The software is provided "AS IS", without warranty.

from typing import Any, Dict, List, Literal, Optional
from requests import Session
from requests.auth import AuthBase, HTTPBasicAuth

from .endpoint_handler.endpoint_registry import EndpointRegistry
from .api import (
    AdminAPI,
    GSQLAPI,
    SchemaAPI,
    DataSourceAPI,
    NodeAPI,
    EdgeAPI,
    QueryAPI,
    UpsertAPI,
)
from .api.data_source_api import DataSourceType

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
        self._data_api = DataSourceAPI(config, self.endpoint_registry, self.session)
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

    # ------------------------------ Data ------------------------------
    def create_data_source(
        self,
        name: str,
        data_source_type: str | DataSourceType,
        access_key: Optional[str] = None,
        secret_key: Optional[str] = None,
        extra_config: Optional[Dict[str, Any]] = None,
        graph: Optional[str] = None,
    ) -> str:
        """
        Create a new data source configuration.

        Args:
            name: Name of the data source.
            source_type: The type of the source (s3, gcs, abs).
            access_key: Optional access key for cloud storage.
            secret_key: Optional secret key for cloud storage.
            extra_config: Additional configuration values to merge into the request payload.
            graph: Optional graph name.

        Returns:
            API response message.
        """
        return self._data_api.create_data_source(
            name=name,
            data_source_type=data_source_type,
            access_key=access_key,
            secret_key=secret_key,
            extra_config=extra_config,
            graph=graph,
        )

    def update_data_source(
        self,
        name: str,
        data_source_type: str | DataSourceType,
        access_key: Optional[str] = None,
        secret_key: Optional[str] = None,
        extra_config: Optional[Dict[str, Any]] = None,
        graph: Optional[str] = None,
    ) -> str:
        """
        Update an existing data source configuration.

        Args:
            name: Name of the data source.
            data_source_type: Type of the source (e.g., s3, gcs, abs).
            access_key: Optional access key.
            secret_key: Optional secret key.
            extra_config: Extra config values to merge in.
            graph: Optional graph name.

        Returns:
            API response message.
        """
        return self._data_api.update_data_source(
            name=name,
            data_source_type=data_source_type,
            access_key=access_key,
            secret_key=secret_key,
            extra_config=extra_config,
            graph=graph,
        )

    def get_all_data_sources(self, graph: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Retrieve a list of all data sources, optionally filtered by graph name.

        Args:
            graph: Optional graph name.

        Returns:
            List of data source dictionaries.
        """
        return self._data_api.get_all_data_sources(graph=graph)

    def drop_data_source(self, name: str, graph: Optional[str] = None) -> str:
        """
        Drop a data source by name. Can specify a graph if removing from a graph-specific context.

        Args:
            name: Name of the data source to remove.
            graph: Optional graph name, required if the data source is local.

        Returns:
            API response message.
        """
        return self._data_api.drop_data_source(name=name, graph=graph)

    def drop_all_data_sources(self, graph: Optional[str] = None) -> str:
        """
        Drop all data source configurations, optionally within a specific graph.

        Args:
            graph: Optional graph name.

        Returns:
            API response message.
        """
        return self._data_api.drop_all_data_sources(graph=graph)

    def get_data_source(self, name: str) -> Dict[str, Any]:
        """
        Get a data source's configuration.

        Args:
            name: Name of the data source.

        Returns:
            A dictionary with data source configuration.
        """
        return self._data_api.get_data_source(name=name)

    def preview_sample_data(
        self,
        path: str,
        data_source_type: Optional[str | DataSourceType] = None,
        data_source: Optional[str] = None,
        data_format: Optional[Literal["csv", "json"]] = "csv",
        size: Optional[int] = 10,
        has_header: bool = True,
        separator: Optional[str] = ",",
        eol: Optional[str] = "\\n",
        quote: Optional[Literal["'", '"']] = '"',
    ) -> Dict[str, Any]:
        """
        Preview sample data from a file path

        Args:
            path: The full file path or URI to preview data from.
            source_type: The source type, e.g., 's3', 'gcs', 'abs', etc.
            data_source: Optional named data source configuration.
            data_format: Format of the file, either 'csv' or 'json'.
            size: Number of rows to preview (default 10).
            has_header: Whether the file contains a header row.
            separator: Field separator used in the file.
            eol: End-of-line character.
            quote: Optional quote character used in the file.

        Returns:
            A dictionary containing the previewed sample data.
        """
        return self._data_api.preview_sample_data(
            path=path,
            data_source_type=data_source_type,
            data_source=data_source,
            data_format=data_format,
            size=size,
            has_header=has_header,
            separator=separator,
            eol=eol,
            quote=quote,
        )

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
    def upsert_graph_data(self, graph_name: str, payload: Dict[str, Any]) -> List:
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
