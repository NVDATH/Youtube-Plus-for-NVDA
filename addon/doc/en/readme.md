# YoutubePlus for NVDA

> YoutubePlus is an add-on for NVDA users who love YouTube but find many features on the website difficult to access — such as reading comments, following channels, or monitoring live chat.
>
> We bring these features into NVDA's user interface in a form that is easy to navigate by keyboard, supports shortcuts, and is fully customizable — **with no API keys or Google/YouTube account login required**.
>
> You can follow your favorite channels and be confident you will see every video from those channels, without YouTube's algorithm filtering them out. A Favorites system is included for videos, channels, playlists, and a Watch List to save content you're interested in but haven't had time to watch yet.
>
> There is a built-in video search that displays results within the add-on's own UI — not just a search box that opens YouTube in the browser. A download feature is included for saving videos and audio as a convenience — if downloading is your primary need, dedicated tools are recommended.
>
> What this add-on does **not** do is embed a video player. We believe the YouTube web player is already accessible enough on its own. If you still find it lacking, you can use other add-ons such as [browserNav](https://addonstore.nvaccess.org/?channel=stable&language=en&apiVersion=2025.3.2&addonId=browsernav) to improve the experience.

---

## Table of Contents

- [Keyboard Shortcuts](#keyboard-shortcuts)
- [Feature Details](#feature-details)
  - [a: Add to... Menu](#a-add-to-menu)
  - [d: Download Video/Audio](#d-download-videoaudio)
  - [b: Download Subtitles](#b-download-subtitles)
  - [e: Search YouTube](#e-search-youtube)
  - [i: Video Info](#i-video-info)
  - [t: Chapters / Timestamps](#t-chapters--timestamps)
  - [l: Comments / Live Chat / Live Chat Replay](#l-comments--live-chat--live-chat-replay)
  - [Favorites (f, c, p, w)](#favorites-f-c-p-w)
  - [s: Subscription Feed](#s-subscription-feed)
  - [m: Manage Subscriptions](#m-manage-subscriptions)
  - [u: User Profile Manager](#u-user-profile-manager)
  - [Video List](#video-list)
- [Settings](#settings)
- [Additional Information](#additional-information)

---

## Keyboard Shortcuts

This add-on uses a **Layer Command** system to avoid conflicts with other add-ons or NVDA commands.

**How to use:**
1. Press **NVDA+Y** to enter YoutubePlus Command Mode (you will hear a notification sound).
2. Press the corresponding letter to activate the desired feature.

> **Note:** If `NVDA+Y` conflicts with another add-on, you can change it at `NVDA → Preferences → Input Gestures...` under the "YoutubePlus" category.

> **URL detection:** For commands that require a video URL, the add-on first checks the **currently open browser window**. If no YouTube URL is found there, it automatically falls back to checking the **clipboard**.

### All keys in YoutubePlus mode

| Key | Feature |
|-----|---------|
| **a** | "Add to..." menu (Favorites / Subscribe) |
| **f** | Open Favorite Videos |
| **c** | Open Favorite Channels |
| **p** | Open Favorite Playlists |
| **w** | Open Watch List |
| **b** | Download subtitles |
| **d** | Download video or audio |
| **e** | Search YouTube |
| **i** | Show video info |
| **t** | Show Chapters / Timestamps |
| **m** | Manage Subscriptions |
| **s** | Open Subscription Feed |
| **u** | Manage User Profiles |
| **l** | Show comments or start live chat monitoring |
| **Shift+L** | Stop live chat monitoring |
| **r** | Toggle automatic live chat reading |
| **v** | Reopen live chat window (while stream is still active) |
| **y** | Open YoutubePlus Settings |
| **h** | Open Help dialog |

---

## Feature Details

### a: Add to... Menu

Opens a submenu to choose where to add the current video or channel:

- **Add to Favorite Videos** — saves the current video to Favorites
- **Add to Favorite Channels** — saves the current video's channel to Favorites
- **Add to Favorite Playlists** — saves the current playlist to Favorites
- **Subscribe to Channel** — follows the channel through the add-on's Subscription system
- **Add to Watch List** — saves the current video to Watch List for viewing later

Most commands work with any YouTube URL format. For example, if you are on a video page and choose "Add to Favorite Channels," the add-on will extract the channel URL automatically.

**Exception:** For Playlists, you must have a YouTube playlist page open, or have a valid playlist URL in the clipboard.

---

### d: Download Video/Audio

Press **NVDA+Y → D** to open a dialog asking whether to download as:

- **Video file (MP4)** — downloads video with audio
- **Audio file (M4A)** — downloads audio only

A progress dialog shows the download percentage while running. A **Cancel** button is available at any time.

Set the destination folder in [Settings](#settings).

> **Note:** This feature is provided for convenience. For bulk downloading, dedicated tools are recommended.

---

### b: Download Subtitles

Press **NVDA+Y → B** to fetch the list of available subtitle languages for the current video, then choose from a dialog. Subtitles are listed in two types:

- **(manual)** — subtitles created by the video creator or the community
- **(auto)** — automatically generated captions by YouTube

Supported file formats: **SRT, VTT, TTML**, and **TXT** (plain text without timecodes). Configurable in [Settings](#settings).

---

### e: Search YouTube

Press **NVDA+Y → E** to open the search window. Type your query and press Enter to search immediately. Press Tab to adjust the number of results (the add-on remembers this value for next time).

Results are displayed in the same [Video List](#video-list) format used throughout the add-on — not as a YouTube web page. Results may include videos, channels, and playlists.

---

### i: Video Info

Press **NVDA+Y → I** to view the following details for the current video:

- Title
- Channel
- Duration
- Upload date
- View count
- Like count
- Comment count
- Description

---

### t: Chapters / Timestamps

Press **NVDA+Y → T** to view the chapter or timestamp list for the current video (if the creator included this information). If the add-on reports "No chapters found," the video simply does not have chapter data.

This window includes:

- **Search field** — filters the chapter list in real time; no need to press Enter
- **Chapter list** — shows chapter title and start time
- **Text area** — displays the selected chapter's name in a readable format
- **Open Chapter button** (or press Space/Enter) — jumps directly to that chapter in the browser
- **Copy Title button** — copies the chapter title
- **Copy URL button** — copies the URL with the timestamp for that chapter
- **Export button** — saves all chapters to a text file

---

### l: Comments / Live Chat / Live Chat Replay

YoutubePlus supports three types of content through this command:

#### 1. Comments (for regular videos)

Press **NVDA+Y → L** while on a video page. The add-on fetches all comments. Pinned comments appear first, followed by all others in the sort order configured in Settings.

**The Comments window includes:**

- **Search field** — filters comments in real time
- **Filter combo box** — preset filters:
  - No Filter — shows all comments
  - Filter by Selected Author — shows only comments from the selected commenter
  - Show Super Chats Only
  - Show Super Stickers Only
  - Show Super Thanks Only
- **Comment list** — shows commenter name and message; reply threading is supported
- **Read-only text area** — shows the full text of the selected comment, useful for long comments
- **Copy button** (Alt+C or Ctrl+C) — copies the selected comment
- **Export button** (Alt+E) — saves all comments to a text file

#### 2. Live Chat (for active live streams)

For videos that are currently live, press L to open a window receiving incoming chat messages. Only messages received after activating this command are shown — no prior history is captured.

- Close and reopen the window with the **V** command as long as monitoring has not been stopped.
- Use the **R** command to toggle automatic reading of new messages — ideal for streams with infrequent messages. For high-volume streams, turning auto-read off and scrolling manually in the window is recommended.
- Use **Shift+L** to stop monitoring. When stopped, the add-on will ask whether you want to save the chat history to a file.

**Related settings:**
- **Automatically speak incoming live chat:** Reads new messages aloud as they arrive (same as the R command, but saved as a default preference).
- **Live chat refresh interval:** How often (in seconds) the add-on checks for new messages (default: 5 seconds).
- **Message history limit:** Maximum messages stored in memory (default: 5,000). The add-on has a hard cap of 200,000 messages to prevent excessive memory use.

#### 3. Live Chat Replay (for past streams)

For previously live videos where the channel has not removed the chat, pressing L will show a dialog asking whether to view **Comments** or the **Live Chat Replay**. The replay window has the same structure as the Comments window, with one addition:

- **Total Paid Amount** — shows the total donations (Super Chats / Super Stickers) collected during the stream

---

### Favorites (f, c, p, w)

The Favorites window is divided into 4 tabs, each accessible by separate commands or all within the same window.

| Key | Tab |
|-----|-----|
| **F** | Saved videos (Favorite Videos) |
| **C** | Saved channels (Favorite Channels) |
| **P** | Saved playlists (Favorite Playlists) |
| **W** | Videos to watch later (Watch List) |

#### Shortcuts in the Favorites window

- **Ctrl+1 to Ctrl+4** — switch between tabs
- **Ctrl+Up/Down** — reorder tabs
- **Ctrl+C / Ctrl+X / Ctrl+V** — copy/cut/paste to move items
  _(Favorite Videos ↔ Watch List can be moved across each other; Channels and Playlists can only be moved within their own list)_
- **F2** — manually rename the selected video/channel/playlist
- **Alt+R or Delete** — remove the selected item
- **Alt+N** — add a new item from a URL in the clipboard
- **Alt+S** — move focus to the search field (results update in real time)
- **Sort... button (Alt+O)** — sort the list:
  - Sort by: Title, Channel, Duration, Date Added, or Upload Date
  - Choose Ascending or Descending
  - If "Apply permanently" is checked, the order is saved; otherwise it resets when you search or refresh
  - Press "Clear Sort" to restore the original order

#### Channel tab (Favorites)

This tab offers more than a simple list — it also includes:
- **Channel description text area** — shows the channel's bio/about text
- **Open channel in browser button**
- **Buttons to browse Videos / Shorts / Live** content from that channel directly

#### Playlist tab (Favorites)

- Press **Space, Enter, or Alt+V** — expand all videos in the playlist
- **Open on Web button (Alt+W)** — opens the playlist in the browser

---

### s: Subscription Feed

A window displaying videos from channels you follow through the add-on. This is **separate** from your YouTube account subscriptions — no login required.

The default view has 4 tabs by content type:

| Tab | Content |
|-----|---------|
| **All** | All content types combined |
| **Video** | Regular videos only |
| **Shorts** | Short-form videos only |
| **Live** | Live streams and live replays |

You can also create **custom categories** and configure which channels appear in each.

#### Shortcuts in Subscription Feed

- **Ctrl+1 to Ctrl+0** — jump to a category tab (up to 10 tabs)
- **Ctrl+Up/Down** — reorder tabs/categories
- **F2** — rename a category (except the 4 default tabs)
- **Ctrl+= (Equals)** — add a new category
- **Ctrl+- (Minus)** — remove a category (except the 4 default tabs)
- **Delete or Alt+S** — mark a video as seen; it will be removed from the list
- **Ctrl+Delete** — mark all videos in the current tab as seen

#### Buttons in the Subscription Feed window

- **Mark as seen (Alt+S)** — marks the selected video as seen
- **Add new Subscription from clipboard URL (Alt+N)** — subscribes to a channel using the URL in the clipboard
- **Update Feed (Alt+U)** — manually triggers an update from all subscribed channels (the add-on also auto-updates on NVDA startup)
- **More... (Alt+M)** — additional options:
  - Mark all in current tab as seen (Ctrl+Delete)
  - Show all videos (including seen) — toggles between unseen-only and all videos; the setting is saved automatically
  - Manage subscriptions...
  - Add New Category... (Ctrl+=)
  - Rename Current Category... (F2)
  - Remove Current Category... (Ctrl+-)
  - **Clear All Feed Videos...** — removes all videos from the database without removing your subscribed channels; useful when the database grows large and affects NVDA performance

---

### m: Manage Subscriptions

A window showing all channels you are subscribed to, with management options for each:

- **Filter by Category** — filter the channel list by category (default: All)
- **Assign to Categories** — choose which categories this channel's content should appear in
- **Content Types to Fetch** — choose which content types to update for this channel (Videos, Shorts, Live); useful for channels that only publish certain types
- **View Content... (Alt+C)** — browse the channel's content (same as the Action button)
- **Add new subscribe channel from Clipboard... (Alt+N)** — subscribe to a new channel using the URL in the clipboard
- **Unsubscribe from this Channel (Alt+U)** — removes the channel from your subscriptions
- **Save Changes** — ⚠️ **Important:** you must press this before closing the window, or your changes will not be saved

---

### u: User Profile Manager

The add-on supports multiple **User Profiles** on the same machine. Each profile keeps its data completely separate (Favorites, Subscriptions, Watch List).

In this window:
- **F2** — rename the selected profile
- **Delete** — delete the selected profile ⚠️ Deletion is permanent; all data in that profile will be lost

To switch profiles, go to [Settings](#settings) → Active Profile, then restart NVDA.

---

### Video List

The video list is the standard UI used throughout the add-on — in search results, Favorites, Subscription Feed, and channel video browsing.

- Press **Enter** to open the video in the browser
- Press **Space** to perform the Quick Action (configurable in Settings)

#### Action button (Alt+A)

Opens the Action menu for the selected video:

| Menu item | Shortcut |
|-----------|---------|
| View Video Info | i |
| View Comments / Replay | c |
| View Chapters/Timestamps | t |
| Download Video | d |
| Download Audio | a |
| Download Subtitles | b |
| Add to Favorite Videos | f |
| Add to Favorite Channels | f |
| Add to Watch List | w |
| Open video in browser | o |
| Open channel in browser | h |
| Show channel videos | v |
| Show channel shorts | s |
| Show channel live | l |

#### Copy button (Alt+C)

Opens the Copy menu:

| Menu item | Shortcut |
|-----------|---------|
| Copy Title | t |
| Copy Video URL | u |
| Copy Channel Name | c |
| Copy Channel URL | h |
| Copy Summary | s |

---

## Settings

Access via `NVDA → Preferences → Settings...` and select the **"YoutubePlus"** category.

| Setting | Description |
|---------|-------------|
| **Active Profile** | Select the active profile (requires NVDA restart after switching) |
| **Manage Profiles** | Opens the User Profile Manager |
| **Quick Action (Space bar)** | Defines what the Space key does in video list windows; all Action menu options are available |
| **Notification mode** | How the add-on signals background activity: **Beep** (short tones), **Sound** (audio file), **Silent** (no audio, spoken messages still occur) |
| **Default sort order** | Default display order: **Newest First** or **Oldest First** — applies to comments, chat, and channel video lists |
| **Items to fetch** | Number of items retrieved per content type when browsing a channel or updating the feed (default: 20, range: 5–100) |
| **Default content types** | Content types to fetch for newly subscribed channels: Videos, Shorts, Live |
| **Background update interval** | How often the add-on automatically checks for new content from subscribed channels (disabled, or 15 minutes to 24 hours) |
| **Automatically speak incoming live chat** | Reads new live chat messages aloud as they arrive |
| **Live chat refresh interval** | How often (in seconds) the add-on checks for new messages (default: 5 seconds) |
| **Message history limit** | Maximum number of chat messages stored in memory during a session (default: 5,000) |
| **Cookie method (Experimental)** | Select the browser you are logged into on YouTube. The add-on will extract cookies from that browser to authenticate requests, which may help resolve the "Sign in to confirm you're not a bot" error. Note that this feature is experimental and results vary depending on the browser and system configuration. |
| **Default subtitle format** | Subtitle file format for downloads: SRT, VTT, TTML, or TXT (plain text without timecodes) |
| **Default download and export folder path** | Destination folder for downloaded videos, audio, and exported files |
| **Backup data now** | Immediately backs up all data for the active profile (the add-on also performs an automatic daily backup) |
| **Restore data from backup** | Shows available backups (up to the last 5 days) to choose from for restoration |

---

## Additional Information

This add-on relies on two main libraries: [pytchat](https://pypi.org/project/pytchat/) for live chat monitoring, and [yt-dlp](https://pypi.org/project/yt-dlp/) for all other YouTube data access. We extend our sincere thanks to the developers of both libraries.

### About yt-dlp

[yt-dlp](https://github.com/yt-dlp/yt-dlp) is one of the most powerful open-source tools for downloading video and audio from websites worldwide — supporting over 1,000 sites, not just YouTube. It is free, open-source, actively maintained by a global community, and contains no ads or malware unlike many browser-based download tools.

**Usage guidelines to keep in mind:**

1. **Fair Use:** Avoid fetching large amounts of data or sending repeated requests in a short time. YouTube may detect unusual activity and temporarily restrict access from your IP address.
2. **Copyright and Privacy:** Any data or content retrieved should be for personal viewing or analysis only. Please respect each platform's Terms of Service and do not use the data in ways that infringe on copyright.
3. **Responsibility:** You are responsible for how you use this software. The add-on developer provides only the interface for accessing YouTube data through the yt-dlp library.

> **Tip:** If you need to process large amounts of data, space out your requests to maintain connection stability and avoid access restrictions.
