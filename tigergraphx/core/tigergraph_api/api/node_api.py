# Copyright 2025 TigerGraph Inc.
# Licensed under the Apache License, Version 2.0.
# See the LICENSE file or https://www.apache.org/licenses/LICENSE-2.0
#
# Permission is granted to use, copy, modify, and distribute this software
# under the License. The software is provided "AS IS", without warranty.

from typing import Dict, List
from .base_api import BaseAPI


class NodeAPI(BaseAPI):
    def retrieve_a_node(self, graph_name: str, node_type: str, node_id: str) -> List:
        """
        Retrieve a single node from the specified graph.
        """
        result = self._request(
            endpoint_name="retrieve_a_node",
            graph_name=graph_name,
            node_type=node_type,
            node_id=node_id,
        )
        if not isinstance(result, list):
            raise TypeError(f"Expected list, but got {type(result).__name__}: {result}")
        return result

    def delete_a_node(self, graph_name: str, node_type: str, node_id: str) -> Dict:
        """
        Delete a single node from the specified graph.
        """
        result = self._request(
            endpoint_name="delete_a_node",
            graph_name=graph_name,
            node_type=node_type,
            node_id=node_id,
        )
        if not isinstance(result, dict):
            raise TypeError(f"Expected dict, but got {type(result).__name__}: {result}")
        return result

    def delete_nodes(self, graph_name: str, node_type: str) -> Dict:
        """
        Delete a single node from the specified graph.
        """
        result = self._request(
            endpoint_name="delete_nodes",
            graph_name=graph_name,
            node_type=node_type,
        )
        if not isinstance(result, dict):
            raise TypeError(f"Expected dict, but got {type(result).__name__}: {result}")
        return result
