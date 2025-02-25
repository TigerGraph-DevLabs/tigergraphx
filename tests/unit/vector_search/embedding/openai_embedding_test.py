from unittest.mock import AsyncMock, patch
import pytest

from tigergraphx.config import (
    OpenAIEmbeddingConfig,
    OpenAIConfig,
)
from tigergraphx.vector_search import OpenAIEmbedding


class TestOpenAIEmbedding:
    @pytest.mark.asyncio
    async def test_generate_embedding(self):
        # Mock OpenAIManager and its methods
        with patch("tigergraphx.llm.OpenAIManager", autospec=True) as MockOpenAIManager:
            # Configure the mock OpenAIManager
            mock_manager = MockOpenAIManager.return_value
            mock_manager.config = OpenAIConfig(type="OpenAI", OPENAI_API_KEY="mock_key")

            # Mock the _generate_with_retry method in OpenAIEmbedding
            with patch.object(
                OpenAIEmbedding, "_generate_with_retry", new=AsyncMock()
            ) as mock_generate_with_retry:
                # Simulate a mocked embedding result for a token chunk
                mock_generate_with_retry.return_value = ([0.1] * 1536, 1)

                # Initialize OpenAIEmbedding with the mocked manager
                embedding = OpenAIEmbedding(
                    mock_manager, OpenAIEmbeddingConfig(type="OpenAI")
                )

                # Test the generate_embedding method
                result = await embedding.generate_embedding("ABC")

                # Assertions
                assert len(result) == 1536  # Check the embedding length
                assert all(
                    isinstance(value, float) for value in result
                )  # Check data type
                mock_generate_with_retry.assert_called_once()  # Ensure the mock was called
