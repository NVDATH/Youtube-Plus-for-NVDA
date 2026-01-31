# YoutubePlus for NVDA

> YoutubePlus is an add-on for those who enjoy YouTube but find many web features difficult to access, such as reading video comments.
> We bring these features to you through the NVDA user interface in an accessible, shortcut-driven, and customizable format. Users do not need to deal with API keys or link any personal data to the add-on.
> You can follow your favorite channels and be certain that you will see every video they post without being filtered out by YouTube's algorithm.
> Additionally, we offer a Favorites system for videos, channels, playlists, and a "Watch List" for saving videos you're interested in but don't have time to watch yet.
> There is a built-in search system that displays results within the same accessible UI as other features, rather than just providing a search box that opens the web results.
> A download feature is included for saving videos or audio files, though it is a secondary feature. If your primary goal is downloading, there are other add-ons specifically designed for that purpose.
> The only thing this add-on does **not** do is play the video within its own interface. We believe the YouTube web player is already quite accessible. If you still find it difficult, you can use features from other add-ons like [browserNav](https://addonstore.nvaccess.org/?channel=stable&language=en&apiVersion=2025.3.2&addonId=browsernav) to enhance your experience.

---

## Shortcuts and Sub-commands

This add-on uses a **Layered Shortcut System** to prevent shortcut conflicts with other add-ons or NVDA's core commands.
First, press **NVDA+y** to enter the YoutubePlus command mode.
Then, press the following letters to access specific features or windows:

**Note:** If the main shortcut (**NVDA+Y**) conflicts with another add-on, you can change it via the NVDA menu: `Preferences -> Input Gestures...` under the "YoutubePlus" category.

### Shortcuts used in the YoutubePlus layer

* **a**: (Add to...) - Opens a sub-menu to choose which list to add the video/channel to.
* **f**: (Open favorite videos) - Opens your favorite videos window.
* **c**: (Open favorite channels) - Opens your favorite channels window.
* **p**: (Open favorite playlists) - Opens your favorite playlists window.
* **w**: (Show watch list) - Displays the Watch List window.
* **d**: (Download) - Prompts to download the video/audio.
* **e**: (Search) - Opens the search window.
* **i**: (Info) - Opens the video details window.
* **t**: (Show timestamp) - Displays timestamps or chapters if available.
* **m**: (Open manage subscriptions) - Opens the subscription management window.
* **s**: (Open subscription feed) - Displays a feed of videos from your subscribed channels.
* **l**: (Show comments) - Displays comments (details explained below).
* **Shift+l**: (Stop monitoring live chat) - Stops live chat detection.
* **r**: (Toggle automatic reading live chat) - Toggles whether NVDA reads new live chat messages automatically.
* **v**: (Show live chat) - Re-opens the live chat window if it was previously closed.
* **h**: (Help) - Opens a window listing all shortcuts.

**Note**: For commands targeting a specific video, the add-on first checks your active browser window. If no YouTube video is open, it checks your clipboard for a YouTube URL.

---

## Feature Details

### a: (Add to...)

This command sends video or channel data to your selected list:

* Add to Favorite Videos (v)
* Add to Favorite Channels (c)
* Add to Favorite Playlists (p)
* Subscribe to Channel (s)
* Add to Watch List (w)

Most commands work with any YouTube URL. For example, if you are on a video page but select "Add to Favorite Channel," the add-on will automatically extract the channel URL. However, "Add to Playlist" requires you to be on a playlist page or have a playlist URL in your clipboard.

### d: (Download video/audio)

Prompts you to save the content as a video (.mp4) or audio (.m4a). You can set the save location in the [Settings](#settings).
*Warning: This feature is for occasional use. If you need to download a large number of videos, please use dedicated software.*

### e: (Search)

Opens a search window. Enter your keywords and press Enter. You can tab to adjust the number of search results. The results are displayed in a [Video List](#video-lists) format within the add-on interface.

### i: (Video Info)

Displays the following details:

* Title, Channel, Duration, Upload Date, Views, Likes, Comments, and Description.

### t: (Timestamp / Chapters)

Displays chapters or timestamps. If the video has none, you will see "No chapters found in this video."

* **Search box**: Filter chapters instantly.
* **Open Chapter**: Press Space or Enter to open the video at that specific time in your browser.
* **Copy title/URL**: Copy the chapter name (Alt+c) or the URL with a timestamp (Alt+u).
* **Export**: Save all timestamps to a text file (Alt+e).

---

### Favorites

A window with four tabs:

* **Video**: Displays your favorite videos with action and copy buttons.
* **Channel**: Lists channels with descriptions and options to view specific content types (Videos, Shorts, Live).
* **Playlist**: Lists saved playlists. Press Space/Enter to expand the playlist videos or Alt+w to open on the web.
* **Watch List**: Functions exactly like the Video tab.

#### Managing Favorites

* **Ctrl+1-4**: Switch between tabs.
* **Ctrl+Up/Down**: Reorder tabs.
* **Shift+Up/Down**: Reorder items within a tab.
* **Alt+r / Delete**: Remove an item.
* **Alt+n**: Add a new item from a clipboard URL.
* **Search**: Filter items in real-time.

---

### Video Lists

Found in Favorites, Watch List, and Search results. Every video entry has **Action** and **Copy** buttons.

#### Action Button (Alt+a)

* View Video Info (i)
* View Comments / Replay (c)
* View Chapters/Timestamps (t)
* Download Video/Audio (d/a)
* Add to favorites video (f)
* Add to favorites channel (f)
* Add to watch list (w)
* Open in browser (b)
* Show channel content (v/s/l)

#### Copy Button (Alt+c)

* Copy Title (t), Video URL (u), Channel Name (c), Channel URL (h), or Summary (s).

---

### Subscription Feed

Displays videos from channels you follow **within this add-on**. This is independent of your actual YouTube account.

* **Categories**: Default categories include All, Video, Shorts, and Live.
* **Customization**: You can create your own categories and assign channels to them.
* **Shortcuts**:
* **Ctrl+1-0**: Jump to the first 10 categories.
* **F2**: Rename category.
* **Ctrl+= / Ctrl+-**: Add or Delete categories.
* **Delete / Alt+s**: Mark as Seen (hides the video).
* **Alt+u**: Update Feed. by default The script will automatically update the feed every time NVDA started.
* **Alt+m (More)**: Access "Mark all as seen," "Show seen videos," and "Clear all feed data."



---

### Manage Subscriptions

A dedicated window to manage your followed channels.

* **Filter by Category**: View channels in specific groups.
* **Assign to Categories**: Select which category a channel belongs to.
* **Content Types**: Choose what to fetch (Videos, Shorts, Live).
* **Save Change**: **Important!** You must click this button to save your modifications before closing the window.

---

### l: (Showing Comments)

Supports three types of feedback:

1. **Comments**: Standard video comments.
2. **Live Chat**: Real-time chat during a live stream.
3. **Live Chat Replay**: Chat history for past live streams.

#### Live Chat

* The add-on monitors chat **only after you start it**.
* **r**: Toggles automatic reading of new messages.
* **Message Limit**: Displays the last 5,000 messages to save memory, but can keep up to 200,000 in the background for export.
* When a stream ends, the add-on will ask if you want to export the chat history.

#### Comments / Replay

Displays standard comments or replay chat. For large comment sections, it may take a moment to load. Pinned comments appear first.

* **Filters**: Filter by specific user, Super Chats, Super Stickers, or Super Thanks.
* **Export**: Save all comments to a text file (Alt+e).

---

## Settings

Access via `NVDA menu -> Preferences -> Settings -> YoutubePlus`:

* **Notification mode**: Beep, Sound, or Silent.
* **Sort order**: Newest First or Oldest First.
* **Items to fetch**: How many videos/comments to load per request (Default: 20).
* **Background update**: How often to check for new videos (Disabled to 24 hours). by default The script will automatically update the feed every time NVDA started.
* **Chat settings**: Auto-speak, refresh interval, and history limits.
* **Paths**: Default folder for downloads and exported text files.
* **Clear Data**: Wipe all favorites and subscriptions.

---

## Additional Information

This add-on utilizes:

* [pytchat](https://pypi.org/project/pytchat/): For live chat monitoring.
* [yt-dlp](https://pypi.org/project/yt-dlp/): For accessing YouTube metadata and downloading.

### Note on yt-dlp and Fair Use

**yt-dlp** is a powerful open-source tool. Please follow these guidelines:

1. **Fair Use**: Avoid making excessive requests in a short time to prevent your IP from being temporarily blocked by YouTube.
2. **Copyright**: Content should be for personal viewing or analysis. Respect the Terms of Service of the platform.
3. **Responsibility**: The user is responsible for the data they fetch. The add-on developer only provides the interface.
