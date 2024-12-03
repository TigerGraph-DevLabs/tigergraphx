import pytest

from tigergraphx import (
    Settings,
    LanceDBConfig,
    OpenAIConfig,
    OpenAIEmbeddingConfig,
    OpenAIChatConfig,
)


class TestSettings:
    """Test suite for the Settings configuration class."""

    @pytest.fixture
    def set_valid_env_vars(self, monkeypatch):
        """Set up valid environment variables for testing."""
        monkeypatch.setenv("OPENAI_API_KEY", "test_api_key")

    def test_settings_from_dict(self, set_valid_env_vars):
        """Test the full Settings class with valid configurations."""
        config_data = {
            "vector_db": {"type": "LanceDB", "uri": "test_uri"},
            "llm": {"type": "OpenAI", "base_url": "https://api.openai.com"},
            "embedding": {"type": "OpenAI", "model": "text-embedding-3-small"},
            "chat": {"type": "OpenAI", "model": "gpt-4o-mini", "max_retries": 10},
        }
        settings = Settings.ensure_config(config_data)

        # Validate vector_db configuration
        assert settings.vector_db.type == "LanceDB"
        assert isinstance(settings.vector_db, LanceDBConfig)
        assert settings.vector_db.uri == "test_uri"

        # Validate llm configuration
        assert settings.llm.type == "OpenAI"
        assert isinstance(settings.llm, OpenAIConfig)
        assert settings.llm.api_key == "test_api_key"  # from environment
        assert settings.llm.base_url == "https://api.openai.com"
        assert settings.llm.max_retries == 10

        # Validate embedding configuration
        assert settings.embedding.type == "OpenAI"
        assert isinstance(settings.embedding, OpenAIEmbeddingConfig)
        assert settings.embedding.model == "text-embedding-3-small"
        assert settings.embedding.max_tokens == 8191

        # Validate chat configuration
        assert settings.chat.type == "OpenAI"
        assert isinstance(settings.chat, OpenAIChatConfig)
        assert settings.chat.model == "gpt-4o-mini"
        assert settings.chat.max_retries == 10

    def test_settings_from_file(self, set_valid_env_vars):
        # Load the configuration from the YAML file
        settings = Settings.ensure_config(config="tests/resources/settings.yaml")

        # Validate vector_db configuration
        assert settings.vector_db.type == "LanceDB"
        assert isinstance(settings.vector_db, LanceDBConfig)
        assert settings.vector_db.uri == "test_uri"

        # Validate llm configuration
        assert settings.llm.type == "OpenAI"
        assert isinstance(settings.llm, OpenAIConfig)
        assert settings.llm.api_key == "test_api_key"  # from environment
        assert settings.llm.base_url is None
        assert settings.llm.max_retries == 10

        # Validate embedding configuration
        assert settings.embedding.type == "OpenAI"
        assert isinstance(settings.embedding, OpenAIEmbeddingConfig)
        assert settings.embedding.model == "text-embedding-3-small"
        assert settings.embedding.max_tokens == 8191

        # Validate chat configuration
        assert settings.chat.type == "OpenAI"
        assert isinstance(settings.chat, OpenAIChatConfig)
        assert settings.chat.model == "gpt-4o-mini"
        assert settings.chat.max_retries == 10
