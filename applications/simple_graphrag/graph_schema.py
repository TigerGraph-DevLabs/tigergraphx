# Copyright 2025 TigerGraph Inc.
# Licensed under the Apache License, Version 2.0.
# See the LICENSE file or https://www.apache.org/licenses/LICENSE-2.0
#
# Permission is granted to use, copy, modify, and distribute this software
# under the License. The software is provided "AS IS", without warranty.

graph_schema = {
    "graph_name": "RetailGraph",
    "nodes": {
        "Product": {
            "primary_key": "name",
            "attributes": {
                "name": "STRING",
                "price": "DOUBLE",
                "weight": "DOUBLE",
                "features": "STRING",
            },
            "vector_attributes": {"emb_features": 1536},
        },
        "Tag": {
            "primary_key": "name",
            "attributes": {
                "name": "STRING",
            },
        },
        "Category": {
            "primary_key": "name",
            "attributes": {
                "name": "STRING",
            },
        },
        "Segment": {
            "primary_key": "name",
            "attributes": {
                "name": "STRING",
            },
        },
        "Bundle": {
            "primary_key": "name",
            "attributes": {
                "name": "STRING",
            },
        },
        "Deal": {
            "primary_key": "name",
            "attributes": {
                "name": "STRING",
                "deal_end_date": "DATETIME",
            },
        },
    },
    "edges": {
        "In_Category": {
            "is_directed_edge": False,
            "from_node_type": "Product",
            "to_node_type": "Category",
        },
        "Tagged_With": {
            "is_directed_edge": False,
            "from_node_type": "Product",
            "to_node_type": "Tag",
        },
        "In_Segment": {
            "is_directed_edge": False,
            "from_node_type": "Product",
            "to_node_type": "Segment",
        },
        "In_Bundle": {
            "is_directed_edge": False,
            "from_node_type": "Product",
            "to_node_type": "Bundle",
        },
        "Is_Accessory_Of": {
            "is_directed_edge": True,
            "from_node_type": "Product",
            "to_node_type": "Product",
        },
        "Is_Upgrade_Of": {
            "is_directed_edge": True,
            "from_node_type": "Product",
            "to_node_type": "Product",
        },
        "Has_Deal": {
            "is_directed_edge": False,
            "from_node_type": "Product",
            "to_node_type": "Deal",
        },
    },
}
