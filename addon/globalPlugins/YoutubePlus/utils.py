# -*- coding: utf-8 -*-
# utils.py for Youtube Plus NVDA Addon

import time
import functools
import yt_dlp.utils
import logging
from socket import timeout as TimeoutError

def retry_on_network_error(retries=3, delay=5):
    """
    A decorator to retry a function on specific, transient network-related errors.
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            for i in range(retries):
                try:
                    return func(*args, **kwargs)
                except (yt_dlp.utils.DownloadError, ConnectionError, TimeoutError) as e:
                    # We will only retry on actual transient network errors.
                    # yt_dlp.utils.DownloadError is very broad, so we inspect its message.
                    # Common transient error strings from yt-dlp include 'timed out', 'Network is unreachable', HTTP 5xx codes, etc.
                    error_str = str(e).lower()
                    is_retryable = (
                        isinstance(e, (ConnectionError, TimeoutError)) or
                        "timed out" in error_str or
                        "network is unreachable" in error_str or
                        "tls handshake" in error_str or
                        "http error 50" in error_str # Catches 500, 502, 503, 504...
                    )

                    if is_retryable:
                        if i < retries - 1:
                            logging.warning(f"Network error encountered: '{e}'. Retrying in {delay}s... ({i+1}/{retries})")
                            time.sleep(delay)
                        else:
                            logging.error(f"Network error persisted after {retries} retries. Failing.", exc_info=True)
                            raise e  # Re-raise the last exception if all retries fail
                    else:
                        # If it's another type of DownloadError (e.g., 404 Not Found, private video), fail immediately.
                        logging.error("A non-retryable DownloadError occurred.", exc_info=True)
                        raise e
        return wrapper
    return decorator