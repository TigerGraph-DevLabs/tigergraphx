# Copyright 2025 TigerGraph Inc.
# Licensed under the Apache License, Version 2.0.
# See the LICENSE file or https://www.apache.org/licenses/LICENSE-2.0
#
# Permission is granted to use, copy, modify, and distribute this software
# under the License. The software is provided "AS IS", without warranty.

from abc import ABC, abstractmethod
from typing import Any

from tigergraphx.config import BaseLLMConfig


class BaseLLMManager(ABC):
    """Base class for LLM implementations."""

    def __init__(self, config: BaseLLMConfig):
        """
        Initialize the base LLM manager.

        Args:
            config: Configuration for the LLM.
        """
        self.config = config

    @abstractmethod
    def get_llm(self) -> Any:
        """
        Retrieve the initialized LLM instance.

        Returns:
            The initialized LLM instance.
        """
        pass
