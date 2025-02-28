# Copyright 2025 TigerGraph Inc.
# Licensed under the Apache License, Version 2.0.
# See the LICENSE file or https://www.apache.org/licenses/LICENSE-2.0
#
# Permission is granted to use, copy, modify, and distribute this software
# under the License. The software is provided "AS IS", without warranty.

from tigergraphx import Graph

graphs_to_drop = [
    "LightRAG",
    "Vector_chunks",
    "Vector_entities",
    "Vector_relationships",
]
for graph_name in graphs_to_drop:
    try:
        G = Graph.from_db(graph_name)
        G.drop_graph()
    except Exception as e:
        print(f"Error message: {str(e)}")
