# Copyright 2025 TigerGraph Inc.
# Licensed under the Apache License, Version 2.0.
# See the LICENSE file or https://www.apache.org/licenses/LICENSE-2.0
#
# Permission is granted to use, copy, modify, and distribute this software
# under the License. The software is provided "AS IS", without warranty.

import logging
from typing import List, Dict, Tuple, Generator
from pathlib import Path
import numpy as np
import asyncio
import tiktoken
from tenacity import RetryError

from .base_embedding import BaseEmbedding

from tigergraphx.config import OpenAIEmbeddingConfig
from tigergraphx.llm import OpenAIManager
from tigergraphx.utils import RetryMixin

logger = logging.getLogger(__name__)


class OpenAIEmbedding(BaseEmbedding, RetryMixin):
    """OpenAI Embedding model wrapper with async embedding generation and robust retries."""

    config: OpenAIEmbeddingConfig

    def __init__(
        self,
        llm_manager: OpenAIManager,
        config: OpenAIEmbeddingConfig | Dict | str | Path,
    ):
        """
        Initialize the OpenAI Embedding wrapper.

        Args:
            llm_manager: Manager for OpenAI LLM interactions.
            config: Configuration for the embedding model.
        """
        config = OpenAIEmbeddingConfig.ensure_config(config)
        super().__init__(config)
        self.llm = llm_manager.get_llm()
        self.token_encoder = tiktoken.get_encoding(config.encoding_name)
        self.retryer = self.initialize_retryer(self.config.max_retries, max_wait=10)

    async def generate_embedding(self, text: str) -> List[float]:
        """
        Generate embedding asynchronously with retry for robustness.

        Args:
            text: The input text to generate embeddings for.

        Returns:
            The normalized embedding vector.
        """
        token_chunks = list(self._tokenize(text))
        embedding_results = await asyncio.gather(
            *[self._generate_with_retry(chunk) for chunk in token_chunks]
        )

        embeddings, lengths = (
            zip(*[(emb, length) for emb, length in embedding_results if emb])
            if embedding_results
            else ([], [])
        )

        if not embeddings:
            return []

        combined_embedding = np.average(embeddings, axis=0, weights=lengths)
        normalized_embedding = combined_embedding / np.linalg.norm(combined_embedding)
        return normalized_embedding.tolist()

    async def _generate_with_retry(self, text: str) -> Tuple[List[float], int]:
        """
        Fetch embedding for a chunk with retry, returning empty list on failure.

        Args:
            text: Text chunk to generate embeddings for.

        Returns:
            The embedding vector and the length of the chunk.
        """
        try:
            async for attempt in self.retryer:
                with attempt:
                    embedding = (
                        await self.llm.embeddings.create(
                            input=text,
                            model=self.config.model,
                        )
                    ).data[0].embedding or []
                    return embedding, len(text)
        except RetryError as e:
            logger.error(
                f"RetryError in _generate_with_retry for text chunk: {text[:50]}... | {e}"
            )

        return [], 0

    def _tokenize(self, text: str) -> List[str]:
        """
        Tokenize text into chunks based on token length.

        Args:
            text: The input text to tokenize.

        Returns:
            List of tokenized text chunks.
        """
        tokens = self.token_encoder.encode(text)
        return [
            self.token_encoder.decode(chunk) for chunk in self._batch_tokens(tokens)
        ]

    def _batch_tokens(self, tokens: List[int]) -> Generator[List[int], None, None]:
        """
        Yield successive batches of tokens up to max_tokens.

        Args:
            tokens: List of token IDs.

        Yields:
            Batches of token IDs.
        """
        for i in range(0, len(tokens), self.config.max_tokens):
            yield tokens[i : i + self.config.max_tokens]
