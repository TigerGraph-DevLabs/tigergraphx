from .base_api import BaseAPI


class GSQLAPI(BaseAPI):
    def gsql(self, command: str) -> str:
        result = self._request(endpoint_name="gsql", version="4.x", data=command)
        if not isinstance(result, str):
            raise TypeError(f"Expected str, but got {type(result).__name__}: {result}")
        return result
