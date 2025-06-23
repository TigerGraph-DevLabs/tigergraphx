# Copyright 2025 TigerGraph Inc.
# Licensed under the Apache License, Version 2.0.
# See the LICENSE file or https://www.apache.org/licenses/LICENSE-2.0
#
# Permission is granted to use, copy, modify, and distribute this software
# under the License. The software is provided "AS IS", without warranty.

from typing import Dict
from .base_api import BaseAPI


class SchemaAPI(BaseAPI):
    def get_schema(self, graph_name: str) -> Dict:
        """
        Retrieves the schema for a specific graph.
        """
        result = self._request(endpoint_name="get_schema", graph_name=graph_name)
        if not isinstance(result, dict):
            raise TypeError(f"Expected dict, but got {type(result).__name__}: {result}")
        return result
