# Copyright 2025 TigerGraph Inc.
# Licensed under the Apache License, Version 2.0.
# See the LICENSE file or https://www.apache.org/licenses/LICENSE-2.0
#
# Permission is granted to use, copy, modify, and distribute this software
# under the License. The software is provided "AS IS", without warranty.

import os

from tigergraphx import Graph

from graph_schema import graph_schema

def main():
    os.environ["TG_HOST"] = "http://127.0.0.1"
    os.environ["TG_USERNAME"] = "tigergraph"
    os.environ["TG_PASSWORD"] = "tigergraph"

    G = Graph(graph_schema)

    loading_job = {
        "loading_job_name": "loading_job_retail",
        "files": [
            {
                "file_alias": "f_nodes_product",
                "file_path": "/home/tigergraph/data/simple_graphrag/nodes_product.csv",
                "csv_parsing_options": {
                    "separator": ",",
                    "header": True,
                    "EOL": "\\n",
                    "quote": "DOUBLE",
                },
                "node_mappings": [
                    {
                        "target_name": "Product",
                        "attribute_column_mappings": {
                            "name": "name",
                            "price": "price",
                            "weight": "weight",
                            "features": "features",
                            "emb_features": 'SPLIT($"embedding", " ")',
                        },
                    }
                ],
            },
            {
                "file_alias": "f_nodes_tag",
                "file_path": "/home/tigergraph/data/simple_graphrag/nodes_tag.csv",
                "csv_parsing_options": {
                    "separator": ",",
                    "header": True,
                    "EOL": "\\n",
                    "quote": "DOUBLE",
                },
                "node_mappings": [
                    {
                        "target_name": "Tag",
                        "attribute_column_mappings": {"name": "name"},
                    }
                ],
            },
            {
                "file_alias": "f_nodes_category",
                "file_path": "/home/tigergraph/data/simple_graphrag/nodes_category.csv",
                "csv_parsing_options": {
                    "separator": ",",
                    "header": True,
                    "EOL": "\\n",
                    "quote": "DOUBLE",
                },
                "node_mappings": [
                    {
                        "target_name": "Category",
                        "attribute_column_mappings": {"name": "name"},
                    }
                ],
            },
            {
                "file_alias": "f_nodes_segment",
                "file_path": "/home/tigergraph/data/simple_graphrag/nodes_segment.csv",
                "csv_parsing_options": {
                    "separator": ",",
                    "header": True,
                    "EOL": "\\n",
                    "quote": "DOUBLE",
                },
                "node_mappings": [
                    {
                        "target_name": "Segment",
                        "attribute_column_mappings": {"name": "name"},
                    }
                ],
            },
            {
                "file_alias": "f_nodes_bundle",
                "file_path": "/home/tigergraph/data/simple_graphrag/nodes_bundle.csv",
                "csv_parsing_options": {
                    "separator": ",",
                    "header": True,
                    "EOL": "\\n",
                    "quote": "DOUBLE",
                },
                "node_mappings": [
                    {
                        "target_name": "Bundle",
                        "attribute_column_mappings": {"name": "name"},
                    }
                ],
            },
            {
                "file_alias": "f_edges_in_category",
                "file_path": "/home/tigergraph/data/simple_graphrag/edges_in_category.csv",
                "edge_mappings": [
                    {
                        "target_name": "In_Category",
                        "source_node_column": "source",
                        "target_node_column": "target",
                    }
                ],
            },
            {
                "file_alias": "f_edges_tagged_with",
                "file_path": "/home/tigergraph/data/simple_graphrag/edges_tagged_with.csv",
                "edge_mappings": [
                    {
                        "target_name": "Tagged_With",
                        "source_node_column": "source",
                        "target_node_column": "target",
                    }
                ],
            },
            {
                "file_alias": "f_edges_in_segment",
                "file_path": "/home/tigergraph/data/simple_graphrag/edges_in_segment.csv",
                "edge_mappings": [
                    {
                        "target_name": "In_Segment",
                        "source_node_column": "source",
                        "target_node_column": "target",
                    }
                ],
            },
            {
                "file_alias": "f_edges_in_bundle",
                "file_path": "/home/tigergraph/data/simple_graphrag/edges_in_bundle.csv",
                "edge_mappings": [
                    {
                        "target_name": "In_Bundle",
                        "source_node_column": "source",
                        "target_node_column": "target",
                    }
                ],
            },
            {
                "file_alias": "f_edges_is_accessory_of",
                "file_path": "/home/tigergraph/data/simple_graphrag/edges_is_accessory_of.csv",
                "edge_mappings": [
                    {
                        "target_name": "Is_Accessory_Of",
                        "source_node_column": "source",
                        "target_node_column": "target",
                    }
                ],
            },
            {
                "file_alias": "f_edges_is_upgrade_of",
                "file_path": "/home/tigergraph/data/simple_graphrag/edges_is_upgrade_of.csv",
                "edge_mappings": [
                    {
                        "target_name": "Is_Upgrade_Of",
                        "source_node_column": "source",
                        "target_node_column": "target",
                    }
                ],
            },
        ],
    }
    G.load_data(loading_job)


if __name__ == "__main__":
    main()
