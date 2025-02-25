# Copyright 2025 TigerGraph Inc.
# Licensed under the Apache License, Version 2.0.
# See the LICENSE file or https://www.apache.org/licenses/LICENSE-2.0
#
# Permission is granted to use, copy, modify, and distribute this software
# under the License. The software is provided "AS IS", without warranty.

from tigergraphx.core.graph_context import GraphContext


class BaseManager:
    def __init__(self, context: GraphContext):
        self._connection = context.connection
        self._graph_schema = context.graph_schema
