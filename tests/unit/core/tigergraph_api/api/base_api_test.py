import pytest
from unittest.mock import MagicMock
from requests.exceptions import (
    ConnectionError,
    HTTPError,
    Timeout,
    TooManyRedirects,
    URLRequired,
    InvalidURL,
    MissingSchema,
    InvalidSchema,
    ChunkedEncodingError,
    ContentDecodingError,
    RequestException,
)
from tigergraphx.core.tigergraph_api.api.base_api import BaseAPI
from tigergraphx.config import TigerGraphConnectionConfig


class TestBaseAPI:
    @pytest.fixture
    def mock_config(self):
        """Fixture for TigerGraphConnectionConfig with mock values."""
        return TigerGraphConnectionConfig()

    @pytest.fixture
    def mock_session(self):
        """Fixture for mocking a requests.Session object."""
        return MagicMock()

    @pytest.fixture
    def mock_registry(self):
        """Fixture for mocking an EndpointRegistry."""
        mock_registry = MagicMock()

        def get_endpoint(name, version, **kwargs):
            graph_name = kwargs.get("graph", "DefaultGraph")
            return {
                "path": f"/gsql/v1/schema/graphs/{graph_name}",
                "method": "GET",
                "port": "gsql_port",
            }

        mock_registry.get_endpoint.side_effect = get_endpoint
        return mock_registry

    @pytest.fixture
    def base_api(self, mock_config, mock_session, mock_registry):
        """Fixture for initializing BaseAPI with mocked dependencies."""
        return BaseAPI(
            config=mock_config, endpoint_registry=mock_registry, session=mock_session
        )

    def test_request_success_json(self, base_api, mock_session):
        """Test a successful JSON response with results."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "error": False,
            "message": "",
            "results": {"GraphName": "MyGraph", "VertexTypes": [], "EdgeTypes": []},
        }
        mock_response.headers = {"Content-Type": "application/json"}
        mock_response.status_code = 200
        mock_session.request.return_value = mock_response

        result = base_api._request("get_schema", "4.x", graph="MyGraph")

        assert result == {"GraphName": "MyGraph", "VertexTypes": [], "EdgeTypes": []}

    def test_request_success_json_no_results(self, base_api, mock_session):
        """Test JSON response with an empty results field, should return message."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "error": False,
            "message": "Schema retrieved successfully.",
            "results": None,
        }
        mock_response.headers = {"Content-Type": "application/json"}
        mock_response.status_code = 200
        mock_session.request.return_value = mock_response

        result = base_api._request("get_schema", "4.x", graph="MyGraph")

        assert result == {"message": "Schema retrieved successfully."}

    def test_request_success_text(self, base_api, mock_session):
        """Test a successful plain text response."""
        mock_response = MagicMock()
        mock_response.text = "Some text response"
        mock_response.headers = {"Content-Type": "text/plain"}
        mock_response.status_code = 200
        mock_session.request.return_value = mock_response

        result = base_api._request("get_schema", "4.x", graph="MyGraph")

        assert result == {"text": "Some text response"}

    def test_request_text_plain_error(self, base_api, mock_session):
        """Test a failed plain text response that should raise an HTTPError with details."""
        mock_response = MagicMock()
        mock_response.text = "Invalid command"
        mock_response.headers = {"Content-Type": "text/plain"}
        mock_response.status_code = 400  # Bad Request
        mock_response.reason = "Bad Request"
        mock_response.url = "http://127.0.0.1:14240/gsql/v1/statements"
        mock_response.raise_for_status.side_effect = HTTPError(
            "400 Bad Request", response=mock_response
        )
        mock_session.request.return_value = mock_response

        expected_error = "HTTP request failed: 400 Bad Request: The request was invalid. Check syntax or parameters. URL: http://127.0.0.1:14240/gsql/v1/statements."

        with pytest.raises(RuntimeError, match=expected_error):
            base_api._request("gsql", "4.x")

    def test_request_unsupported_content_type(self, base_api, mock_session):
        """Test when TigerGraph returns an unknown content type."""
        mock_response = MagicMock()
        mock_response.headers = {"Content-Type": "application/xml"}
        mock_response.status_code = 200
        mock_response.reason = "OK"
        mock_response.url = "http://127.0.0.1:14240/gsql/v1/schema/graphs/MyGraph"
        mock_session.request.return_value = mock_response

        expected_error = "Unsupported content type: application/xml"

        with pytest.raises(ValueError, match=expected_error):
            base_api._request("get_schema", "4.x", graph="MyGraph")

    @pytest.mark.parametrize(
        "exception, expected_error, expected_exception",
        [
            (
                ConnectionError("Connection failed"),
                "Failed to connect to TigerGraph",
                ConnectionError,
            ),
            (
                HTTPError("HTTP 500 Internal Server Error"),
                "HTTP request failed",
                RuntimeError,
            ),
            (Timeout("Request timed out"), "Request timed out", TimeoutError),
            (
                TooManyRedirects("Too many redirects"),
                "Too many redirects",
                RuntimeError,
            ),
            (URLRequired("URL required"), "Invalid request URL", ValueError),
            (InvalidURL("Invalid URL"), "Invalid request URL", ValueError),
            (MissingSchema("Missing schema"), "Invalid request URL", ValueError),
            (InvalidSchema("Invalid schema"), "Invalid request URL", ValueError),
            (
                ChunkedEncodingError("Chunk decoding failed"),
                "Failed to decode response",
                RuntimeError,
            ),
            (
                ContentDecodingError("Content decoding failed"),
                "Failed to decode response",
                RuntimeError,
            ),
            (RequestException("Generic request error"), "Request error", RuntimeError),
        ],
    )
    def test_request_exceptions(
        self, base_api, mock_session, exception, expected_error, expected_exception
    ):
        """Test handling of various request exceptions."""
        mock_session.request.side_effect = exception
        with pytest.raises(expected_exception, match=expected_error):
            base_api._request("get_schema", "4.x", graph="MyGraph")

    def test_request_tigergraph_error(self, base_api, mock_session):
        """Test when TigerGraph API returns an error message."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "error": True,
            "message": "Graph does not exist.",
        }
        mock_response.headers = {"Content-Type": "application/json"}
        mock_response.status_code = 400
        mock_session.request.return_value = mock_response

        with pytest.raises(
            ValueError, match="TigerGraph API Error: Graph does not exist."
        ):
            base_api._request("get_schema", "4.x", graph="InvalidGraph")
