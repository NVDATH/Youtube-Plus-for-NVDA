# -*- coding: UTF-8 -*-
# buildVars.py - variables used by SCons when building the addon.

def _(x):
    return x

# Add-on information variables
addon_info = {
    "addon_name": "YoutubePlus",
    "addon_version": "2026.9.3",
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
• Read comments and live chat replays, and follow a live chat as it happens: read it aloud in a separate voice of your choice, with alert sounds for Super Chats, Super Stickers and new channel members.
• Send a video's thumbnail straight to the Be My Eyes app for a live description (Be My Eyes must be installed)
• Download videos, audio, or subtitles (with multiple format options) for offline use.
• Supports multiple user profiles, with backup and restore built in."""),
    "addon_author": "NVDA_TH <nvdainth@gmail.com>, assisted by A.I.",
    "addon_url": "https://nvda.in.th/youtube-plus",
    "addon_docFileName": "readme.html",
    "addon_minimumNVDAVersion": "2025.1",
    "addon_lastTestedNVDAVersion": "2026.2",
    "addon_updateChannel": "stable",
    # Translators: What's new text for this add-on version, shown in NVDA's Add-on Store.
    # NOTE: content between the CHANGELOG markers below is auto-replaced by
    # scripts/sync_changelog.py using the latest "## " section of changelog.md.
    # Do not edit by hand; edit changelog.md instead and re-run the sync script.
    "addon_changelog": _(
        # CHANGELOG-START
        """### New Features and Improvements

* Added a **Voice profile** setting that lets you select an NVDA configuration profile for incoming live chat messages. Chat uses the selected profile's synthesizer, voice, rate, pitch, and volume, while NVDA's regular speech remains unchanged. A separate synthesizer runs alongside NVDA, allowing chat to use a different synthesizer (such as SAPI 5) without being interrupted by key presses or NVDA speech. Available when **Automatically speak incoming live chat** is enabled. Suggested by @MichalSuchy (#13).
* Added configurable sound alerts for Super Chats, Super Stickers, and new member events. Each event type can have its own alert sound, selected from the `.wav` files in the add-on's `sounds` folder. Alerts work independently of automatic chat speech.
* New member events now appear in the live chat window and exported chat. Super Chats, Super Stickers, and new member events are prioritized over regular messages and are no longer skipped during periods of heavy chat activity.
* Added a connection announcement when starting to monitor a live stream, replacing the progress sound as the only indication that the add-on is connecting to live chat.
* Search results can now be filtered by content type (videos, channels, or playlists), duration, upload date, and sort order. Filters can be combined.
* Search History now saves the filters used for each search, allowing **Search Again** to reproduce the same filtered results.
* Selecting a channel or playlist in search results now correctly opens, copies, and expands it instead of treating it as a video.
* Added a **Within channel** option to the search dialog for searching videos from a specific channel. Channel names are suggested from Search History, Favorite Channels, and Subscribed Channels. If the entered name doesn't match any suggestions, the add-on looks up the channel on YouTube and asks you to confirm the intended channel.
* Checkbox lists in the settings dialog and Manage Subscriptions now automatically select their first item.
* Added Vietnamese (`vi`) interface translation and documentation, contributed by @ninhhoang205.

### Bug Fixes

* Pressing **L** on a stream that is already being monitored now opens its live chat window without restarting the monitoring session.
* When switching to a different live stream while monitoring another, the add-on now asks for confirmation, offers to save the chat being replaced, and fully replaces the existing session. Previously, the old session could continue running alongside the new one, resulting in duplicate or mixed messages.
* Fixed URLs without a scheme (e.g. `youtube.com/watch?v=...` or `youtu.be/...`) failing across commands and **Add from clipboard** actions that read URLs from the clipboard. These URLs are now handled correctly even without an `https://` prefix.

### Dependencies

* Updated yt-dlp to 2026.10.26."""
        # CHANGELOG-END
    ),
}

pythonSources = [
    "addon/globalPlugins",
]

i18nSources = [
    "buildVars.py",
    "addon/installTasks.py",
    "addon/globalPlugins/YoutubePlus/*.py",
]

docFiles = ["readme.html"]

tests = []
excludedFiles = []
baseLanguage = "en"
markdownExtensions = []