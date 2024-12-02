from tenacity import (
    AsyncRetrying,
    stop_after_attempt,
    wait_exponential_jitter,
    retry_if_exception_type,
)


class RetryMixin:
    """Mixin to provide retryer initialization for robust error handling."""

    def initialize_retryer(self, max_retries: int, max_wait: int) -> AsyncRetrying:
        """Initialize retry mechanism with the given configuration."""
        return AsyncRetrying(
            stop=stop_after_attempt(max_retries),
            wait=wait_exponential_jitter(max=max_wait),
            reraise=True,
            retry=retry_if_exception_type(Exception),
        )
