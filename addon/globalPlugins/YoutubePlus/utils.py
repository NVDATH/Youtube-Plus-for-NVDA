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
import base64
import urllib.parse
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


# --- YouTube search filter (sp=) encoding -----------------------------------
#
# YouTube's search-filter panel is encoded as a Protocol Buffers message,
# base64-encoded, and passed as the `sp` query parameter on
# https://www.youtube.com/results?search_query=...&sp=...
# yt-dlp's `ytsearchN:` pseudo-URL does NOT support this -- it's a separate,
# plain-keyword-only extractor. Filtering only works by hitting the real
# search results URL above (which yt-dlp does parse and forward correctly).
#
# Field numbers below are unofficial (Google has never published this
# schema) but were confirmed by manually decoding several known-good `sp`
# values byte-by-byte, cross-checked against independent sources (Invidious,
# various YouTube-scraping API docs, and real sp values seen in yt-dlp bug
# reports). If a future YouTube change makes these stop working, this
# comment block is the first place to check/re-derive.
#
# Credit: the reverse-engineered field mapping used as the reference point
# here comes from the open-source Invidious project
# (https://github.com/iv-org/invidious, AGPLv3) -- specifically its
# `produce_search_params` test fixtures, against which this file's field
# numbers were cross-checked. The encoder code below is written
# independently for this add-on, not copied from Invidious.
#
# Outer message:
#   field 1 (varint)           -> sort_by
#   field 2 (embedded message) -> filter options, below
# Filter options message (field 2 of the outer message):
#   field 1 (varint) -> upload_date
#   field 2 (varint) -> content type
#   field 3 (varint) -> duration
# (Per-feature flags like HD/4K/live/etc. live in this same embedded message
# at other field numbers, but aren't implemented here -- out of scope.)

_YT_SORT_VALUES = {
    "upload_date": 2,
    "view_count": 3,
}
_YT_UPLOAD_DATE_VALUES = {
    "hour": 1,
    "today": 2,
    "week": 3,
    "month": 4,
    "year": 5,
}
_YT_TYPE_VALUES = {
    "video": 1,
    "channel": 2,
    "playlist": 3,
}
_YT_DURATION_VALUES = {
    "short": 1,   # under 4 minutes
    "long": 2,    # over 20 minutes
    "medium": 3,  # 4-20 minutes
}


def _pb_varint(value):
    """Encode a non-negative int as a protobuf varint."""
    out = bytearray()
    while True:
        byte = value & 0x7F
        value >>= 7
        if value:
            out.append(byte | 0x80)
        else:
            out.append(byte)
            return bytes(out)


def _pb_field_varint(field_number, value):
    tag = (field_number << 3) | 0  # wire type 0 = varint
    return _pb_varint(tag) + _pb_varint(value)


def _pb_field_embedded(field_number, payload):
    tag = (field_number << 3) | 2  # wire type 2 = length-delimited
    return _pb_varint(tag) + _pb_varint(len(payload)) + payload


def build_youtube_search_params(sort_by=None, upload_date=None, content_type=None, duration=None):
    """
    Builds the `sp` query-parameter value for a YouTube search URL from any
    combination of filters (all optional):
      sort_by:      None/"relevance" (default) | "upload_date" | "view_count"
      upload_date:  None | "hour" | "today" | "week" | "month" | "year"
      content_type: None | "video" | "channel" | "playlist"
      duration:     None | "short" | "long" | "medium"
    Returns None if every argument is left at its default -- the caller
    should skip adding `sp` to the URL entirely in that case.
    """
    filter_payload = b""
    if upload_date in _YT_UPLOAD_DATE_VALUES:
        filter_payload += _pb_field_varint(1, _YT_UPLOAD_DATE_VALUES[upload_date])
    if content_type in _YT_TYPE_VALUES:
        filter_payload += _pb_field_varint(2, _YT_TYPE_VALUES[content_type])
    if duration in _YT_DURATION_VALUES:
        filter_payload += _pb_field_varint(3, _YT_DURATION_VALUES[duration])

    message = b""
    if sort_by in _YT_SORT_VALUES:
        message += _pb_field_varint(1, _YT_SORT_VALUES[sort_by])
    if filter_payload:
        message += _pb_field_embedded(2, filter_payload)

    if not message:
        return None
    return base64.b64encode(message).decode("ascii")


def build_youtube_search_url(query, sort_by=None, upload_date=None, content_type=None, duration=None):
    """
    Builds a full YouTube search-results URL. If every filter argument is
    left at its default, this is equivalent (in result set) to yt-dlp's own
    `ytsearch:` prefix -- just reached via the real search page instead of
    the ytsearch pseudo-extractor, which is what makes filtering possible.
    """
    url = "https://www.youtube.com/results?search_query=" + urllib.parse.quote(query)
    sp = build_youtube_search_params(sort_by, upload_date, content_type, duration)
    if sp:
        url += "&sp=" + urllib.parse.quote(sp)
    return url