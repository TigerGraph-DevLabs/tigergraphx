from enum import Enum
from typing import Optional, Dict, List
from pydantic import model_validator

from tigergraphx.config import BaseConfig


class QuoteType(Enum):
    DOUBLE = "DOUBLE"
    SINGLE = "SINGLE"


class CsvParsingOptions(BaseConfig):
    separator: str = ","
    header: bool = True
    EOL: str = "\\n"
    quote: Optional[QuoteType] = QuoteType.DOUBLE


class NodeMappingConfig(BaseConfig):
    target_name: str
    attribute_column_mappings: Dict[str, str | int] = {}


class EdgeMappingConfig(BaseConfig):
    target_name: str
    source_node_column: str | int
    target_node_column: str | int
    attribute_column_mappings: Dict[str, str | int] = {}


class FileConfig(BaseConfig):
    file_alias: str
    file_path: Optional[str] = None
    csv_parsing_options: CsvParsingOptions = CsvParsingOptions()
    node_mappings: Optional[List[NodeMappingConfig]] = None
    edge_mappings: Optional[List[EdgeMappingConfig]] = None

    @model_validator(mode="after")
    def validate_mappings(cls, values):
        """
        Ensure that at least one mapping (node or edge) exists.
        """
        n_node_mappings = len(values.node_mappings) if values.node_mappings else 0
        n_edge_mappings = len(values.edge_mappings) if values.edge_mappings else 0
        if n_node_mappings + n_edge_mappings == 0:
            raise ValueError(
                "FileConfig must contain at least one node or edge mapping in 'node_mappings' "
                "or 'edge_mappings'."
            )
        return values


class LoadingJobConfig(BaseConfig):
    loading_job_name: str
    files: List[FileConfig]

    @model_validator(mode="after")
    def validate_file_aliases(cls, values):
        """
        Ensure that all file_alias values are unique.
        """
        file_aliases = [file.file_alias for file in values.files]
        duplicates = {alias for alias in file_aliases if file_aliases.count(alias) > 1}
        if duplicates:
            raise ValueError(
                f"Duplicate file_alias values found in files: {', '.join(duplicates)}"
            )
        return values
