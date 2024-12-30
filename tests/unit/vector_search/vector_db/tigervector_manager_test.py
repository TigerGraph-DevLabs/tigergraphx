import pytest
from unittest.mock import MagicMock
import pandas as pd

from tigergraphx.config import TigerVectorConfig
from tigergraphx.core import Graph
from tigergraphx.vector_search import TigerVectorManager


class TestTigerVectorManager:
    @pytest.fixture(autouse=True)
    def setup(self):
        """Set up a mock context and TigerVectorManager for all tests."""
        # Mock the configuration
        self.mock_config = MagicMock(spec=TigerVectorConfig)
        self.mock_config.vector_attribute_name = "emb_description"
        # Mock the Graph class and its methods
        self.mock_graph = MagicMock(spec=Graph)
        # Instantiate the TigerVectorManager with mock configuration and graph
        self.manager = TigerVectorManager(
            config=self.mock_config, graph=self.mock_graph
        )

    def test_insert_data(self):
        """Test the insert_data method of TigerVectorManager."""
        # Sample DataFrame to insert
        data = pd.DataFrame(
            {
                "__id__": ["Entity_1", "Entity_2"],
                "__vector__": [
                    [-0.01773, -0.01019, -0.01657],
                    [-0.01926, 0.000496, 0.00671],
                ],
            }
        )

        # Call the insert_data method
        self.manager.insert_data(data)

        # Check if add_nodes_from was called with the correct arguments
        expected_nodes = [
            ("Entity_1", {"emb_description": [-0.01773, -0.01019, -0.01657]}),
            ("Entity_2", {"emb_description": [-0.01926, 0.000496, 0.00671]}),
        ]
        self.mock_graph.add_nodes_from.assert_called_once_with(
            nodes_for_adding=expected_nodes, node_type="Entity"
        )

    def test_query(self):
        """Test the query method of TigerVectorManager."""
        # Mock the vector_search method to return fake data
        self.mock_graph.vector_search.return_value = {
            "Entity_1": 0.1,
            "Entity_2": 0.2,
        }

        # Define the query embedding
        query_embedding = [-0.01773, -0.01019, -0.01657]

        # Call the query method
        result = self.manager.query(query_embedding, k=2)

        # Check that the vector_search method was called with the correct parameters
        self.mock_graph.vector_search.assert_called_once_with(
            query_vector=query_embedding,
            vector_attribute_name="emb_description",
            k=2,
        )

        # Assert that the result contains the correct node identifiers
        assert result == ["Entity_1", "Entity_2"]

    def test_query_empty_result(self):
        """Test query method with empty results."""
        # Mock the vector_search method to return an empty dictionary
        self.mock_graph.vector_search.return_value = {}

        # Define the query embedding
        query_embedding = [-0.01773, -0.01019, -0.01657]

        # Call the query method
        result = self.manager.query(query_embedding, k=2)

        # Assert that the result is an empty list since there are no neighbors
        assert result == []

    def test_insert_data_with_empty_df(self):
        """Test insert_data method with an empty DataFrame."""
        # Create an empty DataFrame
        data = pd.DataFrame(columns=pd.Index(["__id__", "__vector__"]))

        # Call insert_data with empty data
        self.manager.insert_data(data)

        # Check that add_nodes_from was not called since there's no data
        self.mock_graph.add_nodes_from.assert_not_called()
