# Copyright 2025 TigerGraph Inc.
# Licensed under the Apache License, Version 2.0.
# See the LICENSE file or https://www.apache.org/licenses/LICENSE-2.0
#
# Permission is granted to use, copy, modify, and distribute this software
# under the License. The software is provided "AS IS", without warranty.

from .base_api import BaseAPI


class AdminAPI(BaseAPI):
    def ping(self) -> str:
        result = self._request(endpoint_name="ping", version="4.x")
        if not isinstance(result, str):
            raise TypeError(f"Expected str, but got {type(result).__name__}: {result}")
        return result
