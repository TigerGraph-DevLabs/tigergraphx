# Copyright 2025 TigerGraph Inc.
# Licensed under the Apache License, Version 2.0.
# See the LICENSE file or https://www.apache.org/licenses/LICENSE-2.0
#
# Permission is granted to use, copy, modify, and distribute this software
# under the License. The software is provided "AS IS", without warranty.

from typing import Literal, cast
import argparse
from datasets import Dataset, load_dataset
from tigergraphx.graphrag import RagasEvaluator
from .graphrag import GraphRAG, QueryParam


def setup_graphrag(to_load_data: bool) -> GraphRAG:
    """Set up GraphRAG instance for querying."""
    return GraphRAG(to_load_data=to_load_data)


def query_graphrag(
    graphrag,
    query: str,
    mode: Literal["local", "global"] = "global",
    only_need_context=False,
):
    """Query GraphRAG to retrieve context or generated responses."""
    param = QueryParam(mode=mode, only_need_context=only_need_context)
    result = graphrag.query(query=query, param=param)
    return result


def prepare_evaluation_data(
    graphrag,
    ragas_data,
    mode: Literal["local", "global"] = "global",
):
    """Prepare evaluation dataset using queries from ragas_data."""
    eval_samples = []

    for row in ragas_data:
        question = row["input"]  # Adjust to match dataset structure
        ground_truths = [
            ans["answer"] for ans in row["output"]
        ]  # Extract ground truth answers

        # Extract passages from the dataset (context retrieval)
        retrieved_contexts = query_graphrag(
            graphrag, question, mode, only_need_context=True
        )

        # Extract generated response from GraphRAG
        response = query_graphrag(graphrag, question, mode, only_need_context=False)

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


def evaluate_graphrag(
    eval_samples,
    mode: Literal["local", "global"] = "global",
):
    """Evaluate GraphRAG using RagasEvaluator."""
    evaluator = RagasEvaluator(model="gpt-4o")

    # Run evaluation
    results = evaluator.evaluate_dataset(eval_samples)

    results.to_csv(f"applications/msft_graphrag/data/output_{mode}.csv", index=False)


def main(mode: Literal["local", "global"], to_load_data: bool):
    """Main function to query and evaluate GraphRAG."""
    # Load datasets
    dataset = load_dataset(
        "json",
        data_files="applications/resources/clapnq_dev_answerable.jsonl.50",
        split="train",
    )
    dataset = cast(Dataset, dataset)

    # Setup GraphRAG
    graphrag = setup_graphrag(to_load_data)

    # Prepare evaluation dataset
    eval_samples = prepare_evaluation_data(graphrag, dataset, mode)

    # Evaluate GraphRAG
    evaluate_graphrag(eval_samples, mode)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run GraphRAG Query.")
    parser.add_argument(
        "--mode", choices=["local", "global"], required=True, help="Query mode"
    )
    parser.add_argument(
        "--to_load_data", action="store_true", help="Flag to load data before querying"
    )

    args = parser.parse_args()
    main(args.mode, args.to_load_data)
