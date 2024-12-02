from typing import Dict
from pathlib import Path

from tigergraphx.config import (
    Settings,
    LanceDBConfig,
    OpenAIConfig,
    OpenAIEmbeddingConfig,
    OpenAIChatConfig,
)
from tigergraphx.llm import (
    OpenAIManager,
    OpenAIChat,
)
from tigergraphx.vector_search import (
    OpenAIEmbedding,
    LanceDBManager,
    LanceDBSearchEngine,
)


def create_openai_components(
    config: Settings | Path | str | Dict,
) -> tuple[OpenAIChat, LanceDBSearchEngine]:
    """
    Creates an OpenAIChat instance and a LanceDBSearchEngine from a shared configuration.
    Reuses the same OpenAIManager instance for both components.
    """
    # Ensure configuration is a Settings instance
    settings = Settings.ensure_config(config)

    # Validate configuration types
    if not isinstance(settings.vector_db, LanceDBConfig):
        raise TypeError("Expected `vector_db` to be an instance of LanceDBConfig.")
    if not isinstance(settings.llm, OpenAIConfig):
        raise TypeError("Expected `llm` to be an instance of OpenAIConfig.")
    if not isinstance(settings.embedding, OpenAIEmbeddingConfig):
        raise TypeError(
            "Expected `embedding` to be an instance of OpenAIEmbeddingConfig."
        )
    if not isinstance(settings.chat, OpenAIChatConfig):
        raise TypeError("Expected `chat` to be an instance of OpenAIChatConfig.")

    # Initialize shared OpenAIManager
    llm_manager = OpenAIManager(settings.llm)

    # Initialize OpenAIChat
    openai_chat = OpenAIChat(
        llm_manager=llm_manager,
        config=settings.chat,
    )

    # Initialize LanceDB components
    embedding = OpenAIEmbedding(llm_manager, settings.embedding)
    lancedb_manager = LanceDBManager(settings.vector_db)

    # Initialize LanceDBSearchEngine
    lancedb_search_engine = LanceDBSearchEngine(embedding, lancedb_manager)

    # Return both instances
    return openai_chat, lancedb_search_engine
