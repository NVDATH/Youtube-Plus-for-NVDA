# -*- coding: utf-8 -*-
# attachments.py for YoutubePlus NVDA add-on
# Copyright (C) 2025
# This file is covered by the GNU General Public License.

"""
Helpers for downloading a video's thumbnail and handing it off to
Be My Eyes for a live description.

Sending a file to Be My Eyes uses the same ShellExecute trick Explorer
uses for "Open with" on a UWP app: targeting shell:appsFolder\\<AUMID>
with the file path as the parameter. This is EXPERIMENTAL -- paste
back the traceback if it doesn't behave as expected on your machine.
"""

import ctypes
import os
import tempfile
import urllib.request
import webbrowser

from logHandler import log

BEMYEYES_AUMID = "BeMyEyes.BeMyEyes_7yeb8xxw19svt!App"
# Microsoft Store product ID for Be My Eyes (Windows app), used to build
# both the ms-windows-store: deep link and the apps.microsoft.com fallback.
BEMYEYES_STORE_PRODUCT_ID = "9MSW46LTDWGF"

_USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"
)


def download_to_temp(url: str, suffix: str = ".jpg") -> str:
    """
    Downloads `url` to a new temp file and returns its path, or raises.
    `suffix` is only a hint for the initial temp filename -- if the
    server's Content-Type says WebP, the file is saved as .webp and then
    converted to PNG using the Pillow copy bundled with NVDA, since not
    every consumer of the resulting file (e.g. Be My Eyes) can be
    guaranteed to handle WebP.
    """
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": _USER_AGENT,
            "Accept": "*/*",
        },
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        status = getattr(response, "status", 200)
        content_type = response.headers.get("Content-Type", "")
        data = response.read()

    if status >= 400:
        raise OSError(f"Download failed: HTTP {status} ({len(data)} bytes)")

    if not content_type.startswith("image/"):
        snippet = data[:200].decode("utf-8", errors="replace")
        raise OSError(f"Expected an image, got Content-Type '{content_type}': {snippet}")

    if content_type.startswith("image/webp"):
        suffix = ".webp"

    fd, path = tempfile.mkstemp(suffix=suffix)
    os.close(fd)

    with open(path, "wb") as f:
        f.write(data)

    if suffix == ".webp":
        try:
            from PIL import Image

            new_path = path + ".png"
            with Image.open(path) as img:
                img.save(new_path, "PNG")
            try:
                os.remove(path)
            except OSError:
                pass
            return new_path
        except Exception as e:
            log.error(f"YoutubePlus: failed to convert WebP thumbnail to PNG: {e}")
            try:
                os.remove(path)
            except OSError:
                pass
            raise OSError(f"Could not convert WebP thumbnail image: {e}")

    return path


def send_to_bemyeyes(file_path: str) -> bool:
    """
    Launches Be My Eyes with `file_path` via ShellExecute against
    shell:appsFolder\\<AUMID>, passing the file path as the parameter --
    this is the same mechanism Explorer uses for "Open with" on a UWP
    app. Returns False if the app isn't installed or launch failed
    (ShellExecute returns a value > 32 on success, an error code
    otherwise).
    """
    target = f"shell:appsFolder\\{BEMYEYES_AUMID}"
    result = ctypes.windll.shell32.ShellExecuteW(None, "open", target, file_path, None, 1)
    return result > 32


def open_bemyeyes_install_page() -> bool:
    """
    Opens the Microsoft Store to the Be My Eyes app page. Prefers the
    ms-windows-store: deep link, which opens straight into the Store app
    with no browser detour, and falls back to the apps.microsoft.com web
    page if that URI scheme doesn't resolve for some reason (older
    Windows builds, N/KN editions without the Store, etc.). Some
    webbrowser.py controllers return False on failure instead of raising,
    so both cases are checked.
    """
    store_uri = f"ms-windows-store://pdp/?productid={BEMYEYES_STORE_PRODUCT_ID}"
    web_url = f"https://apps.microsoft.com/detail/{BEMYEYES_STORE_PRODUCT_ID.lower()}"
    try:
        if webbrowser.open(store_uri):
            return True
    except Exception as e:
        log.warning(f"YoutubePlus: ms-windows-store URI failed, falling back to web link: {e}")
    try:
        return bool(webbrowser.open(web_url))
    except Exception as e:
        log.error(f"YoutubePlus: could not open Be My Eyes Store page: {e}")
        return False
