import os
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
        api_key = os.getenv("OPENAI_API_KEY")
        assert api_key is not None
        llm_manager = OpenAIManager(
            OpenAIConfig(type="OpenAI", OPENAI_API_KEY=api_key)
        )
        embedding = OpenAIEmbedding(
            llm_manager, OpenAIEmbeddingConfig(type="OpenAI")
        )
        result = await embedding.generate_embedding("ABC")
        assert len(result) == 1536
