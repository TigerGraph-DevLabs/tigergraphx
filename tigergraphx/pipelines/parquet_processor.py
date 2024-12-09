import re
from pathlib import Path
from typing import List, Dict, Any
import pandas as pd


class ParquetProcessor:
    def __init__(self, input_dir: str | Path, output_dir: str | Path):
        self.input_dir: Path = Path(input_dir).resolve()
        self.output_dir: Path = Path(output_dir).resolve()
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def save_dataframe_to_csv(self, df: pd.DataFrame | pd.Series, csv_file_name: str):
        """Save DataFrame to CSV with consistent parameters for index, escapechar, and newline handling."""
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
        self, parquet_file_name: str, columns: List[str], csv_file_name: str
    ):
        """Read a Parquet file, select specific columns, and save as a CSV."""
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
        """Generate a CSV file for a relationship mapping from a given column."""
        relationships = [
            {element_name: element, collection_new_name: row[collection_name]}
            for _, row in df.iterrows()
            for element in row[element_list_name]
        ]
        rel_df = pd.DataFrame(relationships)
        self.save_dataframe_to_csv(rel_df, output_name)

    def process_parquet_files(self, configs: List[Dict[str, Any]]):
        """Process a list of Parquet file configurations."""
        for config in configs:
            self.convert_parquet_to_csv(
                config["parquet_file"], config["columns"], config["csv_file"]
            )

    def process_relationship_files(self, configs: List[Dict[str, Any]]):
        """Process a list of relationship file configurations."""
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
