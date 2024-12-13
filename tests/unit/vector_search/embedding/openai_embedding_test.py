from unittest.mock import AsyncMock, MagicMock, patch
import pytest

from tigergraphx import (
    OpenAIEmbedding,
    OpenAIEmbeddingConfig,
    OpenAIManager,
    OpenAIConfig,
)


class TestOpenAIEmbedding:
    @pytest.mark.asyncio
    async def test_generate_embedding(self):
        # Mock OpenAIManager and its behavior
        mock_llm_manager = MagicMock(spec=OpenAIManager)
        mock_llm_manager.config = OpenAIConfig(type="OpenAI", OPENAI_API_KEY="mock_key")

        # Mock the internal _generate_with_retry method in OpenAIEmbedding
        with patch.object(
            OpenAIEmbedding, "_generate_with_retry", new=AsyncMock()
        ) as mock_generate_with_retry:
            # Simulate a mocked embedding result for a token chunk
            mock_generate_with_retry.return_value = ([0.1] * 1536, 1)

            # Initialize OpenAIEmbedding with the mocked manager
            embedding = OpenAIEmbedding(
                mock_llm_manager, OpenAIEmbeddingConfig(type="OpenAI")
            )

            # Test the generate_embedding method
            result = await embedding.generate_embedding("ABC")

            # Assertions
            assert len(result) == 1536  # Check the embedding length
            assert all(isinstance(value, float) for value in result)  # Check data type
            mock_generate_with_retry.assert_called_once()  # Ensure the mock was called
