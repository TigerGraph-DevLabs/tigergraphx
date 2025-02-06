from .base_api import BaseAPI


class AdminAPI(BaseAPI):
    def ping(self) -> str:
        result = self._request(endpoint_name="ping", version="4.x")
        if not isinstance(result, str):
            raise TypeError(f"Expected str, but got {type(result).__name__}: {result}")
        return result
