# Copyright 2025 TigerGraph Inc.
# Licensed under the Apache License, Version 2.0.
# See the LICENSE file or https://www.apache.org/licenses/LICENSE-2.0
#
# Permission is granted to use, copy, modify, and distribute this software
# under the License. The software is provided "AS IS", without warranty.

from typing import Any, Dict, List
from .base_api import BaseAPI


class UpsertAPI(BaseAPI):
    def upsert_graph_data(self, graph_name: str, payload: Dict[str, Any]) -> List:
        """
        Upsert data (nodes and/or edges) into a specific graph.
        """
        result = self._request(
            endpoint_name="upsert_graph_data",
            version="4.x",
            graph_name=graph_name,
            json=payload,
        )
        if not isinstance(result, list):
            raise TypeError(f"Expected list, but got {type(result).__name__}: {result}")
        return result
