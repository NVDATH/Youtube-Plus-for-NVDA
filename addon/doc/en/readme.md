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

1.  First, press **NVDA+Y** to enter the Youtube Plus command layer.
2.  Then, press one of the following keys:

    | Key | Function | Description |
    | :--- | :--- | :--- |
    | **a** | **A**dd Menu | Show menu to add current video, channel, or playlist to favorites. |
    | **d** | **D**ownload | Start the process to download the video or audio from a detected URL. |
    | **e** | YouTube Search | Search YouTube for videos, channels, or playlists. |
    | **f** | **F**avorite Videos | Show dialog to manage saved favorite videos. |
    | **c** | Favorite **C**hannels | Show dialog to manage saved favorite channels. |
    | **p** | Favorite **P**laylists | Show dialog to manage saved favorite playlists. |
    | **i** | Video **I**nfo | Get detailed information about the video from a detected URL. |
    | **l** | **L**et Data | Get Live Chat, Comments, or Live Chat Replay from a detected URL. |
    | **shift+l** | Stop Live Chat | Stop the currently active live chat monitoring. |
    | **v** | **V**iew Live Messages | Show the dialog containing the live chat messages (if monitoring is active). |
    | **m** | **M**anage Subscriptions | Show dialog to manage the list of channels you are tracking. |
    | **s** | **S**ubscription Feed | Show latest videos from your tracked channels. |
    | **r** | **R**ead Toggle | Toggle the automatic reading of incoming live chat messages. |
    | **h** | **H**elp | Show the help dialog with a list of all commands. |

**Note:** If the main shortcut (`NVDA+Y`) conflicts with another addon, you can change it in `NVDA Menu -> Preferences -> Input Gestures...`, under the "Youtube Plus" category.

## Configuration

Settings are available in the NVDA Settings dialog (`NVDA Menu -> Preferences -> Settings...`) under the **"Youtube Plus"** category. Here is a detailed explanation of each option:

### General & Network
- **Notification mode:** Choose how the addon provides feedback during long operations:
  - *Beep:* Plays beep tones.
  - *Sound:* Plays sound effects.
  - *Silent:* No audible feedback.
- **Background update interval:** Set how often the addon checks for updates (e.g., new videos from subscriptions) in the background. You can disable this or set intervals from 15 minutes up to 24 hours.

### Content & Sorting
- **Default sort order:** Choose whether lists (like comments or channel videos) appear with **Newest First** or **Oldest First**.
- **Items to fetch:** Determine how many items to retrieve at a time when loading playlists or channel videos (Default: 20).
- **Default content types:** Select what types of content to fetch for new subscriptions:
  - *Videos*
  - *Shorts*
  - *Live*

### Live Chat
- **Automatically speak incoming live chat:** If checked, NVDA will read new chat messages aloud automatically.
- **Live chat refresh interval:** How many seconds to wait before checking for new messages (Default: 5 seconds).
- **Message history limit:** The maximum number of chat messages to keep in memory during a session.

### Account & Storage
- **Cookie method:** This setting allows the addon to access members-only content, age-restricted videos, or premium subscriptions by using cookies from a browser logged into your account.
  - **Do not use cookies (Default):** Recommended for general use, as the addon works anonymously.
  - **Browser Selection (Chrome, Firefox, Edge, etc.):** Select a browser only if you need to access restricted content that requires login.
  - **Usage Tip (Secondary Browser Strategy):** The addon cannot access cookies from a browser that is currently open and actively watching videos due to file locking. It is highly recommended to use a **secondary browser** for this setting.
  - **Example:** If you regularly watch YouTube on **Chrome**, you should log in to your account on a different browser like **Edge** and ensure **Edge is completely closed**. Then, select **Edge** in these settings. This allows the addon to read the necessary cookies without conflicting with your active viewing session on Chrome.
- **Default download and export folder path:** Choose the folder where downloaded videos, audio, and exported logs will be saved.
- **Clear Data:** A button to permanently delete all saved favorite videos, channels, and subscription data.

## Requirements

- NVDA 2025.1 or later.
- An active internet connection.
- All necessary components are bundled with the addon.