# Copyright 2025 TigerGraph Inc.
# Licensed under the Apache License, Version 2.0.
# See the LICENSE file or https://www.apache.org/licenses/LICENSE-2.0
#
# Permission is granted to use, copy, modify, and distribute this software
# under the License. The software is provided "AS IS", without warranty.

from typing import Any, Dict, List, Literal, Optional
from enum import Enum


from .base_api import BaseAPI


class DataSourceType(str, Enum):
    S3 = "s3"
    GCS = "gcs"
    ABS = "abs"

    @classmethod
    def from_value(cls, value: str) -> "DataSourceType":
        value = value.lower()
        try:
            return cls(value)
        except ValueError:
            valid_values = ", ".join([e.value for e in cls])
            raise ValueError(
                f"Invalid DataSourceType: '{value}'. Valid types are: {valid_values}"
            )


class DataSourceAPI(BaseAPI):
    def create_data_source(
        self,
        name: str,
        data_source_type: str | DataSourceType,
        access_key: Optional[str] = None,
        secret_key: Optional[str] = None,
        extra_config: Optional[Dict[str, Any]] = None,
        graph_name: Optional[str] = None,
    ) -> str:
        payload = self._build_data_source_payload(
            name=name,
            data_source_type=data_source_type,
            access_key=access_key,
            secret_key=secret_key,
            extra_config=extra_config,
        )

        result = self._request(
            endpoint_name="create_data_source",
            params={"graph": graph_name} if graph_name else None,
            json=payload,
        )

        if not isinstance(result, str):
            raise TypeError(f"Expected str, but got {type(result).__name__}: {result}")
        return result

    def update_data_source(
        self,
        name: str,
        data_source_type: str | DataSourceType,
        access_key: Optional[str] = None,
        secret_key: Optional[str] = None,
        extra_config: Optional[Dict[str, Any]] = None,
        graph_name: Optional[str] = None,
    ) -> str:
        payload = self._build_data_source_payload(
            name=name,
            data_source_type=data_source_type,
            access_key=access_key,
            secret_key=secret_key,
            extra_config=extra_config,
        )

        result = self._request(
            endpoint_name="update_data_source",
            params={"graph": graph_name} if graph_name else None,
            json=payload,
            data_source_name=name,
        )

        if not isinstance(result, str):
            raise TypeError(f"Expected str, but got {type(result).__name__}: {result}")
        return result

    def get_data_source(self, name: str) -> Dict[str, Any]:
        result = self._request(
            endpoint_name="get_data_source",
            data_source_name=name,
        )

        if not isinstance(result, dict):
            raise TypeError(f"Expected dict, but got {type(result).__name__}: {result}")
        return result

    def drop_data_source(
        self,
        name: str,
        graph_name: Optional[str] = None,
    ) -> str:
        result = self._request(
            endpoint_name="drop_data_source",
            params={"graph": graph_name} if graph_name else None,
            data_source_name=name,
        )

        if not isinstance(result, str):
            raise TypeError(f"Expected str, but got {type(result).__name__}: {result}")
        return result

    def get_all_data_sources(
        self, graph_name: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        result = self._request(
            endpoint_name="get_all_data_sources",
            params={"graph": graph_name} if graph_name else None,
        )
        if not isinstance(result, list):
            raise TypeError(f"Expected list, but got {type(result).__name__}: {result}")
        return result

    def drop_all_data_sources(self, graph_name: Optional[str] = None) -> str:
        result = self._request(
            endpoint_name="drop_all_data_sources",
            params={"graph": graph_name} if graph_name else None,
        )

        if not isinstance(result, str):
            raise TypeError(f"Expected str, but got {type(result).__name__}: {result}")
        return result

    def preview_sample_data(
        self,
        path: str,
        data_source_type: Optional[str | DataSourceType] = None,
        data_source: Optional[str] = None,
        data_format: Optional[Literal["csv", "json"]] = "csv",
        size: Optional[int] = 10,
        has_header: bool = True,
        separator: Optional[str] = ",",
        eol: Optional[str] = "\\n",
        quote: Optional[Literal["'", '"']] = '"',
    ) -> Dict[str, Any]:
        payload: Dict[str, Any] = {
            "path": path,
            "parsing": {
                "header": str(has_header).lower(),
                "separator": separator,
                "eol": eol,
                "quote": "none",
            },
            "size": size,
            "dataFormat": data_format,
        }

        if data_source_type is not None:
            if isinstance(data_source_type, str):
                data_source_type = DataSourceType.from_value(data_source_type)
            payload["type"] = data_source_type.value
        if data_source is not None:
            payload["dataSource"] = data_source
        if quote is not None:
            payload["parsing"]["quote"] = quote

        result = self._request(
            endpoint_name="preview_sample_data",
            json=payload,
        )

        if not isinstance(result, dict):
            raise TypeError(f"Expected dict, but got {type(result).__name__}: {result}")
        return result

    def _build_data_source_payload(
        self,
        name: str,
        data_source_type: str | DataSourceType,
        access_key: Optional[str],
        secret_key: Optional[str],
        extra_config: Optional[Dict[str, Any]],
    ) -> Dict[str, Any]:
        if isinstance(data_source_type, str):
            data_source_type = DataSourceType.from_value(data_source_type)

        config: Dict[str, Any] = {
            "type": data_source_type.value,
            "access.key": access_key or "none",
            "secret.key": secret_key or "none",
        }

        if extra_config:
            config.update(extra_config)

        return {"name": name, "config": config}
