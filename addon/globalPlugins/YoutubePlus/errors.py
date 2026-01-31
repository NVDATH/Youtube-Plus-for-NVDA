# -*- coding: utf-8 -*-
# errors.py for Youtube Plus NVDA Addon

class HandledError(Exception):
    """
    Base exception for errors that are handled and reported to the user,
    and shouldn't be logged as unexpected critical failures.
    """
    pass

class NetworkRetryError(HandledError):
    """Exception raised when a network operation fails after all retries."""
    pass