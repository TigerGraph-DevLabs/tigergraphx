import logging
from functools import wraps


def safe_call(func):
    """
    A decorator to handle errors and log them during method calls.
    """

    @wraps(func)
    def wrapper(self, *args, **kwargs):
        try:
            return func(self, *args, **kwargs)
        except Exception as e:
            logging.error(f"Error during {func.__name__}: {e}")
            return None

    return wrapper
