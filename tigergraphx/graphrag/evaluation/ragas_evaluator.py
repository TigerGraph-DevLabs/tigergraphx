# Copyright 2025 TigerGraph Inc.
# Licensed under the Apache License, Version 2.0.
# See the LICENSE file or https://www.apache.org/licenses/LICENSE-2.0
#
# Permission is granted to use, copy, modify, and distribute this software
# under the License. The software is provided "AS IS", without warranty.

import logging
from typing import Dict, List, Optional
import pandas as pd
from langchain_openai import ChatOpenAI
from ragas import EvaluationDataset, evaluate
from ragas.llms import LangchainLLMWrapper
from ragas.metrics import (
    ResponseRelevancy,
    Faithfulness,
    LLMContextPrecisionWithReference,
    LLMContextRecall,
)


from .base_rag_evaluator import BaseRAGEvaluator


logger = logging.getLogger(__name__)


class RagasEvaluator(BaseRAGEvaluator):
    """Ragas-based evaluator for assessing RAG system performance."""

    def __init__(self, model: str = "gpt-4o", metrics: Optional[List] = None):
        """Initialize the evaluator with a specified LLM model and optional custom metrics."""
        super().__init__(metrics)
        self.llm = ChatOpenAI(model=model)
        self.evaluator_llm = LangchainLLMWrapper(self.llm)

    def default_metrics(self) -> List:
        """Return default metrics for evaluation."""
        return [
            ResponseRelevancy(),
            Faithfulness(),
            LLMContextPrecisionWithReference(),
            LLMContextRecall(),
        ]

    def evaluate(
        self,
        question: str,
        contexts: List[str],
        answer: str,
        ground_truth: Optional[List[str]] = None,
    ) -> Dict[str, float | str]:
        """Evaluate the given response with the provided metrics.

        Args:
            question: The input query.
            contexts: Retrieved context passages.
            answer: The generated response.
            ground_truth: The reference answer (optional).

        Returns:
            A dictionary containing evaluation scores.
        """
        dataset = EvaluationDataset.from_list(
            [
                {
                    "user_input": question,
                    "retrieved_contexts": contexts,
                    "response": answer,
                    "reference": ground_truth[0] if ground_truth else "",
                }
            ]
        )
        results = evaluate(
            dataset=dataset, metrics=self.metrics, llm=self.evaluator_llm
        )
        logger.info(f"Evaluation results: {results}")
        return results.to_pandas().to_dict(orient="records")[0]

    def evaluate_dataset(
        self, dataset: List[Dict[str, str | List[str]]]
    ) -> pd.DataFrame:
        """Evaluate a dataset containing multiple question-context-answer pairs.

        Args:
            dataset: A list of dictionaries, each containing:
                - 'question': The query.
                - 'contexts': Retrieved context passages.
                - 'answer': The generated response.
                - 'ground_truth': The reference answers (optional).

        Returns:
            A pandas DataFrame with evaluation scores for each sample.
        """
        formatted_dataset = EvaluationDataset.from_list(
            [
                {
                    "user_input": item["question"],
                    "retrieved_contexts": item["contexts"],
                    "response": item["answer"],
                    "reference": item["ground_truth"][0]
                    if "ground_truth" in item and item["ground_truth"]
                    else "",
                }
                for item in dataset
            ]
        )
        results = evaluate(
            dataset=formatted_dataset, metrics=self.metrics, llm=self.evaluator_llm
        )
        logger.info(f"Evaluation results: {results}")
        return results.to_pandas()
