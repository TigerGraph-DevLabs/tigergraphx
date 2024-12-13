import pytest
import pandas as pd
from tigergraphx.pipelines.parquet_processor import ParquetProcessor


@pytest.fixture
def parquet_processor(tmp_path):
    input_dir = tmp_path / "input"
    output_dir = tmp_path / "output"
    input_dir.mkdir()
    output_dir.mkdir()
    return ParquetProcessor(input_dir=str(input_dir), output_dir=output_dir)


class TestParquetProcessor:
    def test_save_dataframe_to_csv(self, parquet_processor, tmp_path):
        df = pd.DataFrame(
            {
                "column1": ["value1", 'value"2"'],
                "column2": ['"value"3', '"value\n4"'],
            }
        )
        file_name = "test_save_dataframe_to_csv.csv"
        file_path = tmp_path / "output" / file_name
        parquet_processor.save_dataframe_to_csv(df, file_path.name)

        # Verify the file content
        with open(file_path, "r") as f:
            content = f.read()
        expected_content = """column1,column2
value1,"\\"value\\"3"
"value\\"2\\"","\\"value\\n4\\""
"""
        assert content == expected_content

    def test_convert_parquet_to_csv(self, parquet_processor, tmp_path):
        # Create a sample DataFrame and save it as a Parquet file
        df = pd.DataFrame(
            {
                "column1": ["value1", "value2"],
                "column2": ["value3", "value4"],
                "column3": ["value5", "value6"],
            }
        )
        parquet_file_name = "test_convert_parquet_to_csv.parquet"
        parquet_file_path = tmp_path / "input" / parquet_file_name
        df.to_parquet(parquet_file_path)

        # Define the columns to select and the output CSV file name
        columns_to_select = ["column1", "column3"]
        csv_file_name = "test_convert_parquet_to_csv.csv"
        csv_file_path = tmp_path / "output" / csv_file_name

        # Convert Parquet to CSV
        parquet_processor.convert_parquet_to_csv(
            parquet_file_name, columns_to_select, csv_file_path.name
        )

        # Verify the CSV file content
        with open(csv_file_path, "r") as f:
            content = f.read()
        expected_content = """column1,column3
value1,value5
value2,value6
"""
        assert content == expected_content

    def test_create_relationship_file(self, parquet_processor, tmp_path):
        # Create a sample DataFrame
        df = pd.DataFrame(
            {
                "elements": [["elem1", "elem2"], ["elem3"]],
                "collection": ["collection1", "collection2"],
            }
        )

        # Define parameters for the relationship file creation
        element_list_name = "elements"
        element_name = "element"
        collection_name = "collection"
        collection_new_name = "new_collection"
        output_name = "relationship.csv"
        output_file_path = tmp_path / "output" / output_name

        # Create the relationship file
        parquet_processor.create_relationship_file(
            df,
            element_list_name,
            element_name,
            collection_name,
            collection_new_name,
            output_file_path.name,
        )

        # Verify the CSV file content
        with open(output_file_path, "r") as f:
            content = f.read()
        expected_content = """element,new_collection
elem1,collection1
elem2,collection1
elem3,collection2
"""
        assert content == expected_content
