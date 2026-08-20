# -*- coding: UTF-8 -*-
# buildVars.py - variables used by SCons when building the addon.

def _(x):
    return x

# Add-on information variables
addon_info = {
    "addon_name": "YoutubePlus",
    "addon_version": "2026.8.19",
# Translators: Summary for this add-on
    "addon_summary": _("YouTubePlus"),
    # Translators: Long description to be shown for this add-on on add-on information from add-ons manager
    "addon_description": _("""YoutubePlus is an add-on for those who enjoy YouTube but find many web features difficult to access, such as reading comments or live chat.
We bring these features to you through the NVDA user interface in an accessible, shortcut-driven, and customizable format.
Users do not need to deal with API keys or link any personal data to the add-on.

Features:
• Follow your favorite channels and be certain you'll see every video they post, without being filtered out by YouTube's algorithm.
• A full Favorites system for videos, channels, and playlists, plus a Watch List for videos you want to watch later — with categories, sorting, and background updates to keep channel and playlist info current.
• Built-in search with saved search history, plus a Quick Search shortcut that searches instantly using selected text or clipboard content.
• Browse a channel's videos, shorts, streams, playlists, and podcasts directly, without leaving the accessible interface.
• Read comments and follow live chat replays.
• Read comments and follow live chat replays.
• Send a video's thumbnail straight to the Be My Eyes app for a live description (Be My Eyes must be installed
• Download videos, audio, or subtitles (with multiple format options) for offline use.
• Supports multiple user profiles, with backup and restore built in."""),
    "addon_author": "NVDA_TH <nvdainth@gmail.com>, assisted by A.I.",
    "addon_url": "https://nvda.in.th/youtube-plus",
    "addon_docFileName": "readme.html",
    "addon_minimumNVDAVersion": "2025.1",
    "addon_lastTestedNVDAVersion": "2026.1",
    "addon_updateChannel": "stable",
}

pythonSources = [
    "addon/globalPlugins",
]

i18nSources = [
    "buildVars.py",
    "addon/globalPlugins/YoutubePlus/*.py",
]

docFiles = ["readme.html"]

tests = []
excludedFiles = []
baseLanguage = "en"
markdownExtensions = []