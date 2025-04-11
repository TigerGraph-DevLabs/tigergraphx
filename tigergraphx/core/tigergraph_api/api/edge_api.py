# Copyright 2025 TigerGraph Inc.
# Licensed under the Apache License, Version 2.0.
# See the LICENSE file or https://www.apache.org/licenses/LICENSE-2.0
#
# Permission is granted to use, copy, modify, and distribute this software
# under the License. The software is provided "AS IS", without warranty.

from typing import List
from .base_api import BaseAPI


class EdgeAPI(BaseAPI):
    def retrieve_a_edge(
        self,
        graph_name: str,
        source_node_type: str,
        source_node_id: str,
        edge_type: str,
        target_node_type: str,
        target_node_id: str,
    ) -> List:
        """
        Retrieve a single edge from the specified graph.
        """
        result = self._request(
            endpoint_name="retrieve_a_edge",
            version="4.x",
            graph_name=graph_name,
            source_node_type=source_node_type,
            source_node_id=source_node_id,
            edge_type=edge_type,
            target_node_type=target_node_type,
            target_node_id=target_node_id,
        )
        if not isinstance(result, list):
            raise TypeError(f"Expected list, but got {type(result).__name__}: {result}")
        return result
