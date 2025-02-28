# Copyright 2025 TigerGraph Inc.
# Licensed under the Apache License, Version 2.0.
# See the LICENSE file or https://www.apache.org/licenses/LICENSE-2.0
#
# Permission is granted to use, copy, modify, and distribute this software
# under the License. The software is provided "AS IS", without warranty.

from tenacity import (
    AsyncRetrying,
    stop_after_attempt,
    wait_exponential_jitter,
    retry_if_exception_type,
)


class RetryMixin:
    """
    Mixin for initializing a retry mechanism with configurable parameters.
    """

    def initialize_retryer(self, max_retries: int, max_wait: int) -> AsyncRetrying:
        """
        Initialize the retry mechanism with exponential backoff and jitter.

        Args:
            max_retries: Maximum number of retry attempts.
            max_wait: Maximum wait time between retries in seconds.

        Returns:
            AsyncRetrying: Configured retrying instance with specified parameters.
        """
        return AsyncRetrying(
            stop=stop_after_attempt(max_retries),
            wait=wait_exponential_jitter(max=max_wait),
            reraise=True,
            retry=retry_if_exception_type(Exception),
        )
