# -*- coding: UTF-8 -*-
# buildVars.py - variables used by SCons when building the addon.

# Add-on information variables
addon_info = {
    "addon_name": "YoutubePlus",
    "addon_version": "2026.2.4",
    "addon_author": "NVDA_TH <nvdainth@gmail.com>, assisted by A.I.",
    "addon_summary": "YouTubePlus",
    "addon_description": (
        """YoutubePlus is an add-on for those who enjoy YouTube but find many web features difficult to access, such as reading video comments.
We bring these features to you through the NVDA user interface in an accessible, shortcut-driven, and customizable format.
Users do not need to deal with API keys or link any personal data to the add-on.

features:       
• You can follow your favorite channels and be certain that you will see every video they post without being filtered out by YouTube's algorithm.
• we offer a Favorites system for videos, channels, playlists, and a Watch List for saving videos you're interested in but don't have time to watch yet.
• built-in search system that displays results within the same accessible UI as other features, rather than just providing a search box that opens the web results.
• included download feature for saving videos or audio files."""
),
    "addon_url": "https://nvda.in.th/youtube-plus",
    "addon_docFileName": "readme.html",
    "addon_minimumNVDAVersion": "2025.1",
    "addon_lastTestedNVDAVersion": "2025.3.2",
    "addon_updateChannel": None,
}

pythonSources = [
    "addon/globalPlugins",
]

i18nSources = []
docFiles = ["readme.html"]

tests = []
excludedFiles = [] 