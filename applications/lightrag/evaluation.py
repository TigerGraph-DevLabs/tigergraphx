from typing import Literal, cast
import os
import argparse
from datasets import Dataset, load_dataset
from lightrag import QueryParam
from lightrag.llm.openai import gpt_4o_mini_complete, openai_embed

from .custom_ligtrag import CustomLightRAG

from tigergraphx.graphrag import RagasEvaluator


def setup_lightrag():
    """Set up LightRAG instance for indexing and querying."""
    working_dir = "applications/lightrag/data"

    if not os.path.exists(working_dir):
        os.makedirs(working_dir, exist_ok=True)

    return CustomLightRAG(
        working_dir=working_dir,
        embedding_func=openai_embed,
        llm_model_func=gpt_4o_mini_complete,
        graph_storage="TigerGraphStorage",
        vector_storage="TigerVectorStorage",
        kv_storage="JsonKVStorage",
    )


def query_light_rag(
    custom_rag,
    query,
    mode: Literal["naive", "hybrid"] = "hybrid",
    only_context=False,
):
    """Query LightRAG to retrieve context or generated responses."""
    param = QueryParam(mode=mode, only_need_context=only_context)
    result = custom_rag.query(query=query, param=param)
    return result


def prepare_evaluation_data(
    custom_rag,
    ragas_data,
    mode: Literal["naive", "hybrid"] = "hybrid",
):
    """Prepare evaluation dataset using queries from ragas_data."""
    eval_samples = []

    for row in ragas_data:
        question = row["input"]  # Adjust to match dataset structure
        ground_truths = [
            ans["answer"] for ans in row["output"]
        ]  # Extract ground truth answers

        # Extract passages from the dataset (context retrieval)
        retrieved_contexts = query_light_rag(
            custom_rag, question, mode, only_context=True
        )

        # Extract generated response from LightRAG
        response = query_light_rag(custom_rag, question, mode, only_context=False)

        eval_samples.append(
            {
                "question": question,
                "contexts": retrieved_contexts
                if isinstance(retrieved_contexts, list)
                else [retrieved_contexts],
                "answer": response,
                "ground_truth": ground_truths,
            }
        )
    return eval_samples


def evaluate_light_rag(
    eval_samples,
    mode: Literal["naive", "hybrid"] = "hybrid",
):
    """Evaluate LightRAG using RagasEvaluator."""
    evaluator = RagasEvaluator(model="gpt-4o")

    # Run evaluation
    results = evaluator.evaluate_dataset(eval_samples)

    results.to_csv(f"applications/lightrag/data/output_{mode}.csv", index=False)


def main(mode: Literal["naive", "hybrid"]):
    """Main function to index, query, and evaluate LightRAG."""
    # Load datasets
    dataset = load_dataset(
        "json",
        data_files="applications/resources/clapnq_dev_answerable.jsonl.50",
        split="train",
    )
    dataset = cast(Dataset, dataset)

    # Setup LightRAG
    custom_rag = setup_lightrag()

    # Prepare evaluation dataset
    eval_samples = prepare_evaluation_data(custom_rag, dataset, mode)

    # Evaluate LightRAG
    evaluate_light_rag(eval_samples, mode)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run LightRAG Query.")
    parser.add_argument(
        "--mode", choices=["naive", "hybrid"], required=True, help="Query mode"
    )

    args = parser.parse_args()
    main(args.mode)
