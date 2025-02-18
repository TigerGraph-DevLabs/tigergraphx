from pathlib import Path
import argparse
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


def index_documents(custom_rag: CustomLightRAG, file_path: Path):
    """Insert documents from the dataset into LightRAG."""
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    with file_path.open(encoding="utf-8") as f:
        custom_rag.insert(f.read())


def main(input_filename: str):
    """Run LightRAG indexing with a user-specified input file."""
    working_dir = Path("applications/lightrag/data")
    input_file = working_dir / "input" / input_filename

    working_dir.mkdir(parents=True, exist_ok=True)  # Ensure directory exists

    # Setup and index documents
    custom_rag = setup_lightrag(str(working_dir))
    index_documents(custom_rag, file_path=input_file)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Run LightRAG indexing with a custom input file."
    )
    parser.add_argument(
        "--input-file",
        type=str,
        default="clapnq_dev_answerable_orig.jsonl.1",
        help="Specify the input file name (default: clapnq_dev_answerable_orig.jsonl.1)",
    )

    args = parser.parse_args()
    main(args.input_file)
