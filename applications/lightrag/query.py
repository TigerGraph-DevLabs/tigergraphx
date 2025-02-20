import os
import argparse
from typing import Literal
from lightrag import QueryParam
from lightrag.llm.openai import gpt_4o_mini_complete, openai_embed

from .custom_ligtrag import CustomLightRAG


def setup_lightrag(working_dir: str) -> CustomLightRAG:
    """Initialize and return a CustomLightRAG instance."""
    return CustomLightRAG(
        working_dir=working_dir,
        embedding_func=openai_embed,
        llm_model_func=gpt_4o_mini_complete,
        graph_storage="TigerGraphStorage",
        vector_storage="TigerVectorStorage",
        kv_storage="JsonKVStorage",
    )


def run_query(custom_rag: CustomLightRAG, mode: Literal["naive", "hybrid"], query: str):
    """Run a query on LightRAG with the specified mode."""
    result = custom_rag.query(query=query, param=QueryParam(mode=mode))
    print(f"\n----- Query Result ({mode} mode) -----\n{result}")


def main(mode: Literal["naive", "hybrid"], query: str):
    """Set up and execute a LightRAG query."""
    working_dir = "applications/lightrag/data"
    os.makedirs(working_dir, exist_ok=True)  # Ensure directory exists

    custom_rag = setup_lightrag(working_dir)
    run_query(custom_rag, mode, query)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run LightRAG Query.")
    parser.add_argument(
        "--mode", choices=["naive", "hybrid"], required=True, help="Query mode"
    )
    parser.add_argument("--query", required=True, help="The query string to execute")

    args = parser.parse_args()
    main(args.mode, args.query)
