from typing import Dict, Optional
from pathlib import Path

from tigergraphx.core import Graph
from tigergraphx.config import (
    Settings,
    TigerVectorConfig,
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
    TigerVectorManager,
    LanceDBManager,
    TigerVectorSearchEngine,
    LanceDBSearchEngine,
)


def create_openai_components(
    config: Settings | Path | str | Dict, graph: Optional[Graph] = None
) -> tuple[OpenAIChat, TigerVectorSearchEngine | LanceDBSearchEngine]:
    """
    Creates an OpenAIChat instance and a TigerVectorSearchEngine or LanceDBSearchEngine
    from a shared configuration. Reuses the same OpenAIManager instance for both components.
    """
    # Ensure configuration is a Settings instance
    settings = Settings.ensure_config(config)

    # Validate configuration types
    if not isinstance(settings.vector_db, (TigerVectorConfig, LanceDBConfig)):
        raise TypeError(
            "Expected `vector_db` to be an instance of TigerVectorConfig or LanceDBConfig."
        )
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

    embedding = OpenAIEmbedding(llm_manager, settings.embedding)
    if isinstance(settings.vector_db, TigerVectorConfig):
        if graph is None:
            raise ValueError("Graph cannot be None when TigerVector is used.")
        tigervector_manager = TigerVectorManager(settings.vector_db, graph)
        search_engine = TigerVectorSearchEngine(embedding, tigervector_manager)
    else:
        lancedb_manager = LanceDBManager(settings.vector_db)
        search_engine = LanceDBSearchEngine(embedding, lancedb_manager)

    # Return both instances
    return openai_chat, search_engine
