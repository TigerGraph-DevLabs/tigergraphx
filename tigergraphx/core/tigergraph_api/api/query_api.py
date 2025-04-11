# Copyright 2025 TigerGraph Inc.
# Licensed under the Apache License, Version 2.0.
# See the LICENSE file or https://www.apache.org/licenses/LICENSE-2.0
#
# Permission is granted to use, copy, modify, and distribute this software
# under the License. The software is provided "AS IS", without warranty.

from typing import Any, Dict, List, Optional
from datetime import datetime

from .base_api import BaseAPI


class QueryAPI(BaseAPI):
    def run_interpreted_query(
        self, query_text: str, params: Optional[Dict[str, Any]] = None
    ) -> List:
        parsed_params = self._parse_query_parameters(params) if params else None
        result = self._request(
            endpoint_name="run_interpreted_query",
            version="4.x",
            data=query_text,
            params=parsed_params,
        )
        if not isinstance(result, list):
            raise TypeError(f"Expected list, but got {type(result).__name__}: {result}")
        return result

    def run_installed_query_get(
        self, graph_name: str, query_name: str, params: Optional[Dict[str, Any]] = None
    ) -> List:
        parsed_params = self._parse_query_parameters(params) if params else None
        result = self._request(
            endpoint_name="run_installed_query",
            version="4.x",
            params=parsed_params,
            method="GET",
            query_name=query_name,
            graph_name=graph_name,
        )
        if not isinstance(result, list):
            raise TypeError(f"Expected list, but got {type(result).__name__}: {result}")
        return result

    def run_installed_query_post(
        self, graph_name: str, query_name: str, json: Optional[Dict[str, Any]] = None
    ) -> List:
        result = self._request(
            endpoint_name="run_installed_query",
            version="4.x",
            json=json,
            method="POST",
            query_name=query_name,
            graph_name=graph_name,
        )
        if not isinstance(result, list):
            raise TypeError(f"Expected list, but got {type(result).__name__}: {result}")
        return result

    def _parse_query_parameters(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parses query parameters into a dictionary suitable for HTTP requests.
        """

        parsed_params = {}

        for key, value in params.items():
            if isinstance(value, tuple):  # Handling (vertex_primary_id, vertex_type)
                if len(value) == 2 and isinstance(value[1], str):
                    parsed_params[key] = str(value[0])
                    parsed_params[f"{key}.type"] = value[1]
                else:
                    raise ValueError("Invalid parameter format: expected (id, type).")

            elif isinstance(value, list):  # Handling SET<VERTEX> and other lists
                for i, item in enumerate(value):
                    if isinstance(item, tuple):
                        if len(item) == 2 and isinstance(item[1], str):
                            parsed_params[f"{key}[{i}]"] = str(item[0])
                            parsed_params[f"{key}[{i}].type"] = item[1]
                        else:
                            raise ValueError(
                                "Invalid parameter format in list: expected (id, type)."
                            )
                    else:
                        parsed_params = params
                        break

            elif isinstance(value, datetime):  # Convert datetime to string
                parsed_params[key] = value.strftime("%Y-%m-%d %H:%M:%S")

            else:  # Default case
                parsed_params[key] = str(value)

        return parsed_params
