# Copyright 2025 TigerGraph Inc.
# Licensed under the Apache License, Version 2.0.
# See the LICENSE file or https://www.apache.org/licenses/LICENSE-2.0
#
# Permission is granted to use, copy, modify, and distribute this software
# under the License. The software is provided "AS IS", without warranty.

from typing import Dict, Optional
from pathlib import Path
import logging

from tigergraphx.config import (
    TigerGraphConnectionConfig,
    GraphSchema,
)
from tigergraphx.core.tigergraph_api import TigerGraphAPI

logger = logging.getLogger(__name__)


class GraphContext:
    def __init__(
        self,
        graph_schema: GraphSchema | Dict | str | Path,
        tigergraph_connection_config: Optional[
            TigerGraphConnectionConfig | Dict | str | Path
        ] = None,
    ):
        graph_schema = GraphSchema.ensure_config(graph_schema)
        self.graph_schema = graph_schema
        self.tigergraph_api = TigerGraphAPI(tigergraph_connection_config)
