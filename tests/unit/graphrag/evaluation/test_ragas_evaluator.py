import pytest
import pandas as pd
from ragas.metrics import (
    ResponseRelevancy,
    Faithfulness,
    LLMContextPrecisionWithReference,
    LLMContextRecall,
)
from ragas.dataset_schema import EvaluationResult, EvaluationDataset

from tigergraphx.graphrag import RagasEvaluator


class TestRagasEvaluator:
    """Unit tests for RagasEvaluator."""

    @pytest.fixture(autouse=True)
    def setup(self, mocker):
        """Set up a RagasEvaluator instance with mocked dependencies."""
        # Mock ChatOpenAI before initializing RagasEvaluator
        self.mock_llm = mocker.patch(
            "tigergraphx.graphrag.evaluation.ragas_evaluator.ChatOpenAI", autospec=True
        )
        self.mock_llm_instance = self.mock_llm.return_value

        # Mock LangchainLLMWrapper
        self.mock_evaluator_llm = mocker.patch(
            "tigergraphx.graphrag.evaluation.ragas_evaluator.LangchainLLMWrapper",
            autospec=True,
        )
        self.mock_evaluator_llm_instance = self.mock_evaluator_llm.return_value

        # Initialize the evaluator with mocked LLM
        self.evaluator = RagasEvaluator(model="gpt-4o")

        self.evaluator = RagasEvaluator(model="gpt-4o")

        # Mock dependencies
        mocker.patch.object(self.evaluator, "llm")
        mocker.patch.object(self.evaluator, "evaluator_llm")

        # Mock default metrics
        self.evaluator.metrics = [
            ResponseRelevancy(),
            Faithfulness(),
            LLMContextPrecisionWithReference(),
            LLMContextRecall(),
        ]

        # Create a mock EvaluationResult instance
        self.mock_evaluation_result = mocker.MagicMock(spec=EvaluationResult)
        self.mock_evaluation_result.dataset = EvaluationDataset([])

        # Patch `evaluate` to return the mocked EvaluationResult
        self.mock_evaluate = mocker.patch(
            "tigergraphx.graphrag.evaluation.ragas_evaluator.evaluate",
            return_value=self.mock_evaluation_result,
        )

    def test_default_metrics(self):
        """Test that the default metrics are correctly set."""
        default_metrics = self.evaluator.default_metrics()
        assert len(default_metrics) == 4
        assert isinstance(default_metrics[0], ResponseRelevancy)
        assert isinstance(default_metrics[1], Faithfulness)
        assert isinstance(default_metrics[2], LLMContextPrecisionWithReference)
        assert isinstance(default_metrics[3], LLMContextRecall)

    def test_evaluate(self):
        """Test evaluation of a single query with mocked `ragas.evaluate`."""
        self.mock_evaluation_result.to_pandas.return_value = pd.DataFrame(
            [
                {
                    "context_recall": 1.0,
                    "faithfulness": 0.9,
                    "factual_correctness": 0.85,
                }
            ]
        )
        result = self.evaluator.evaluate(
            question="What is AI?",
            contexts=["AI is a branch of computer science."],
            answer="AI is about creating intelligent machines.",
            ground_truth=["AI is the simulation of human intelligence by machines."],
        )

        assert isinstance(result, dict)
        assert "context_recall" in result
        assert result["context_recall"] == 1.0
        assert "faithfulness" in result
        assert result["faithfulness"] == 0.9
        assert "factual_correctness" in result
        assert result["factual_correctness"] == 0.85

        # Ensure `ragas.evaluate` was called once
        self.mock_evaluate.assert_called_once()

    def test_evaluate_dataset(self):
        """Test evaluation of a dataset with mocked `ragas.evaluate`."""
        self.mock_evaluation_result.to_pandas.return_value = pd.DataFrame(
            [
                {
                    "context_recall": 1.0,
                    "faithfulness": 0.9,
                    "factual_correctness": 0.85,
                },
                {
                    "context_recall": 1.0,
                    "faithfulness": 0.9,
                    "factual_correctness": 0.85,
                },
            ]
        )
        dataset = [
            {
                "question": "What is AI?",
                "contexts": ["AI is a branch of computer science."],
                "answer": "AI is about creating intelligent machines.",
                "ground_truth": [
                    "AI is the simulation of human intelligence by machines."
                ],
            },
            {
                "question": "What is ML?",
                "contexts": ["ML is a subset of AI."],
                "answer": "ML allows computers to learn from data.",
                "ground_truth": [
                    "ML enables computers to learn without explicit programming."
                ],
            },
        ]

        result = self.evaluator.evaluate_dataset(dataset)

        assert isinstance(result, pd.DataFrame)
        assert len(result) == 2

        # Ensure `ragas.evaluate` was called once
        self.mock_evaluate.assert_called_once()

    def test_custom_metrics(self):
        """Test that custom metrics can be passed to RagasEvaluator."""
        custom_metrics = [Faithfulness()]
        evaluator = RagasEvaluator(model="gpt-4o", metrics=custom_metrics)

        assert len(evaluator.metrics) == 1
        assert isinstance(evaluator.metrics[0], Faithfulness)
