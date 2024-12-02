import pytest
from unittest.mock import MagicMock
from openai import AsyncOpenAI
from pydantic import ValidationError

from tigergraphx.llm.openai_manager import OpenAIManager
from tigergraphx.config import OpenAIConfig


class TestOpenAIManager:
    """Test suite for the OpenAIManager class."""

    @pytest.fixture
    def valid_config_dict(self):
        """Fixture to provide a valid OpenAI configuration as a dictionary."""
        return {
            "type": "OpenAI",
            "OPENAI_API_KEY": "test-api-key",
            "base_url": "https://api.openai.com/v1",
            "organization": "test-org",
            "max_retries": 5,
            "request_timeout": 60.0,
        }

    @pytest.fixture
    def valid_config(self, valid_config_dict):
        """Fixture to provide a valid OpenAIConfig object."""
        return OpenAIConfig(**valid_config_dict)

    @pytest.fixture
    def mock_async_openai(self, monkeypatch):
        """Fixture to mock the AsyncOpenAI class."""
        mock_openai = MagicMock(spec=AsyncOpenAI)
        monkeypatch.setattr("tigergraphx.llm.openai_manager.AsyncOpenAI", mock_openai)
        return mock_openai

    def test_init_with_valid_config(self, valid_config, mock_async_openai):
        """Test initialization with a valid OpenAIConfig."""
        manager = OpenAIManager(valid_config)

        # Assert that AsyncOpenAI was initialized correctly
        mock_async_openai.assert_called_once_with(
            api_key="test-api-key",
            base_url="https://api.openai.com/v1",
            organization="test-org",
            timeout=60.0,
            max_retries=5,
        )
        # Assert that the manager's LLM is set
        assert manager.get_llm() == mock_async_openai.return_value

    def test_init_with_config_dict(self, valid_config_dict, mock_async_openai):
        """Test initialization with a configuration dictionary."""
        manager = OpenAIManager(valid_config_dict)

        # Assert that AsyncOpenAI was initialized correctly
        mock_async_openai.assert_called_once_with(
            api_key="test-api-key",
            base_url="https://api.openai.com/v1",
            organization="test-org",
            timeout=60.0,
            max_retries=5,
        )
        # Assert that the manager's LLM is set
        assert manager.get_llm() == mock_async_openai.return_value

    def test_init_with_config_file(
        self, tmp_path, valid_config_dict, mock_async_openai
    ):
        """Test initialization with a configuration file."""
        # Write the configuration to a JSON file
        config_file = tmp_path / "config.json"
        config_file.write_text(str(valid_config_dict).replace("'", '"'))

        # Initialize the manager with the file path
        manager = OpenAIManager(config_file)

        # Assert that AsyncOpenAI was initialized correctly
        mock_async_openai.assert_called_once_with(
            api_key="test-api-key",
            base_url="https://api.openai.com/v1",
            organization="test-org",
            timeout=60.0,
            max_retries=5,
        )
        # Assert that the manager's LLM is set
        assert manager.get_llm() == mock_async_openai.return_value

    def test_init_without_api_key_raises_error(self, valid_config_dict, monkeypatch):
        """Test initialization without an API key raises a ValidationError."""
        # Remove the OPENAI_API_KEY from the environment
        monkeypatch.delenv("OPENAI_API_KEY", raising=False)

        # Remove the API key from the configuration
        valid_config_dict.pop("OPENAI_API_KEY", None)

        # Assert that ValidationError is raised
        with pytest.raises(ValidationError, match="Field required"):
            OpenAIManager(valid_config_dict)

    def test_get_llm(self, valid_config, mock_async_openai):
        """Test the get_llm method."""
        manager = OpenAIManager(valid_config)

        # Assert that get_llm returns the correct AsyncOpenAI instance
        assert manager.get_llm() == mock_async_openai.return_value
