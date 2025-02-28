# Copyright 2025 TigerGraph Inc.
# Licensed under the Apache License, Version 2.0.
# See the LICENSE file or https://www.apache.org/licenses/LICENSE-2.0
#
# Permission is granted to use, copy, modify, and distribute this software
# under the License. The software is provided "AS IS", without warranty.

from typing import Literal
import argparse
from .graphrag import GraphRAG, QueryParam


def main(mode: Literal["local", "global"], query: str, to_load_data: bool):
    """Run a GraphRAG query with the specified parameters."""
    graphrag = GraphRAG(to_load_data=to_load_data)

    param = QueryParam(mode=mode)

    result = graphrag.query(query=query, param=param)

    print("------------------- Query Result:  -------------------")
    print(result)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run GraphRAG Query.")
    parser.add_argument(
        "--mode",
        type=str,
        required=True,
        choices=["global", "local"],
        help="Query mode (global or local)",
    )
    parser.add_argument(
        "--query", type=str, required=True, help="The query string to execute"
    )
    parser.add_argument(
        "--to_load_data",
        action='store_true',
        help="Flag to load data before running the query",
    )

    args = parser.parse_args()

    # Explicit cast to Literal to satisfy the type checker
    mode: Literal["local", "global"] = args.mode  # Safe because of `choices`
    main(mode=mode, query=args.query, to_load_data=args.to_load_data)
