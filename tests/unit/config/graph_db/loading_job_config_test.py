import pytest
from tigergraphx.config import (
    CsvParsingOptions,
    NodeMappingConfig,
    EdgeMappingConfig,
    FileConfig,
    LoadingJobConfig,
    QuoteType,
)


class TestLoadingJobConfig:
    def test_csv_parsing_options_default(self):
        """Test default values for CsvParsingOptions."""
        options = CsvParsingOptions()
        assert options.separator == ","
        assert options.header is True
        assert options.EOL == "\\n"
        assert options.quote == QuoteType.DOUBLE

    def test_node_mapping_config(self):
        """Test NodeMappingConfig initialization."""
        config = NodeMappingConfig(
            target_name="Node1",
            attribute_column_mappings={"id": "id_column", "name": "name_column"},
        )
        assert config.target_name == "Node1"
        assert config.attribute_column_mappings["id"] == "id_column"
        assert config.attribute_column_mappings["name"] == "name_column"

    def test_edge_mapping_config(self):
        """Test EdgeMappingConfig initialization."""
        config = EdgeMappingConfig(
            target_name="Edge1",
            source_node_column="source_column",
            target_node_column="target_column",
            attribute_column_mappings={"weight": "weight_column"},
        )
        assert config.target_name == "Edge1"
        assert config.source_node_column == "source_column"
        assert config.target_node_column == "target_column"
        assert config.attribute_column_mappings["weight"] == "weight_column"

    def test_file_config_valid(self):
        """Test FileConfig with valid node mappings."""
        file_config = FileConfig(
            file_alias="file1",
            file_path="/path/to/file1.csv",
            node_mappings=[
                NodeMappingConfig(
                    target_name="Node1",
                    attribute_column_mappings={"id": "id_column"},
                )
            ],
        )
        assert file_config.file_alias == "file1"
        assert file_config.node_mappings is not None
        assert file_config.node_mappings[0].target_name == "Node1"
        assert (
            file_config.node_mappings[0].attribute_column_mappings["id"] == "id_column"
        )

    def test_file_config_no_mappings(self):
        """Test FileConfig raises error if no mappings are provided."""
        with pytest.raises(
            ValueError,
            match="FileConfig must contain at least one node or edge mapping",
        ):
            FileConfig(
                file_alias="file1",
                file_path="/path/to/file1.csv",
            )

    def test_loading_job_config_valid(self):
        """Test LoadingJobConfig with valid file configurations."""
        file1 = FileConfig(
            file_alias="file1",
            file_path="/path/to/file1.csv",
            node_mappings=[
                NodeMappingConfig(
                    target_name="Node1",
                    attribute_column_mappings={"id": "id_column"},
                )
            ],
        )
        file2 = FileConfig(
            file_alias="file2",
            file_path="/path/to/file2.csv",
            edge_mappings=[
                EdgeMappingConfig(
                    target_name="Edge1",
                    source_node_column="source",
                    target_node_column="target",
                    attribute_column_mappings={"weight": "weight_column"},
                )
            ],
        )
        loading_job = LoadingJobConfig(loading_job_name="job1", files=[file1, file2])
        assert loading_job.loading_job_name == "job1"
        assert len(loading_job.files) == 2
        assert loading_job.files[0].file_alias == "file1"

    def test_loading_job_config_duplicate_file_aliases(self):
        """Test LoadingJobConfig raises error if duplicate file_aliases are found."""
        file1 = FileConfig(
            file_alias="file1",
            file_path="/path/to/file1.csv",
            node_mappings=[
                NodeMappingConfig(
                    target_name="Node1",
                    attribute_column_mappings={"id": "id_column"},
                )
            ],
        )
        file2 = FileConfig(
            file_alias="file1",  # Duplicate file_alias
            file_path="/path/to/file2.csv",
            edge_mappings=[
                EdgeMappingConfig(
                    target_name="Edge1",
                    source_node_column="source",
                    target_node_column="target",
                    attribute_column_mappings={"weight": "weight_column"},
                )
            ],
        )
        with pytest.raises(
            ValueError, match="Duplicate file_alias values found in files"
        ):
            LoadingJobConfig(loading_job_name="job1", files=[file1, file2])

    def test_loading_job_config_from_dict(self):
        """Test LoadingJobConfig initialization from a nested dictionary."""
        config_dict = {
            "loading_job_name": "complex_job",
            "files": [
                {
                    "file_alias": "file1",
                    "file_path": "/path/to/file1.csv",
                    "csv_parsing_options": {
                        "separator": "|",
                        "header": True,
                        "EOL": "\\n",
                        "quote": "SINGLE",
                    },
                    "node_mappings": [
                        {
                            "target_name": "Node1",
                            "attribute_column_mappings": {
                                "id": "id_column",
                                "name": "name_column",
                            },
                        }
                    ],
                },
                {
                    "file_alias": "file2",
                    "file_path": "/path/to/file2.csv",
                    "csv_parsing_options": {
                        "separator": ",",
                        "header": False,
                    },
                    "edge_mappings": [
                        {
                            "target_name": "Edge1",
                            "source_node_column": "source",
                            "target_node_column": "target",
                            "attribute_column_mappings": {
                                "weight": "weight_column",
                            },
                        }
                    ],
                },
            ],
        }

        # Load configuration using ensure_config
        loading_job_config = LoadingJobConfig.ensure_config(config_dict)

        # Assertions for top-level LoadingJobConfig
        assert loading_job_config.loading_job_name == "complex_job"
        assert len(loading_job_config.files) == 2

        # Assertions for File 1
        file1 = loading_job_config.files[0]
        assert file1.file_alias == "file1"
        assert file1.csv_parsing_options.separator == "|"
        assert file1.csv_parsing_options.quote == QuoteType.SINGLE
        assert file1.node_mappings is not None
        assert len(file1.node_mappings) == 1
        assert file1.node_mappings[0].target_name == "Node1"
        assert file1.node_mappings[0].attribute_column_mappings["id"] == "id_column"

        # Assertions for File 2
        file2 = loading_job_config.files[1]
        assert file2.file_alias == "file2"
        assert file2.csv_parsing_options.separator == ","
        assert file2.csv_parsing_options.header is False
        assert file2.edge_mappings is not None
        assert len(file2.edge_mappings) == 1
        assert file2.edge_mappings[0].target_name == "Edge1"
        assert file2.edge_mappings[0].source_node_column == "source"
        assert (
            file2.edge_mappings[0].attribute_column_mappings["weight"]
            == "weight_column"
        )
