from unittest.mock import MagicMock
from tigergraphx.vector_search.search.lancedb_search_engine import LanceDBSearchEngine
from tigergraphx.vector_search import OpenAIEmbedding, LanceDBManager


class TestLanceDBSearchEngine:
    def test_initialization(self):
        # Mock the OpenAIEmbedding and LanceDBManager
        mock_embedding_model = MagicMock(spec=OpenAIEmbedding)
        mock_vector_db = MagicMock(spec=LanceDBManager)

        # Instantiate LanceDBSearchEngine with the mocked dependencies
        search_engine = LanceDBSearchEngine(
            embedding_model=mock_embedding_model, vector_db=mock_vector_db
        )

        # Assert that the search engine is initialized with the correct attributes
        assert search_engine.embedding_model == mock_embedding_model
        assert search_engine.vector_db == mock_vector_db
