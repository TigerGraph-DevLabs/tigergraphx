# Copyright 2025 TigerGraph Inc.
# Licensed under the Apache License, Version 2.0.
# See the LICENSE file or https://www.apache.org/licenses/LICENSE-2.0
#
# Permission is granted to use, copy, modify, and distribute this software
# under the License. The software is provided "AS IS", without warranty.

from lightrag import LightRAG
from lightrag.lightrag import lazy_external_import


class CustomLightRAG(LightRAG):
    def _get_storage_class(self, storage_name: str) -> dict:
        """Override storage retrieval to use a modified STORAGES mapping."""

        custom_storages = {
            "TigerGraphStorage": "applications.lightrag.storage.tigergraph_storage",
            "TigerVectorStorage": "applications.lightrag.storage.tigervector_storage",
        }

        if storage_name in custom_storages:
            import_path = custom_storages[storage_name]
            return lazy_external_import(import_path, storage_name) # pyright: ignore

        # Call the parent class's method instead of self to prevent infinite recursion
        return super()._get_storage_class(storage_name)
