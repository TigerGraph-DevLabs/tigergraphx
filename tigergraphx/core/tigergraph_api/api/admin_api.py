# Copyright 2025 TigerGraph Inc.
# Licensed under the Apache License, Version 2.0.
# See the LICENSE file or https://www.apache.org/licenses/LICENSE-2.0
#
# Permission is granted to use, copy, modify, and distribute this software
# under the License. The software is provided "AS IS", without warranty.

import re
from collections import Counter

from .base_api import BaseAPI


class AdminAPI(BaseAPI):
    def ping(self) -> str:
        result = self._request(endpoint_name="ping")
        if not isinstance(result, str):
            raise TypeError(f"Expected str, but got {type(result).__name__}: {result}")
        return result

    def get_version(self) -> str:
        result = self._request(endpoint_name="get_version")

        if not isinstance(result, str):
            raise TypeError(f"Expected str, but got {type(result).__name__}: {result}")

        # Try primary method: look for 'TigerGraph version:'
        for line in result.splitlines():
            if "TigerGraph version:" in line:
                parts = line.strip().split(":")
                if len(parts) == 2:
                    return parts[1].strip()

        # Fallback: extract all 'release_X.Y.Z_' patterns and find the most common one
        version_pattern = re.compile(r"release_(\d+\.\d+\.\d+)_")
        matches = version_pattern.findall(result)

        if matches:
            most_common_version, _ = Counter(matches).most_common(1)[0]
            return most_common_version

        raise ValueError(f"Unable to parse TigerGraph version from result:\n{result}")
