# Youtube Plus for NVDA

"Youtube Plus" is a comprehensive toolkit that enhances the YouTube experience for visually impaired users with NVDA. It provides an accessible interface to monitor live chats, read comments, get detailed video information, and download videos or audio directly.

Designed with accessibility and responsiveness in mind, it features automatic URL detection and background processing to ensure a smooth, freeze-free workflow.

## Features

- **Live Chat Monitoring:** Monitor YouTube live chat in real-time.
- **View Comments & live chat Replay:** Download and view the full comment section or the complete live chat replay from any video.
- **Get Video Info:** Instantly get detailed information about a video, including title, channel, duration, view/like/comment counts, and description.
- **Download Video & Audio:** Download videos directly as MP4 files or audio-only as M4A files, without requiring any additional programs.
- **Automatic URL Detection:** Automatically finds a YouTube URL from your browser or clipboard, eliminating manual copy-pasting.
- **Smart Content Selection:** Detects if a video was a past live stream and prompts you to choose between viewing comments or the live chat replay.
- **Accessible Dialogs:** All content is displayed in fully accessible dialogs with search functionality and intuitive keyboard shortcuts.
- **Export to File:** Export the full chat log or comment list to a `.txt` file.
- **Responsive & Non-Blocking:** All network operations run in the background, ensuring the NVDA interface never freezes.
- **Audible Feedback:** Provides clear tones and spoken messages to inform you about the status of operations (e.g., working, success, failure).

## Keyboard Shortcuts

This addon uses a layered command system for easy access without key conflicts.

1.  First, press **NVDA+Shift+Y** to enter the Youtube Plus command layer.
2.  Then, press one of the following keys:

    - **g:** **G**et Data - The universal command to get Live Chat, Comments, or Live Chat Replay from a detected URL.
    - **i:** **I**nfo - Get detailed information about the video from a detected URL.
    - **d:** **D**ownload - Start the process to download the video or audio from a detected URL.
    - **s:** **S**top - Stop the currently active live chat monitoring.
    - **v:** **V**iew - Show the live chat messages dialog if monitoring is active.
    - **r:** **R**ead Toggle - Toggle the automatic reading of incoming live chat messages.
    - **h:** **H**elp - Show the help dialog with a list of all commands.

**Note:** If the main shortcut (`NVDA+Shift+Y`) conflicts with another addon, you can change it in `NVDA Menu -> Preferences -> Input Gestures...`, under the "Youtube Plus" category.

## Configuration

Settings are available in the NVDA Settings dialog (`NVDA Menu -> Preferences -> Settings...`) under the **"Youtube Plus"** category:

- Enable or disable automatic speaking of incoming live chat messages.
- Set the refresh interval (in seconds) for fetching new live chat messages.
- Set a default folder path for all exported files and downloads.

## Requirements

- NVDA 2019.3 or later.
- An active internet connection.
- All necessary components are bundled with the addon.