import os
import argparse
from typing import Literal
from lightrag import QueryParam

from .custom_ligtrag import CustomLightRAG


def main(mode: Literal["naive", "hybrid"], query: str):
    """Run a LightRAG query with the specified parameters."""
    working_dir = "applications/lightrag/data"

    if not os.path.exists(working_dir):
        os.mkdir(working_dir)

    custom_rag = CustomLightRAG(
        working_dir=working_dir,
        graph_storage="TigerGraphStorage",
        vector_storage="NanoVectorDBStorage",
        kv_storage="JsonKVStorage",
    )

    param = QueryParam(mode=mode)

    result = custom_rag.query(query=query, param=param)

    print("------------------- Query Result:  -------------------")
    print(result)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run LightRAG Query.")
    parser.add_argument(
        "--mode",
        type=str,
        required=True,
        choices=["naive", "hybrid"],
        help="Query mode (naive or hybrid)",
    )
    parser.add_argument(
        "--query", type=str, required=True, help="The query string to execute"
    )

    args = parser.parse_args()

    # Explicit cast to Literal to satisfy the type checker
    mode: Literal["naive", "hybrid"] = args.mode  # Safe because of `choices`
    main(mode=mode, query=args.query)
