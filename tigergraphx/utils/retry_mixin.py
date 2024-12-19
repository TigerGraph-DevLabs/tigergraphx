from tenacity import (
    AsyncRetrying,
    stop_after_attempt,
    wait_exponential_jitter,
    retry_if_exception_type,
)


class RetryMixin:
    """Mixin for initializing a retry mechanism."""

    def initialize_retryer(self, max_retries: int, max_wait: int) -> AsyncRetrying:
        """Initialize the retry mechanism.

        Args:
            max_retries (int): Maximum number of retry attempts.
            max_wait (int): Maximum wait time between retries in seconds.

        Returns:
            AsyncRetrying: Configured retrying instance.
        """
        return AsyncRetrying(
            stop=stop_after_attempt(max_retries),
            wait=wait_exponential_jitter(max=max_wait),
            reraise=True,
            retry=retry_if_exception_type(Exception),
        )
