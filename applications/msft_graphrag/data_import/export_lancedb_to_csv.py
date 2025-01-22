import os
from pathlib import Path
import lancedb


def main(input_dir: str, output_dir: str):
    os.makedirs(output_dir, exist_ok=True)
    db = lancedb.connect(input_dir)
    table = db.open_table("default-entity-description")
    df = table.to_pandas()

    # Concatenate the embeddings into a single string
    # Assuming "vector" column contains the embeddings (lists or arrays)
    df["embedding_str"] = df["vector"].apply(lambda x: ' '.join(map(str, x)))

    # Drop the original columns
    df = df.drop(columns=["vector", "text", "attributes"])

    # Write the DataFrame to a CSV file
    csv_file_path = Path(output_dir) / "entity_emb_description.csv"
    df.to_csv(csv_file_path, index=False)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Process parquet files and export to CSV."
    )
    parser.add_argument(
        "--input_dir",
        type=str,
        required=True,
        help="Directory containing the input parquet files.",
    )
    parser.add_argument(
        "--output_dir",
        type=str,
        required=True,
        help="Directory to save the output CSV files.",
    )

    args = parser.parse_args()
    main(args.input_dir, args.output_dir)
