# YoutubePlus for NVDA

> YoutubePlus is an add-on for people who love using YouTube but find many features on the website difficult to access — such as reading video comments.
> We bring these features to you through NVDA's user interface in a form that is easy to navigate, supports keyboard shortcuts, and is fully customizable — without requiring you to deal with API keys or connect any personal accounts to the add-on.
> You can follow your favorite channels and be confident that you will see every video from those channels, without YouTube's algorithm filtering them out.
> We also provide a Favorites system for videos, channels, playlists, and a watch list to save content you're interested in but haven't had time to watch yet.
> There is a built-in video search that displays results within the same user interface used throughout the add-on — not just a search box that opens YouTube in a browser.
> A download feature is included for saving videos or audio files, though it is provided as a convenience rather than a primary focus. If downloading is your main need, there are other add-ons dedicated to this feature that you may want to explore.
> The one thing this add-on does not do is embed a video player. We believe the YouTube web player is already accessible enough on its own. If you find it still lacking, you can use other add-ons such as [browserNav](https://addonstore.nvaccess.org/?channel=stable&language=en&apiVersion=2025.3.2&addonId=browsernav) to improve the experience.

## Keyboard Shortcuts and Commands

This add-on uses a layered shortcut system to avoid conflicts with other add-ons or NVDA commands.
Press **NVDA+Y** to enter YoutubePlus command mode, then press one of the following keys to access each feature or window.

**Note:** If the main shortcut (`NVDA+Y`) conflicts with another add-on, you can change it via `NVDA -> Preferences -> Input Gestures...` under the "YoutubePlus" category.

### Keys available in the YoutubePlus layer

* a: (add to...) — Opens a submenu letting you choose where to add the current video or channel
* f: (open favorites video) — Opens the favorite videos window
* c: (open favorites channel) — Opens the favorite channels window
* p: (open favorites playlist) — Opens the favorite playlists window
* w: (show watch list) — Opens the watch list window
* d: (download) — Prompts you to confirm whether to download as video or audio only
* e: (search) — Opens the video search window
* q: (quick search) — Searches YouTube immediately using the currently selected text, or the clipboard content if nothing is selected — without opening the search dialog first
* control+h: (search history) — Opens the Favorites window directly on the Search History tab
* i: (info) — Opens the video details window
* t: (show timestamp) — Displays timestamps or chapters if available
* m: (open manage subscription) — Opens the subscription management window
* s: (open subscription feed) — Shows videos from channels you follow
* u: (open User Profile Manager) — Opens the User Profile management window
* l: (show comment) — Displays comments (details explained below)
* shift+l: (stop monitor live chat) — Stops live chat monitoring
* r: (toggle automatic reading live chat) — Toggles automatic speech for incoming live chat messages
* v: (show live chat) — Reopens the live chat window if you closed it while the stream is still active
* y: (open YoutubePlus settings dialog) quick open NVDA settings then focus at YoutubePlus category.
* h: (help) — Opens a window listing all available shortcuts

**Note:** For commands that act on a video directly, the add-on first checks the browser window you have open. If a YouTube video page is active, it uses that video's URL. If no video page is open, it checks the clipboard for a YouTube URL.

## Feature Details and Commands

### a: (add to...)

This command in the YoutubePlus layer sends video or channel information to the selected destination:

* Add to Favorite Videos  (v)
* Add to Favorite Channels  (c)
* Add to Favorite Playlist  (p)
* Subscribe to Channel  (s)
* Add to Watch List  (w)

The add-on checks the currently open browser page first. If it is a YouTube video page, it extracts the URL and processes it according to your selection. If the page is not a YouTube video or no browser is open, it checks the clipboard for a YouTube URL.

Most commands work with any type of YouTube URL, since the add-on can derive the needed information. For example, if you are on a video page and choose "Add to Favorite Channels," the add-on can extract the channel URL automatically. The same applies to subscribing to a channel.

The only exception is playlists — you must have a YouTube playlist page open, or have a valid YouTube playlist URL copied to the clipboard.

### d: (download video/audio)

This command opens a small dialog asking whether you want to download the video as an MP4 file or audio only as M4A. You can set the download destination in the [Settings](#settings) section.

Note that the download feature is provided for convenience and may have limitations if used heavily. If you need to download large amounts of YouTube content, other dedicated tools are recommended.

### e: (search)

This command opens a YouTube search window. Type your query in the search field and press Enter to search immediately. You can also Tab to adjust the number of results to display — the add-on remembers this value for future searches.

The search field is a combo box that remembers your past searches: press the Down arrow (or Alt+Down) to drop down a list of previous keywords and pick one instead of retyping it.

Results are displayed in the same [video list](#video-list) format used throughout the add-on, not as a YouTube web page. You can access all video details the same way as any other video list in the add-on.

#### q: (quick search)

A faster alternative to the search dialog above. Select some text in any application (or have a query copied to the clipboard if nothing is selected), then press Q in the YoutubePlus layer. The add-on searches YouTube immediately using that text and the saved result count from your last search — no dialog, no extra key presses.

#### Search History

Every search you run — from either the search dialog or quick search — is saved automatically. Press **Control+H** in the YoutubePlus layer to jump straight to the Search History tab in the Favorites window, where you can:

* Press Enter, or the **Search Again** button, to re-run a past search
* Press **New Search (Alt+N)** to open the search dialog
* Press Delete, or the **Remove** button, to remove a single entry
* Press the **Clear All** button to clear the entire history

### i: (video info)

Displays the following details for the current video:

* Title
* Channel
* Duration
* Uploaded
* Views
* Likes
* Comments
* Description

### t: (timestamp / chapter)

Displays the timestamp or chapter list for the video (if the creator included this information). If the add-on reports "No chapters found in this video," the video simply does not have chapter data.

This window offers more convenience than reading chapters from the browser:

* A search field to filter the timestamp/chapter list — results update instantly without pressing Enter
* The full list displayed with each section's description first, followed by its time position
* A read-only text area for reading long chapter descriptions
* An "Open Chapter" button — or press Space or Enter — to jump directly to that chapter in the video
* Copy Title button (Alt+C) to copy the chapter name
* Copy URL button (Alt+U) to copy the URL with the timestamp for that chapter
* Export button (Alt+E) to save all timestamp/chapter data as a text file

### Favorites

A window displaying your saved favorites, divided into 5 tabs by type:

* **Video:** Lists your saved videos, organized into categories of your own making. A category tree sits on the left and the video list for the selected category sits on the right (see [Categories](#categories-video--watch-list-tabs) below). Includes Action and Copy buttons for each item (described below).
* **Channel:** Lists your saved channels with a channel description panel. Includes buttons to open the channel and browse its content by type.
* **Playlist:** Lists your saved playlists. Press Space, Enter, or Alt+V to expand all videos in a playlist. Includes an Open on Web button (Alt+W) to open the playlist in a browser.
* **Watch List:** Lists your saved videos using the same category tree + list layout as the Video tab, with its own independent set of categories.
* **Search History:** Lists every search you've run, with options to re-run, remove, or clear entries (see [Search History](#search-history) above).

#### Favorites window commands

* Press Control+1 through Control+5 to switch between tabs
* Press Control+Up/Down to reorder tabs
* Press Control+C (copy), Control+X (cut), or Control+V (paste) to reorder items
    * Favorite Videos and Watch List support copying and moving items between each other, including items inside a category. The Video and Watch List tabs each keep their own separate category list, so when an item moves between them it's placed into whichever category is currently selected in the destination tab. Favorites Channels and Playlists only support moving items within their own list.
* Press Alt+R or Delete to remove an item
* Press Alt+N to add a new item from the clipboard — for channel and playlist tabs, the URL must match the tab type
* Press **Alt+O (Sort...)** to open the sort dialog for the current tab — see [Sorting](#sorting) below
* The search field filters results instantly as you type — no need to press Enter

#### Categories (Video & Watch List tabs)

Both the Video and Watch List tabs let you organize items into categories of your own, using a tree view on the left, separate from the item list on the right. Each tab keeps its own categories — creating a category in one does not affect the other. There's always a default node for uncategorized items ("Videos" in the Video tab, "Watch List" in the Watch List tab).

With focus on the category tree:

* Press **Control+=** to add a new category
* Press **F2** to rename the selected category
* Press **Delete** to remove the selected category — if it still contains items, you'll be asked whether to move them to the default node or delete them along with the category
* Press **Control+Shift+Up** / **Control+Shift+Down** to reorder the selected category
* Press Enter, or Tab, to move focus to the item list for that category
* Right-click, or press the Application/Menu key, for a context menu — its contents depend on what's selected: a category node shows category management options (Add/Rename/Delete/Move), while the default node only shows Add Category

With focus on the item list (right side), right-click or press the Application/Menu key for the same Action menu used throughout the add-on (View Info, Comments, Download, Add to..., etc.) — separate from the category context menu on the tree.

Cut, Copy, and Paste on the item list work as described above, and pasting always places items into whichever category is currently selected in the tree.

#### Sorting

The **Sort... (Alt+O)** button is available on any tab with a sortable list — including Video, Watch List, and Search History. It opens a dialog with:

* **Sort by:** the field to sort on (Title, Channel, Duration, Upload Date, Date Added — fields vary slightly by tab)
* **Ascending / Descending**
* **Sort only the current category:** when checked, sorting only reorders items inside the category currently selected in the tree, leaving every other category untouched. Unchecked by default, meaning the sort applies across all categories at once.
* **Apply permanently (saves to file):** when checked, the new order is written to disk immediately. When unchecked, the sort is temporary — it changes what you see right now but reverts the next time the list reloads or you search.
* **Clear Sort:** discards any temporary sort and restores the saved order from disk.

#### Video list

In the video and watch list tabs, as well as any other view that shows a video list, you will find the **Action...** and **Copy...** buttons. These are standard controls across all video list views, with the subscription feed adding an extra "Unsubscribe from this channel" option.

Press Enter on any item to open the video in your browser. or press space bar to perform quickAction that you can set it from [settings](#settings)

##### Action button

Press Alt+A to open the Action menu, which includes:

* View Video Info...  (i)
* View Comments / Replay...  (c)
* View Chapters/Timestamps...  (t)
* Download Video  (d)
* Download Audio  (a)
* Add to Favorite Videos  (f)
* Add to Favorite Channels  (f)
* Add to Watch List  (w)
* Open video in browser  (b)
* Open channel in browser  (h)
* Show channel videos  (v)
* Show channel shorts  (s)
* Show channel live  (l)
* Show channel playlist  (l)
* Show channel podcast  (p)

##### Copy button

Press Alt+C to open the Copy menu, which includes:

* Copy Title  (t)
* Copy Video URL  (u)
* Copy Channel Name  (c)
* Copy Channel URL  (h)
* Copy Summary  (s)

### Subscription feed

A window displaying videos from channels you follow within the add-on. This is separate from your YouTube account subscriptions — no account linking or personal data is required.

Unlike the Favorites window, this view uses standard tabs divided by content type:

* **All:** All content types combined
* **Video:** Regular videos only
* **Shorts:** Short-form videos only
* **Live:** Live streams and live stream replays

Beyond these default categories, you can create custom categories and configure which channels appear in each.

#### Subscription feed commands

* Press Control+1 through Control+0 to jump to a category tab (up to 10 categories)
* Press Control+Up/Down to reorder categories, same as in the Favorites window
* Press F2 to rename a category (except the 4 default categories)
* Press Control+= to add a new category
* Press Control+- to remove a category (except the 4 default categories)
* Access each video's Action and Copy buttons, or press Enter to open it in a browser
* Press Delete or Alt+S to mark a video as seen — it will be removed from the list
* Press Control+Delete to mark all videos in the current tab as seen

Additional buttons in this window:

* **Mark as seen (Alt+S)** — removes the video from the list; Delete key also works
* **Add new Subscription from clipboard URL (Alt+N)** — subscribes to a channel using the URL copied to the clipboard
* **Update Feed (Alt+U)** — manually triggers an update for all subscribed channels; the add-on also auto-updates on NVDA startup by default
* **More... (Alt+M)** — opens a submenu with additional options:
    * Mark all in current tab as seen (Ctrl+Delete)  (a)
    * Show all videos (including seen)  (v) — toggles between unseen-only and all videos; the setting is saved automatically
    * Manage subscriptions...  (m)
    * Add New Category...  Ctrl+=  (c)
    * Rename Current Category...  F2  (r)
    * Remove Current Category...  Ctrl+-
    * Clear All Feed Videos... — removes all videos from the database without removing your subscriptions; useful if the database grows large and affects NVDA performance

### Manage subscription

This window shows all channels you are subscribed to. The first section is the channel list, followed by management options for each channel:

* **Filter by Category** — filter the channel list by category; defaults to "All"
* **Assign to Categories** — choose which categories this channel's content should appear in
* **Content Types to Fetch** — choose which content types to update for this channel (Videos, Shorts, Live); useful for channels that only publish certain types
* **View Content... (Alt+C)** — browse the channel's content, same as the Action button
* **Add new subscribe channel from Clipboard... (Alt+N)** — subscribe to a new channel using the URL in the clipboard
* **Unsubscribe from this Channel (Alt+U)** — removes the channel from your subscriptions
* **Save Changes** — **important:** you must press this before closing the window, or your changes will not be saved

### User Profile Manager

This window manages your user profiles. The add-on comes with a "default" profile. You can add, delete, or rename profiles here. To switch between profiles, go to the add-on's Settings panel.

In this window:

* Press F2 to rename the selected profile
* Press Delete to remove the selected profile

**Note:** Deleting a profile permanently deletes all data associated with it. Any saved videos, channels, or subscriptions in that profile will be lost.

### l: (show comments)

There are three types of comments on YouTube videos:

* **Comment** — standard viewer comments on regular videos
* **Live chat** — messages sent during a live stream
* **Live chat replay** — the recorded live chat for a previously streamed video, if the channel owner has not removed it

YoutubePlus supports access to all three types through this command.

#### Live chat of...

For currently live videos, press L and the add-on will open a new window displaying incoming chat messages. Only messages received after you activate the command are shown — earlier messages are not captured.

You can close this window and reopen it later with the V command in the YoutubePlus layer, as long as the stream is still active and NVDA has not been restarted.

Use the R command to toggle whether NVDA reads new messages aloud as they arrive. This works well for streams with infrequent messages. For high-volume streams, it may be easier to turn auto-read off and scroll through the window manually.

Press Shift+L to stop monitoring chat for the current video.

Three settings directly affect this feature:

- **Automatically speak incoming live chat:** When checked, NVDA reads new messages aloud immediately — the same function as the R command, but saved as a default preference.
- **Live chat refresh interval:** How often (in seconds) the add-on checks for new messages. Default is 5 seconds.
- **Message history limit:** The maximum number of messages stored in memory during a session. The live chat window shows only the most recent messages up to this limit (default: 5,000). The add-on keeps all messages in the background for export, up to a maximum of 200,000 to prevent excessive memory use.

When a stream ends — or the add-on detects that it has ended — a dialog will automatically appear asking whether you want to export all collected messages. Press Yes to save the chat history as a file.

#### Comments / Live chat replay

For regular uploaded videos or archived streams, you can access comments the same way. If both live chat replay and standard comments are available, a dialog will ask which you want to load.

There is no limit on the number of comments displayed, though loading may take time for videos with many comments.

Comments are displayed with pinned comments first, followed by all others in the sort order configured in Settings (newest first or oldest first).

#### Comment window sections

* **Search field** — type to filter comments; results update instantly
* **Filter combo box** — select a filter option (the add-on fills the search field automatically):
    * No Filter — default; shows all comments
    * Filter by Selected Author — shows only comments from the selected commenter
    * Show Super Chats Only
    * Show Super Stickers Only
    * Show Super Thanks Only
* **Comment list** — shows commenter name followed by their message
* **Read-only text area** — scroll through the full text of the selected comment, useful when a comment is too long to display in full in the list
* **Copy button (Alt+C or Ctrl+C)** — copies the selected comment
* **Export button (Alt+E)** — saves all comments as a text file to the folder set in Settings
* **Total paid amount field** — shown only for live chat replays; displays the total donations from viewers during the stream

## Settings

Access settings via `NVDA -> Preferences -> Settings...` and select the **"YoutubePlus"** category.

- **Active Profile:** Select the profile to use. A restart is required after switching profiles.
- **Manage Profile button:** Opens the User Profile Manager window.
- **Quick Action (Space bar):** Choose what the Space key does in video list windows. All options from the Action menu are available.
- **Notification mode:** Choose how the add-on signals background activity:
  - *Beep:* Short beep tones
  - *Sound:* Audio effect
  - *Silent:* No audio notification (spoken responses still occur)
- **Default sort order:** Choose whether lists (comments, channel videos) are sorted **Newest First** or **Oldest First**.
- **Items to fetch:** How many items to retrieve per content type when browsing a channel, and for subscription feed updates. Default: 20.
- **Default content types:** Choose which content types to fetch for newly subscribed channels: Videos, Shorts, and/or Live.
- **Background update interval:** How often the add-on checks for new content from subscribed channels. Can be disabled or set from 15 minutes to 24 hours. The add-on also auto-updates on every NVDA startup by default.
- **Automatically speak incoming live chat:** When checked, NVDA reads new chat messages aloud as they arrive.
- **Live chat refresh interval:** How often (in seconds) the add-on checks for new messages. Default: 5 seconds.
- **Message history limit:** Maximum number of chat messages stored in memory during a session.
- **Default subtitle format:** Subtitle file format for downloads: SRT, VTT, TTML, or TXT (plain text without timecodes)
- **Cookie method (Experimental):** Select the browser you are logged into on YouTube. The add-on will extract cookies from that browser to authenticate requests, which may help resolve the "Sign in to confirm you're not a bot" error. Note that this feature is experimental and results vary depending on the browser and system configuration.
- **Default download and export folder path:** The destination folder for downloaded videos/audio and exported chat.
- **Backup data now:** Manually backs up all data for the active profile. The add-on also performs an automatic daily backup in the background.
- **Restore data from backup:** Shows a list of available backups (up to the last 5 days) so you can choose which date to restore from.

## Additional Information

This add-on relies on two main libraries: [pytchat](https://pypi.org/project/pytchat/) for live chat monitoring, and [yt-dlp](https://pypi.org/project/yt-dlp/) for all other YouTube data access. We extend our sincere thanks to the developers of both libraries.

### About yt-dlp

[yt-dlp](https://github.com/yt-dlp/yt-dlp) is one of the most powerful open-source tools for downloading video and audio from websites around the world — supporting over 1,000 sites, not just YouTube. It is free, open-source, and actively maintained by a global community, with no ads or malware unlike many browser-based download tools.

That said, please keep the following usage guidelines in mind:

1. **Fair Use:** Avoid fetching large amounts of data or sending repeated requests in a short time. YouTube may detect unusual activity and temporarily restrict access from your IP address.
2. **Copyright and Privacy:** Any data or content retrieved should be for personal viewing or analysis only. Please respect each platform's Terms of Service and do not use the data in ways that infringe on copyright.
3. **Responsibility:** You are responsible for how you use this software. The add-on developer provides only the interface for accessing YouTube data through the yt-dlp library.

**Tip:** If you need to process large amounts of data, space out your requests to maintain connection stability and avoid access restrictions.