from .base_api import BaseAPI


class SchemaAPI(BaseAPI):
    def get_schema(self, graph_name):
        """
        Retrieves the schema for a specific graph.
        """
        return self._request(
            endpoint_name="get_schema", version="4.x", graph=graph_name
        )
