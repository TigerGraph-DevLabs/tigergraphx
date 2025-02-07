from typing import Dict
from .base_api import BaseAPI


class SchemaAPI(BaseAPI):
    def get_schema(self, graph_name) -> Dict:
        """
        Retrieves the schema for a specific graph.
        """
        result = self._request(
            endpoint_name="get_schema", version="4.x", graph_name=graph_name
        )
        if not isinstance(result, dict):
            raise TypeError(f"Expected str, but got {type(result).__name__}: {result}")
        return result
