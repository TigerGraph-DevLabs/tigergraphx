from .base_api import BaseAPI


class AdminAPI(BaseAPI):
    def ping(self):
        return self._request(endpoint_name="ping", version="4.x")
