# -*- coding: utf-8 -*-
# utils.py for Youtube Plus NVDA Addon
# This file contains functions adapted from the BrowserNav addon for NVDA
# Original Copyright (C) 2017-2022 Tony Malykh
# Licensed under the GNU General Public License.

import time
import functools
import logging
import types
import itertools
import api
import controlTypes
import winUser
import IAccessibleHandler
import NVDAObjects.IAccessible
import core
import yt_dlp.utils
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
                    error_str = str(e).lower()
                    is_retryable = (
                        isinstance(e, (ConnectionError, TimeoutError)) or
                        "timed out" in error_str or
                        "network is unreachable" in error_str or
                        "tls handshake" in error_str or
                        "http error 50" in error_str 
                    )

                    if is_retryable:
                        if i < retries - 1:
                            logging.warning(f"Network error encountered: '{e}'. Retrying in {delay}s... ({i+1}/{retries})")
                            time.sleep(delay)
                        else:
                            logging.error(f"Network error persisted after {retries} retries. Failing.", exc_info=True)
                            raise e
                    else:
                        logging.debug("A non-retryable DownloadError occurred: %s", e)
                        raise e
        return wrapper
    return decorator

def executeAsynchronously(gen):
    if not isinstance(gen, types.GeneratorType):
        raise Exception("Generator function required")
    try:
        value = gen.__next__()
    except StopIteration:
        return
    core.callLater(value, executeAsynchronously, gen)

def getIA2Document(textInfo=None):
    focus = api.getFocusObject()
    for obj in itertools.chain(api.getFocusAncestors(), [focus]):
        if obj.role == controlTypes.Role.DOCUMENT:
            return obj
    return None

def getIA2FocusedObject(obj):
    if obj is None:
        return None
    tup = IAccessibleHandler.accFocus(obj.IAccessibleObject)
    if tup is None:
        return None
    ia2Focus, ia2ChildId = tup
    realObj = NVDAObjects.IAccessible.IAccessible(
        IAccessibleObject=ia2Focus,
        IAccessibleChildID=ia2ChildId,
    )
    return realObj

def getIA2DocumentInThread():
    focus = api.getFocusObject()
    obj = NVDAObjects.IAccessible.getNVDAObjectFromEvent(focus.windowHandle, winUser.OBJID_CLIENT, 0)
    if obj is None:
        return None
    if obj.role == controlTypes.Role.DOCUMENT:
        return obj
    else:
        obj = getIA2FocusedObject(obj) # เรียกใช้ helper function
        while obj is not None:
            if obj.role == controlTypes.Role.DOCUMENT:
                return obj
            obj = obj.parent
        return None