from typing import Dict
from requests import Session
from requests.adapters import HTTPAdapter
from requests.auth import AuthBase, HTTPBasicAuth
from urllib3.util import Retry

from .endpoint_handler.endpoint_registry import EndpointRegistry
from .api import (
    AdminAPI,
    GSQLAPI,
    SchemaAPI,
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

    def ping(self) -> Dict:
        return self._admin_api.ping()

    def gsql(self, command: str) -> Dict:
        return self._gsql_api.gsql(command)

    def get_schema(self, graph_name: str) -> Dict:
        """
        Retrieve the schema of a graph.

        Args:
            graph_name: The name of the graph.

        Returns:
            The schema as JSON.
        """
        return self._schema_api.get_schema(graph_name)

    def _initialize_session(self) -> Session:
        """
        Create a shared requests.Session with retries and default headers.

        Returns:
            A configured session object.
        """
        session = Session()

        retries = Retry(
            total=3,
            backoff_factor=0.1,
            status_forcelist=[502, 503, 504],
            allowed_methods={"POST"},
        )
        session.mount("https://", HTTPAdapter(max_retries=retries))

        # Configure retry logic
        retry_strategy = Retry(
            total=3,
            status_forcelist=[500, 502, 503, 504],
            backoff_factor=1,
            allowed_methods=["GET", "POST", "DELETE", "PUT", "PATCH"],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("https://", adapter)
        session.mount("http://", adapter)

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
