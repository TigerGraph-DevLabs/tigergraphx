import pytest
from unittest.mock import MagicMock

from tigergraphx.config import LoadingJobConfig, GraphSchema
from tigergraphx.core.managers.data_manager import DataManager


class TestDataManager:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.mock_connection = MagicMock()
        self.mock_connection.gsql = MagicMock()

        mock_context = MagicMock()
        mock_context.connection = self.mock_connection  # Use the mocked connection
        mock_context.graph_schema = GraphSchema(
            graph_name="MyGraph", nodes={}, edges={}
        )
        self.data_manager = DataManager(mock_context)

    def test_load_data_success(self):
        loading_job_config = LoadingJobConfig(loading_job_name="test_job", files=[])
        # Mock the gsql return value to simulate a successful load process
        self.mock_connection.gsql.return_value = (
            "Using graph 'MyGraph'...\n"
            "Successfully created loading jobs:\n"
            "LOAD SUCCESSFUL for loading jobid\n"
            "Successfully dropped jobs"
        )
        self.data_manager.load_data(loading_job_config)

        # Assert the gsql method was called once
        self.mock_connection.gsql.assert_called_once()

    def test_load_data_failure(self):
        loading_job_config = LoadingJobConfig(loading_job_name="test_job", files=[])
        # Mock the gsql return value for failure
        self.mock_connection.gsql.return_value = "LOAD FAILED"

        # Assert that RuntimeError is raised on failure
        with pytest.raises(RuntimeError):
            self.data_manager.load_data(loading_job_config)
