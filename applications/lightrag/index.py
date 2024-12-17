import os

from .custom_ligtrag import CustomLightRAG


def main():
    """Run a LightRAG indexing."""
    working_dir = "applications/lightrag/data"

    if not os.path.exists(working_dir):
        os.mkdir(working_dir)

    custom_rag = CustomLightRAG(
        working_dir=working_dir,
        graph_storage="TigerGraphStorage",
        vector_storage="NanoVectorDBStorage",
        kv_storage="JsonKVStorage",
    )

    with open(working_dir + "/input/fin.txt") as f:
        custom_rag.insert(f.read())


if __name__ == "__main__":
    main()
