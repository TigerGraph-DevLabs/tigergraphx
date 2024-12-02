import pytest
from unittest.mock import AsyncMock, MagicMock

from tigergraphx.config import OpenAIChatConfig
from tigergraphx.llm import (
    OpenAIManager,
    OpenAIChat,
)


class TestOpenAIChat:
    """Test suite for the OpenAIChat class."""

    @pytest.fixture
    def mock_llm_manager(self):
        """Fixture to mock OpenAIManager."""
        manager = MagicMock(spec=OpenAIManager)
        mock_llm = MagicMock()
        manager.get_llm.return_value = mock_llm
        return manager

    @pytest.fixture
    def mock_retryer(self):
        """Fixture to mock the retryer."""
        retryer = MagicMock()
        retryer.__aiter__.return_value = [MagicMock()]
        return retryer

    @pytest.fixture
    def mock_config(self):
        """Fixture to provide a mock OpenAIChatConfig."""
        return OpenAIChatConfig(
            type="OpenAI",
            model="gpt-4",
            max_retries=3,
        )

    @pytest.fixture
    def openai_chat(self, mock_llm_manager, mock_config, mock_retryer):
        """Fixture to initialize OpenAIChat with mocked dependencies."""
        chat_instance = OpenAIChat(mock_llm_manager, mock_config)
        chat_instance.retryer = mock_retryer
        return chat_instance

    @pytest.mark.asyncio
    async def test_chat_success(self, openai_chat):
        """Test the chat method for a successful response."""
        # Mock the API response
        mock_response = MagicMock()
        mock_response.choices = [MagicMock(message=MagicMock(content="Test response"))]
        openai_chat.llm.chat.completions.create = AsyncMock(return_value=mock_response)

        # Mock input messages
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Tell me a joke."},
        ]

        # Call the method
        result = await openai_chat.chat(messages)

        # Assertions
        assert result == "Test response"
        openai_chat.llm.chat.completions.create.assert_awaited_once_with(
            messages=messages, model="gpt-4"
        )
