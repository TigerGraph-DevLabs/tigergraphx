from .base_api import BaseAPI


class GSQLAPI(BaseAPI):
    def gsql(self, command: str):
        return self._request(endpoint_name="gsql", version="4.x", data=command)
