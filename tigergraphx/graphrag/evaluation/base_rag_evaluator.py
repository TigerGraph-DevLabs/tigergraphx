from abc import ABC, abstractmethod
from typing import Dict, List, Optional
import pandas as pd


class BaseRAGEvaluator(ABC):
    """Abstract base class for RAG evaluation frameworks."""

    def __init__(self, metrics: Optional[List] = None):
        """Initialize the evaluator with optional custom metrics."""
        self.metrics = metrics if metrics else self.default_metrics()

    @abstractmethod
    def default_metrics(self) -> List:
        """Define default metrics for evaluation."""
        pass

    @abstractmethod
    def evaluate(
        self,
        question: str,
        contexts: List[str],
        answer: str,
        ground_truth: Optional[List[str]] = None,
    ) -> Dict[str, float | str]:
        """Evaluate the RAG system's output using a chosen framework."""
        pass

    @abstractmethod
    def evaluate_dataset(
        self, dataset: List[Dict[str, str | List[str]]]
    ) -> pd.DataFrame:
        """Evaluate a dataset containing multiple question-context-answer pairs."""
        pass
