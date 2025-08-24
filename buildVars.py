# -*- coding: UTF-8 -*-
# buildVars.py - variables used by SCons when building the addon.

# Add-on information variables
addon_info = {
    "addon_name": "YoutubePlus",

    "addon_version": "2025.8.211",

    "addon_author": "NVDA_TH <nvdainth@gmail.com>, assisted by A.I.",

    "addon_summary": "YouTube Plus can monitor a live chat, view comments and more.",

    "addon_description": (
        "A complete toolkit for YouTube. Allows NVDA users to monitor live chat in real-time, "
        "view/search comments and live chat replays, get detailed video information, and download "
        "videos (MP4) or audio (M4A). Features automatic URL detection and background processing "
        "to keep NVDA responsive."
    ),

    "addon_url": "https://nvda.in.th",

    "addon_docFileName": "readme.html",

    "addon_minimumNVDAVersion": "2025.1",
    "addon_lastTestedNVDAVersion": "2025.2",

    "addon_updateChannel": None,
}

pythonSources = [
    "addon/globalPlugins",
]

i18nSources = []
docFiles = ["readme.html"]

tests = []
excludedFiles = [] 