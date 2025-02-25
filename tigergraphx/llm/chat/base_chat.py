# Copyright 2025 TigerGraph Inc.
# Licensed under the Apache License, Version 2.0.
# See the LICENSE file or https://www.apache.org/licenses/LICENSE-2.0
#
# Permission is granted to use, copy, modify, and distribute this software
# under the License. The software is provided "AS IS", without warranty.

from abc import ABC, abstractmethod
from typing import List, Any

from tigergraphx.config import BaseChatConfig


class BaseChat(ABC):
    """Base class for chat models."""

    def __init__(self, config: BaseChatConfig):
        """
        Initialize the chat model with the given configuration.

        Args:
            config: Configuration for the chat model.
        """
        self.config = config

    @abstractmethod
    async def chat(self, messages: List[Any]) -> str:
        """
        Asynchronously process the messages and return the generated response.

        Args:
            messages: A list of messages to process.

        Returns:
            The generated response.
        """
        pass
