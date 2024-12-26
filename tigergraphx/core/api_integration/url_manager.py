from urllib.parse import urlparse, urljoin


class URLManager:
    def __init__(self, base_url: str, version: str):
        # Base URL (scheme + netloc)
        self.base_url = base_url

        # Validate the base URL
        self._validate_url(self.base_url)

        # Set the version (e.g., '3.0', '4.0')
        self.version = version

        # Initialize version-specific URL mappings
        self._initialize_versioned_urls()

    def get_url(self, endpoint: str, **params) -> str:
        """
        Return the full URL for a specific endpoint, with dynamic parameters.
        The URL will replace placeholders like {graph_name} with the actual values passed in **params.
        """
        # Check if the endpoint exists as a member variable
        url = getattr(self, f"{endpoint}_url", None)
        if not url:
            raise ValueError(f"Unknown endpoint: {endpoint}")

        # Replace placeholders in the URL with actual parameters
        for key, value in params.items():
            url = url.replace(f"{{{key}}}", str(value))

        # Ensure the final URL is valid
        full_url = urljoin(self.base_url, url)
        return full_url

    def _validate_url(self, url: str):
        """Ensure the URL has a valid scheme and netloc."""
        parsed_url = urlparse(url)
        if not all([parsed_url.scheme, parsed_url.netloc]):
            raise ValueError(
                f"Invalid URL: {url}. It must have a valid scheme and netloc."
            )
        else:
            print(f"Base URL '{url}' validated successfully.")

    def _initialize_versioned_urls(self):
        """Initialize version-specific URLs."""
        if self.version >= "4.0":
            self._initialize_v4_urls()
        else:
            self._initialize_v3_urls()

    def _initialize_v4_urls(self):
        """Define URLs for version 4.x"""
        # Graph Schema URLs
        self.graph_schema_url = "/restpp/graph/{graph_name}/schema"

        # Data Loading URLs
        self.graph_data_loading_url = "/restpp/graph/{graph_name}/jobs/{job_name}"

        # Node Operations URLs
        self.node_insert_url = "/restpp/graph/{graph_name}/vertices"
        self.node_list_url = "/restpp/graph/{graph_name}/vertices/{vertex_type}"
        self.node_retrieve_url = (
            "/restpp/graph/{graph_name}/vertices/{vertex_type}/{vertex_id}"
        )
        self.node_delete_url = "/restpp/graph/{graph_name}/vertices/{vertex_type}"

        # Edge Operations URLs
        self.edge_insert_url = "/restpp/graph/{graph_name}/edges"
        self.edge_list_url = (
            "/restpp/graph/{graph_name}/edges/{vertex_type}/{vertex_id}"
        )
        self.edge_retrieve_url = "/restpp/graph/{graph_name}/edges/{source_vertex_type}/{source_vertex_id}/{edge_type}/{target_vertex_type}/{target_vertex_id}"
        self.edge_delete_url = "/restpp/graph/{graph_name}/edges/{source_vertex_type}/{source_vertex_id}/{edge_type}/{target_vertex_type}/{target_vertex_id}"

        # Graph Queries URLs
        self.query_run_url = "/restpp/query/{graph_name}/{query_name}"
        self.query_metadata_url = "/restpp/query/{graph_name}/{query_name}/status"

        # Graph Statistics URLs
        self.query_info_url = "/restpp/query_info"

        # System Utilities URLs
        self.system_health_check_url = "/api/ping"
        self.system_echo_url = "/restpp/echo"
        self.system_version_url = "/restpp/version"

        # Authentication & Security URLs
        self.auth_request_token_url = "/restpp/requesttoken"

    def _initialize_v3_urls(self):
        """Define URLs for version 3.x"""
        # Graph Schema URLs
        self.graph_schema_url = "/restpp/graph/{graph_name}/schema"

        # Data Loading URLs
        self.graph_data_loading_url = "/restpp/graph/{graph_name}/jobs/{job_name}"

        # Node Operations URLs
        self.node_insert_url = "/restpp/graph/{graph_name}/vertices"
        self.node_list_url = "/restpp/graph/{graph_name}/vertices/{vertex_type}"
        self.node_retrieve_url = (
            "/restpp/graph/{graph_name}/vertices/{vertex_type}/{vertex_id}"
        )
        self.node_delete_url = "/restpp/graph/{graph_name}/vertices/{vertex_type}"

        # Edge Operations URLs
        self.edge_insert_url = "/restpp/graph/{graph_name}/edges"
        self.edge_list_url = (
            "/restpp/graph/{graph_name}/edges/{vertex_type}/{vertex_id}"
        )
        self.edge_retrieve_url = "/restpp/graph/{graph_name}/edges/{source_vertex_type}/{source_vertex_id}/{edge_type}/{target_vertex_type}/{target_vertex_id}"
        self.edge_delete_url = "/restpp/graph/{graph_name}/edges/{source_vertex_type}/{source_vertex_id}/{edge_type}/{target_vertex_type}/{target_vertex_id}"

        # Graph Queries URLs
        self.query_run_url = "/restpp/query/{graph_name}/{query_name}"
        self.query_metadata_url = "/restpp/query/{graph_name}/{query_name}/status"

        # Graph Statistics URLs
        self.query_info_url = "/restpp/query_info"

        # System Utilities URLs
        self.system_health_check_url = "/api/ping"
        self.system_echo_url = "/restpp/echo"
        self.system_version_url = "/restpp/version"

        # Authentication & Security URLs
        self.auth_request_token_url = "/restpp/requesttoken"
