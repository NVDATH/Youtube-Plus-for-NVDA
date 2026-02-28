# YouTube Plus for NVDA

> YoutubePlus is an extension for those who enjoy using YouTube but find
> some features on the website inconvenient to access, such as reading
> video comments. We bring various features to you through an
> easy-to-use, customizable NVDA user interface with keyboard shortcuts.
> Users don\'t need to worry about finding API keys or connecting any
> personal data to the extension. You can follow your favorite channels
> and be assured of seeing all their videos without being rejected by
> YouTube algorithms. We also have a Favorites system for videos,
> channels, playlists, and watchlists to save interesting videos you
> haven\'t had time to watch yet. The video search function displays
> results in the same user interface as other extensions, not just a
> field to enter search terms and view results on the website. A
> download feature is available, but it just for functionality and
> not our primary focus. If downloading is your main priority, there are
> other extensions that offer this feature. The only thing this
> extension doesn\'t do is integrate a built-in video player, as we
> believe the website video player is already well-designed. However,
> if you still find this inconvenient, you can use features from other
> extensions like
> [browserNav](https://addonstore.nvaccess.org/?channel=stable&language=en&apiVersion=2025.3.2&addonId=browsernav)
> to improve usability.

## Keyboard shortcuts and subcommands

This add-on uses a layered keyboard shortcut system to prevent shortcuts
from overlapping with other add-ons or NVDA commands. You need to press
**NVDA+y** to enter YouTubePlus command mode, and then press the
following letter-based sub-commands to access each feature or window.

**Note:** If the primary shortcut ( `NVDA+Y `) is already used by
another extension, you can change it in the
`NVDA menu -> Preferences -> Input Gestures... `under the "YoutubePlus"
section.

### Keyboard shortcuts used in YouTube Plus layer.

-   a: (add to \*\*\*) - This command will bring up a submenu allowing
    you to select which window you want to add the clip to.
-   f: (open favorites video) - Opens your favorite video window.
-   c: (open favorites channel) - Opens your favorite channel window.
-   p: (open favorites playlist) - Opens your favorites playlist.
-   w: (show watch list) - Displays the watch list window.
-   d: (download) - Instructs the add-on to download the clip. A window
    will appear asking for confirmation on whether you want to download
    the video or just the audio file.
-   e: (search) - Opens a window for searching for clips.
-   i: (info) - Opens the clip details window.
-   t: (show timestamp) - Displays the timestamp or chapter number if
    the clip has one.
-   m: (open manage subscription) - Opens the channel management page
    for the channels you subscribe to.
-   s: (open subscription feed) - Displays a list of videos from the
    channels you are subscribed to.
-   u: (open User Profile Manager)  - you can add rename or delete profile.
-   l: (show comment) - Leave a comment (further details will be
    explained below)
-   shift+l: (stop monitor live chat) - Stops monitoring live chat.
-   r: (toggle automatic reading live chat) - Toggle the text-to-speech
    setting for live chat.
-   v: (show live chat) - If you have displayed the live chat and then
    closed the window, you can reopen it and read the messages using
    this command.
-   h: (help) - Opens a window displaying a list of keyboard shortcuts.

**Note** : When using each command that directly manipulates a clip, the
extension will attempt to detect the browser window you have open and
prioritize the clip you are currently viewing. However, if you do not
have a clip open, the extension will check the YouTube URL in the
clipboard next.

## Details of the features and commands used in the YouTube Plus layer.

### a: (add to...)

This command in the YoutubePlus layer sends video or channel information
to the selected window.

-   Add to Favorite Videos v
-   Add to Favorite Channels c
-   Add to Favorite playlist p
-   Subscribe to Channel s
-   Add to Watch list w

The extension first checks the browser page the user is currently
viewing. If it a YouTube video page, it retrieves the video URL and
processes it according to the user selection. However, if the open
page is not a video page or not even a browser window, it checks the
clipboard to see if the YouTube URL has been copied. If it has, it can
proceed accordingly.

Most commands work with all types of YouTube URLs because the extension
can process them. For example, if you\'re on a video page and click
"add to channel," the extension can retrieve the channel URL and
process it. Subscribing to a channel works the same way. The only
exception is playlists; users need to have the playlist page open or
have the correct YouTube playlist URL copied for the extension to add
the URL to the playlist.

### d: (download video/audio)

This command will bring up a sub-window asking whether the user wants to
download the video clip (.mp4) or just the audio file (.m4a). Users can
specify the desired file saving location in the [settings page.
It](#settings)  important to note that our download feature is
available but may have limitations if used excessively. If you need to
download a large number of YouTube clips, it advisable to use other
methods.

### e: (search)

This command will open a window for searching YouTube clips. Users can
enter their search term in the search box and press enter to start the
search immediately, or they can tab to edit the number of search results
to display. Once the user has changed the number of results, the
extension will remember that setting for subsequent searches. The search
results will be displayed as a list of [videos](#video_list) , not
opening the YouTube webpage. Users can access the search results just
like any other video displayed within this extension.

### i: (video info)

This command will display the video details, which are as follows:

-   Title
-   Channel
-   Duration
-   Uploaded
-   Views
-   Likes
-   Comments
-   Description

### t: (timestamp / chapter)

This command will display the timestamp or chapter list of the video (if
the clip owner has provided this information). Therefore, if clicking
this option shows "No chapters found in this video," it means the
video does not contain this information.

The window displaying the timestamp/chapter will be more convenient for
users than reading from a video in a browser.

-   There a search field that can be used to filter
    timestamps/chapters. Simply enter your search term, and the feature
    will filter the results immediately without needing to press enter.
-   Show the complete list, with the description of each period coming
    first, followed by the time position.
-   If you want to read it, the text of that item is set to read-only
    and you can scroll to read it.
-   There an "open chapter" button that you can press to directly
    open the video at that chapter location, or you can press space
    or enter from the menu.
-   There is a copy title button (alt+c) to copy the chapter name
    immediately.
-   There is a "copy URL" button (alt+u) that allows you to directly
    copy the URL specifying the time location to that chapter.
-   There is an export button (alt+e) to save all timestamp/chapter
    information as a text file.

### favorites

This is a window for displaying the user favorites list, divided into
4 tabs by category.

-   Video: Displays a list of videos added by the user. Each video has
    its own action and copy buttons (explained further below).
-   Channel: Displays a list of channels added by the user, with channel
    descriptions next to them, as well as buttons to open and select
    content from each channel according to its type.
-   Playlist: Displays a list of playlists added by the user. Pressing
    space, enter, or alt+v on each item will expand all the videos in
    that playlist. An "open on web" (alt+w) button is also included to
    open the playlist link in a browser.
-   Watch list: Displays a list of videos added by the user. The
    structure and usage are the same as the video tab.

#### Commands and management of the favorites window.

-   Users can press Control + number 1-4 to switch between tabs in this
    window.
-   Users can press the Control+up/down keyboard shortcut to change the
    order of each tab. Pressing the commands from the YoutubePlus layer
    will directly access each tab on this page; the current order has no
    effect.
-   Users can press Shift+Up/Down to rearrange the order of items in
    each tab.
-   Users can press alt+r or the delete key to remove an item.
-   Users can press alt+n to directly add a new item to each tab when
    the YouTube URL is in the clipboard. For channel/playlist tabs,
    users must copy the YouTube URL correctly according to the tab type.
-   In the search box, you can enter the word you want to search for
    without having to press enter. The extension will search immediately
    after you enter the characters.

#### Video list

In the video/watch list and other sections that display the video list
directly, users will find the \`action...\` and \`copy...\` buttons.
These two are standard buttons for pages displaying the video list, and
their function is similar across all pages. Only the subscription page
will have an additional `Unsubscribe from this channel (u)` option to
unsubscribe from that video channel. Users can then press enter
to open the video directly in their browser.

##### action button

When a user is in a list of videos, they can press alt+a to use the
action buttons, which will provide the following options.

-   View Video Info... (i)
-   View Comments / Replay... (c)
-   View Chapters/Timestamps... (t)
-   Download Video (d)
-   Download Audio (a)
-   Add to Favorite Videos (f)
-   Add to Favorite Channels (f)
-   Add to Watch List (w)
-   Open video in browser (b)
-   Open channel in browser (h)
-   Show channel videos (v)
-   Show channel shorts(s)
-   Show channel live (l)

##### copy button

When the user is in the list of videos displayed, they can press alt+c
to use the copy button to copy the following information.

-   Copy Title (t)
-   Copy Video URL (u)
-   Copy Channel Name (c)
-   Copy Channel URL (h)
-   Copy Summary(s)

### subscription feed

This window displays a list of videos from the channels you\'ve
subscribed to. This effect is only specific to this add-on and does not
relate to the actual channels you\'ve subscribed to on YouTube, as we
don\'t link any accounts or request any user information for this
add-on.

This window differs from the favorites window in that it has standard
tabs organized by video category.

-   all: Includes all types of videos.
-   Video: Regular videos only.
-   Shorts: For short videos only.
-   Live: Only includes clips from live broadcasts or recorded
    broadcasts.

In addition to the default main categories, users can add other
categories to freely diversify their viewing experience and can specify
which channels\' clips should belong in which category.

#### Commands and management of the subscription feed window.

-   Users can press Control + number 1-0 to jump to different tabs
    (categories) that have been created. There is a limit of 10
    categories that can be accessed.
-   Users can press Control + Up/Down to change the order of each
    category, just like in the favorites window.
-   Users can press F2 to edit category names (except for the 4
    categories that are the default).
-   Users can press Control + = to add a new category.
-   Users can press Control + - to delete categories (except for the 4
    default categories).
-   Users can access each video individually, just like any other video
    list. Use [the action key](#actionbutton) or [the copy
    key](#copybutton) and press enter to open the video.
-   Users can press delete or alt+s to mark a video as seen. Once
    pressed, the video status will change to "seen" causing it to
    be removed from the list.
-   Users can press Control + Delete (mark all as seen) for all items in
    the list. This will only affect the category the user is currently
    viewing.

In addition to the action and copy buttons, this page will have the
following additional buttons:

-   Mark as seen (Alt+S) - Removes the video from the list, or you can
    press delete.
-   Add new Subscription from clipboard URL (Alt+n) - This is similar to
    the favorites page where users can copy the channel URL and add a
    subscription directly using this button.
-   Update Feed (Alt+u) - This instructs the add-on to check for updates
    on all subscribed channels. This is useful if the add-on isn\'t
    configured to check automatically, or if you want immediate updates.
    The script will automatically update the feed whenever NVDA is open
    by default.
-   The More... button (Alt+m) will bring up an additional sub-menu with
    management options.
    -   Mark all in current tab as seen (control+delete) (a) - This
        displays the commands as buttons in case the user forgets the
        shortcut commands.
    -   Show all videos (including seen) (v) - By default, the
        subscription feed displays only unseen videos. However, if you
        want to see all clips, you can change the display setting using
        this option. To revert back to showing only unseen videos, you
        must edit the setting again in the same location, as we save
        your settings.
    -   Manage subscriptions... (m) - Opens the [manage subscriptions
        window](#manage-subscription) , another location that users can
        access.
    -   Add New Category... Ctrl+= (c) - Used to add a new category. The
        menu will be displayed here. If the user forgets or doesn\'t
        know the shortcut, they can still access this function from
        here.
    -   Rename Current Category... F2 (r) - Used to edit the category
        name. The menu is displayed here, allowing users to access this
        function from here even if they forget or don\'t know the
        shortcut.
    -   Remove Current Category... Ctrl+- - Used to delete a category.
        The menu is displayed here so that if the user forgets or
        doesn\'t know the shortcut, they can still access this function
        from here.
    -   Clear All Feed Videos... - This function clears all videos in
        the database. It will not clear channels you have subscribed to.
        Over time, this extension may cause the database to grow large,
        potentially affecting NVDA overall performance. Once you have
        cleared all the videos you are interested in, you can click
        here.

### Manage subscription

This window displays a list of all channels the user has subscribed to.
The first section is a list of channels, and subsequent sections allow
you to manage each channel individually.

-   Filter by Category - Users can filter the list of channels by
    category. The default setting is "all," which shows all channels.
-   Assign to Categories - This section is used to select which
    categories the item will appear in.
-   Content Types to Fetch - You can edit which types of videos users
    want to be fetched for a channel. The default setting is already in
    [the Settings](#settings) for new subscriptions, but you can edit it
    for specific channels here. For example, you might find that some
    channels don\'t have any live streams, so you don\'t need to check
    the "live" option, and the feed updates will be slightly faster.
-   View Content... (Alt+c) - Users can view the content of each field
    from here, just like they can from [the action
    button.](#actionbutton)
-   Add new subscribe channel from Clipboard... (Alt+n) = Users can also
    add new channels from here. This works like the button on the
    [subscription feed page.](#subscriptionfeed)
-   Unsubscribe from this Channel (Alt+u) - This button is used to
    unsubscribe from that channel. This is another feature users can
    use.
-   Save changes - **This button is important.** If you have modified
    the settings in each field, you must press this button before
    closing the window; otherwise, the changes will not be saved.

### User Profile Manager

This window is for managing user profiles. By default, the add-on comes
with a "default" profile. Users can add, remove, or edit the name from
this window. However, to switch profiles, you need to edit the settings
in the add-on settings page.

In this window, users can...

-   Press F2 to edit the profile name selected in the list.
-   Press delete to remove the selected profile from the list.

**Note**: If a user deletes their profile, they will also delete the
profile database files. All previously saved video data will be lost.

### l: (Showing a comment)

First, we need to understand the types of video comments on YouTube.
Basically, there are three main types:

-   Comment - This refers to the typical opinions we read on a video.
-   Live chat refers to the comments and discussions within a live
    broadcast video.
-   Live chat replay displays the live chat comments from a previous
    live broadcast, provided the channel owner hasn\'t deleted these
    comments.

For the YouTubePlus add-on, we designed it to access all three comment
formats via the \`l\` command.

#### Live chat of ...

For live streams, users can press the \'l\' command, and the extension
will display comments in a new window. This is because the extension
only monitors comments that have already been triggered by the user.
Comments made before the extension activated will not be displayed. The
live chat window can be closed and reopened later if the live stream is
still ongoing (and the user hasn\'t restarted NVDA). In the YouTube Plus
layer, users can toggle whether the extension automatically reads new
comments using the \'r\' command (turning it on or off). For videos with
infrequent comments and where the user is actively listening, keeping it
enabled is convenient. However, for videos with many comments, it might
be harder to keep track, so closing the window and manually scrolling
through them might be more convenient. To stop monitoring comments on a
video, press Shift+L.

On this page, there are three main [settings](#settings) that directly
affect the settings:

-   **Automatically speak incoming live chat:** If this box is checked,
    NVDA will immediately read new incoming chat messages aloud. This is
    the same function as the \`r\` command but can be set as the
    default.
-   **Live chat refresh interval:** The time (in seconds) that the
    program allows to check for new messages (default: 5 seconds). This
    affects how quickly new comments are displayed.
-   **Message history limit:** The maximum number of chat messages that
    can be stored in memory while in use. This means that the live chat
    window of... will only display the last 5,000 comments that have
    been captured. If the live video continues to gain comments, only
    the last 5,000 comments will be displayed. However, behind the
    scenes, the extension will store all comments so that you can export
    them for later reading. But there is still a limit of 200,000
    comments to prevent excessive memory usage.

Once the video live stream ends, or the extension encounters a problem
and recognizes that the live stream has ended, the extension will
automatically display a window asking the user if they want to export
all comments. The user can answer yes to export the live chat for later
reading.

#### Comments / Live Chat Replay

If it a video that was uploaded normally, or a clip from a previous
live stream that the channel owner still keeps, users can also access
the comments. If there a live chat replay and comments, a sub-window
will appear asking to select which parts to display. There no limit
to the number of comments that can be displayed, but if a video has many
comments, the add-on may take some time to retrieve them. When
displaying these comments, the add-on will adjust the display order,
showing pinned comments first, then sorting comments chronologically
according to the user settings ( [newest](#settings) to oldest).

#### Parts of the comment window.

-   Search edit box - Users can enter search terms to filter comments in
    this box.
-   Filter combo box - Users can filter by selecting options. The add-on
    will pull search terms and place them in the search box. The
    available options are:
    -   No Filter - The default setting is to not filter anything.
    -   Filter by Selected Author - Filter by the username of the
        selected comment.
    -   Show Super Chats Only - Display only comments from Super Chats.
    -   Show Super Stickers Only - Show only comments that contain Super
        Stickers.
    -   Show Super Thanks Only - Display only comments that are Super
        Thanks.
-   The comments list will display the username followed by the comment.
-   A read-only field for that item, so users can scroll through it, or
    in cases where comments are so long that the entire item isn\'t
    displayed.
-   The copy button (alt+c or control+c) will copy the comment
    immediately.
-   The export button (alt+e) will save all comments as a text file. The
    save location will be in [the Settings,](#settings) the same location
    as the download location.
-   The read-only total paid amount section will only display live chat
    replays, showing the viewer donations from those clips.

## Settings

Users can access this setting in the
`NVDA menu -> Preferences -> Settings... `and select
**"YoutubePlus."** Details are as follows:

-   **Active Profile:** Select the desired profile. When switching to a
    new profile, NVDA must be restarted for the database of the new
    profile to be used correctly.
    -  **Manage Profile button:** Opens the User Profile Manager dialog.
-   **quickAction (space bar):** This option determines what the user
    wants the space bar to do in the video list window, drawing all the
    options from the Action... button.
-   **Notification mode:** Select the notification style while the
    program is running:
    -   *Beep:* Emits a beeping sound.
    -   *Sound:* Play sound effects.
    -   *Silent:* No notification sound, but still speaks interactive
        messages.
-   **Default sort order:** Choose the initial sorting order for items
    (e.g., comments or channel clips), either **Newest First** or
    **Oldest First.**
-   **Items to fetch:** Specifies the number of items to retrieve each
    time a user views each type of video in the channel, as well as for
    updating the subscription feed. (Default: 20)
-   **Default content types:** Select the type of content to display for
    newly subscribed channels:
    -   *Videos (Regular videos)*
    -   *Shorts (short clip)*
    -   *Live (livestream)*
-   **Background update interval:** Defines the frequency for checking
    new data for the tracked channel. It can be disabled or scheduled
    from 15 minutes to 24 hours. The script will automatically update
    the feed whenever NVDA is enabled by default.
-   **Automatically speak incoming live chat:** If this box is checked,
    NVDA will immediately read incoming chat messages aloud.
-   **Live chat refresh interval:** The time (in seconds) that allows
    the program to check for new messages (default: 5 seconds).
-   **Message history limit:** The maximum number of chat messages that
    can be stored in memory while in use.
-   **Default download and export folder path:** Select the destination
    folder to store downloaded video/audio files and exported chat
    history files.
-   **Clear Data:** This button clears all favorites and tracking data
    from the add-on.

## Additional information

This extension primarily uses the libraries
[pytchat](https://pypi.org/project/pytchat/) for capturing comments in
live chats and [yt-dlp](https://pypi.org/project/yt-dlp/) for accessing
the rest of YouTube data. We would like to express our gratitude to the
developers of these libraries for their contribution.

### More information about yt-dlp.

[yt-dlp](https://github.com/yt-dlp/yt-dlp) is the most powerful
open-source tool for "extracting" or "downloading" videos and audio
from websites worldwide. It can download from almost any website, not
just YouTube, supporting over 1,000 sites. Furthermore, it free and
safe, being an open-source program constantly monitored and updated by
developers globally. This means it free from hidden ads or malware
found on typical video download websites.

However, there are still usage guidelines to follow:

1.  Fair Use: Please avoid retrieving large amounts of data or running
    commands repeatedly in a short period of time, as this may be
    considered abnormal usage by YouTube and could result in access
    being blocked from your IP address.
2.  Privacy and Copyright Policy: The use of metadata or any content
    should be for personal viewing or analysis only. Please respect the
    Terms of Service of each website and do not use the information in a
    way that infringes on copyright.
3.  Responsibility: Users are responsible for accessing data through
    this software themselves. The app developer only provides an
    interface for accessing data via the yt-dlp library.

Recommendation: If you need to analyze large datasets, it is recommended
to space out the work between sessions to maintain connection stability
and prevent access restrictions.
