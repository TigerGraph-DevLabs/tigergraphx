import re
from pathlib import Path
from typing import Any, Dict, List
import pandas as pd


class ParquetProcessor:
    """
    A class to process Parquet files and generate CSV files with custom transformations.
    """

    def __init__(self, input_dir: str | Path, output_dir: str | Path):
        """
        Initialize the ParquetProcessor with input and output directories.

        Args:
            input_dir: Directory containing the input Parquet files.
            output_dir: Directory to save the output CSV files.
        """
        self.input_dir: Path = Path(input_dir).resolve()
        self.output_dir: Path = Path(output_dir).resolve()
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def save_dataframe_to_csv(self, df: pd.DataFrame | pd.Series, csv_file_name: str):
        """
        Save a DataFrame or Series to a CSV file with specific formatting.

        Args:
            df: The DataFrame or Series to save.
            csv_file_name: Name of the output CSV file.
        """
        df = df.apply(
            lambda col: col.str.replace("\n", "\\n") if col.dtype == "object" else col
        )
        csv_file_path = self.output_dir / csv_file_name
        df.to_csv(csv_file_path, index=False)

        with open(csv_file_path, "r") as file:
            content = file.read()
        content = re.sub(r'(?<![,])""(?![,])', r'\\"', content)
        with open(csv_file_path, "w") as file:
            file.write(content)

    def convert_parquet_to_csv(
        self,
        parquet_file_name: str,
        columns: List[str],
        csv_file_name: str,
    ):
        """
        Convert a Parquet file to a CSV file with specific columns.

        Args:
            parquet_file_name: Name of the input Parquet file.
            columns: List of columns to include in the output CSV.
            csv_file_name: Name of the output CSV file.
        """
        input_file_path = self.input_dir / parquet_file_name
        df = pd.read_parquet(input_file_path)[columns]
        self.save_dataframe_to_csv(df, csv_file_name)

    def create_relationship_file(
        self,
        df: pd.DataFrame,
        element_list_name: str,
        element_name: str,
        collection_name: str,
        collection_new_name: str,
        output_name: str,
    ):
        """
        Generate a CSV file for relationship mapping based on input DataFrame.

        Args:
            df: Input DataFrame containing relationship data.
            element_list_name: Name of the column containing element lists.
            element_name: Name of the element to map.
            collection_name: Name of the collection column.
            collection_new_name: New name for the collection in the output.
            output_name: Name of the output CSV file.
        """
        relationships = [
            {element_name: element, collection_new_name: row[collection_name]}
            for _, row in df.iterrows()
            for element in row[element_list_name]
        ]
        rel_df = pd.DataFrame(relationships)
        self.save_dataframe_to_csv(rel_df, output_name)

    def process_parquet_files(self, configs: List[Dict[str, Any]]):
        """
        Process a list of Parquet file configurations and convert them to CSV.

        Args:
            configs: List of configuration dictionaries for processing Parquet files.
        """
        for config in configs:
            self.convert_parquet_to_csv(
                config["parquet_file"], config["columns"], config["csv_file"]
            )

    def process_relationship_files(self, configs: List[Dict[str, Any]]):
        """
        Process a list of relationship file configurations and generate CSV files.

        Args:
            configs: List of configuration dictionaries for generating relationship files.
        """
        for config in configs:
            df = pd.read_parquet(self.input_dir / config["parquet_file"])
            self.create_relationship_file(
                df,
                config["element_list_name"],
                config["element_name"],
                config["collection_name"],
                config["collection_new_name"],
                config["output_name"],
            )
