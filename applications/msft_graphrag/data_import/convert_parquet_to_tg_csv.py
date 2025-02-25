# Copyright 2025 TigerGraph Inc.
# Licensed under the Apache License, Version 2.0.
# See the LICENSE file or https://www.apache.org/licenses/LICENSE-2.0
#
# Permission is granted to use, copy, modify, and distribute this software
# under the License. The software is provided "AS IS", without warranty.

import os
import pandas as pd
from tigergraphx import ParquetProcessor


def generate_parquet_configs() -> list[dict]:
    """Generate configurations for processing Parquet files."""
    return [
        {
            "parquet_file": "create_final_documents.parquet",
            "columns": ["id", "title"],
            "csv_file": "create_final_documents.csv",
        },
        {
            "parquet_file": "create_final_text_units.parquet",
            "columns": ["id", "text", "n_tokens"],
            "csv_file": "create_final_text_units.csv",
        },
        {
            "parquet_file": "create_final_entities.parquet",
            "columns": ["id", "human_readable_id", "name", "type", "description"],
            "csv_file": "create_final_entities.csv",
        },
        {
            "parquet_file": "create_final_relationships.parquet",
            "columns": ["id", "human_readable_id", "rank", "weight", "description"],
            "csv_file": "create_final_relationships.csv",
        },
        {
            "parquet_file": "create_final_communities.parquet",
            "columns": ["id", "title", "level"],
            "csv_file": "create_final_communities.csv",
        },
        {
            "parquet_file": "create_final_community_reports.parquet",
            "columns": [
                "community",
                "rank",
                "rank_explanation",
                "full_content",
                "summary",
            ],
            "csv_file": "create_final_community_reports.csv",
        },
    ]


def generate_relationship_configs() -> list[dict]:
    """Generate configurations for processing relationship files."""
    return [
        {
            "parquet_file": "create_final_text_units.parquet",
            "element_list_name": "document_ids",
            "element_name": "document_id",
            "collection_name": "id",
            "collection_new_name": "text_unit_id",
            "output_name": "document_contains_text_unit.csv",
        },
        {
            "parquet_file": "create_final_entities.parquet",
            "element_list_name": "text_unit_ids",
            "element_name": "text_unit_id",
            "collection_name": "id",
            "collection_new_name": "entity_id",
            "output_name": "text_unit_contains_entity.csv",
        },
        {
            "parquet_file": "create_final_relationships.parquet",
            "element_list_name": "text_unit_ids",
            "element_name": "text_unit_id",
            "collection_name": "id",
            "collection_new_name": "relationship_id",
            "output_name": "text_unit_contains_relationship.csv",
        },
    ]


def map_relationships_to_entities(processor: ParquetProcessor):
    """Map source and target names to entity IDs for relationships."""
    entities_df = pd.read_parquet(processor.input_dir / "create_final_entities.parquet")
    relationships_df = pd.read_parquet(
        processor.input_dir / "create_final_relationships.parquet"
    )
    entities_name_to_id = dict(zip(entities_df["name"], entities_df["id"]))
    relationships_df["source_id"] = relationships_df["source"].map(
        lambda x: entities_name_to_id.get(x)
    )
    relationships_df["target_id"] = relationships_df["target"].map(
        lambda x: entities_name_to_id.get(x)
    )

    filtered_df = relationships_df[["id", "source_id"]].dropna()
    renamed_df = filtered_df.rename(columns={"source_id": "entity_id"}) # pyright: ignore
    processor.save_dataframe_to_csv(renamed_df, "relationship_source.csv")

    filtered_df = relationships_df[["id", "target_id"]].dropna()
    renamed_df = filtered_df.rename(columns={"target_id": "entity_id"}) # pyright: ignore
    processor.save_dataframe_to_csv(renamed_df, "relationship_target.csv")


def process_community_relationships(processor: ParquetProcessor):
    """Process and save community relationships."""
    communities_df = pd.read_parquet(
        processor.input_dir / "create_final_communities.parquet"
    )
    community_contains_relationship = [
        {"community_id": row["id"], "relationship_id": rel_id}
        for _, row in communities_df.iterrows()
        for rel_id in row["relationship_ids"]
    ]
    community_contains_relationship_df = pd.DataFrame(community_contains_relationship)
    processor.save_dataframe_to_csv(
        community_contains_relationship_df, "community_contains_relationship.csv"
    )


def main(input_dir: str, output_dir: str):
    os.makedirs(output_dir, exist_ok=True)

    processor = ParquetProcessor(input_dir=input_dir, output_dir=output_dir)

    # Process Parquet files
    parquet_configs = generate_parquet_configs()
    processor.process_parquet_files(parquet_configs)

    # Process relationships
    relationship_configs = generate_relationship_configs()
    processor.process_relationship_files(relationship_configs)

    # Map source and target names to entity IDs
    map_relationships_to_entities(processor)

    # Process community relationships
    process_community_relationships(processor)

    # Process community entities
    processor.convert_parquet_to_csv(
        "create_final_nodes.parquet",
        ["id", "community"],
        "community_contains_entity.csv",
    )

    print("Conversion and processing to CSV completed successfully.")


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
