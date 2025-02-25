# Copyright 2025 TigerGraph Inc.
# Licensed under the Apache License, Version 2.0.
# See the LICENSE file or https://www.apache.org/licenses/LICENSE-2.0
#
# Permission is granted to use, copy, modify, and distribute this software
# under the License. The software is provided "AS IS", without warranty.

from pydantic import Field
from ..base_config import BaseConfig


class BaseChatConfig(BaseConfig):
    """
    Base configuration class for chat models.
    """

    type: str = Field(
        description="Mandatory base type; derived classes can override or set a default."
    )


class OpenAIChatConfig(BaseChatConfig):
    """
    Configuration class for OpenAI Chat models.
    """

    type: str = Field(
        default="OpenAI", description="Default type for OpenAIChatConfig."
    )
    model: str = Field(default="gpt-4o-mini", description="Default OpenAI model.")
    max_retries: int = Field(
        default=10, description="Maximum number of retries for API calls."
    )
