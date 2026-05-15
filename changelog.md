## 2026.5.15

### New Features

* **Rename:** Added the ability to rename items in the Favorites dialog for better personal organization.
* **Sort in Favorites:** Added sort feature in all four Favorites tabs (Videos, Watch List, Channels, Playlists).
  * Supports temporary and permanent modes, with ascending/descending order.
  * Sort fields for Videos and Watch List: Title, Channel, Duration, Date Added, Upload Date.
  * Sort fields for Channels: Channel Name, Subscribers.
  * Sort fields for Playlists: Title, Channel, Video Count.
* **Upload Date column:** Added Upload Date display in Favorites Videos and Watch List.
* **Plain text subtitle export:** Added TXT format option for subtitle downloads — exports subtitle content as plain text without timecodes or formatting tags.

### Improvements

* **Dual-Architecture Support:** Added full compatibility for both NVDA 2025.x (32-bit/Python 3.11) and NVDA 2026.1+ (64-bit/Python 3.13). Libraries are now organized in separate `x64` and `x86` subfolders and loaded automatically based on the running NVDA version. For NVDA 2026.1+, the add-on also registers the library directory using `os.add_dll_directory` to ensure native DLL resolution works correctly under 64-bit Python.
* **Cookie extraction :** Improved cookie handling for the experimental Cook ie method — `cookies_from_browser` 
* **Cancelled download cleanup:** Leftover `.part` files from cancelled downloads are now automatically removed from the download folder.

### Bug Fixes

* Fixed subscription feed not restoring focus position after a background update.
* Fixed focus not restoring correctly in other Favorites tabs after marking a video as seen.
* Fixed duplicate success sound when displaying comments or live chat replay.
* Fixed Add to Watch List quick action not working due to a typo.
* Fixed Watch List items missing the `channel_url` field.

---

## 2026.3.19

### New Features

* Added subtitle download feature accessible from the Action menu, quick action, and YoutubePlus layer.
* Subtitle language selection dialog shows only languages that can actually be downloaded.
* Added subtitle format setting (SRT, VTT, TTML) in Settings.
* Added shortcut to open YoutubePlus settings directly from the YoutubePlus layer (NVDA+Y → Y).

### Dependencies

* Updated yt-dlp to v2026.3.19

## 2026.3.17

### New Features

* Added cut/copy/paste support in Favorites Videos and Watch List (Ctrl+X/C/V), including cross-list support between the two panels.
* Added cut/paste support in Favorites Channels and Favorites Playlists for reordering items within each list.
* Multi-select support in all four Favorites panels using Shift+Arrow.
* Search text is now preserved per tab when switching between tabs in the Favorites dialog.
* Added manual backup button in Settings to back up the active profile on demand.
* Added automatic daily backup triggered by the background subscription update worker.
* Added restore from backup in Settings with a submenu listing up to the last 5 backups by date.
* Backup files are stored in a dedicated folder and auto-rotated to keep only the 5 most recent.
* Added Ukrainian (uk) translation by Георгій Галас.

### Bug Fixes

* Fixed NVDA reading list items twice when opening the Favorites dialog or switching tabs.
* Fixed focus not returning to the correct position after clearing the search field in Favorites.
* Fixed Watch List not focusing the newly added item after adding.
* Fixed Add button using the wrong worker for Watch List.
* Fixed Live Chat Messages dialog showing the wrong video title after viewing other content.
* Fixed Live Chat search causing IndexError when the selected item is outside the filtered results range.
* Fixed Live Chat search not restoring the correct scroll position after clearing the search field.
* Fixed profile list in Settings incorrectly including the backups folder as a selectable profile.

### Dependencies

* Updated yt-dlp to v2026.3.13

## 2026.3.3

* **Core Engine Update:** Upgraded internal **yt-dlp to v2026.3.3** for enhanced video extraction performance and stability.

## 2026.2.28

### ✨ New Features

* **User Profiles:** Introduced a dedicated user profile system, allowing users to customize and save their preferences for a more personalized experience.
* **Quick Actions:** Added a new quick access menu to trigger frequently used functions instantly.
* **Full I18n Support:** Refactored the entire codebase to support Internationalization (I18n), enabling seamless translation via Gettext and supporting translator notes.

### 🛠️ Improvements & Fixes

* **Core Engine Update:** Upgraded internal **yt-dlp to v2026.2.21** for enhanced video extraction performance and stability.
* **Dependency Resolution:** Fixed critical internal import errors; the add-on is now fully self-contained and functions correctly without relying on other installed add-ons.
* **General Bug Fixes:** Resolved multiple bugs across various modules, including video list rendering. All features are now expected to be fully operational and stable.

## 2026.2.4

* update yt-dlp to latest 2026.2.4
* Removed potentially confusing commands from the input gesture settings.

## 2026.2.1

* update yt-dlp to latest 2026.1.31
* update some description format
* fix lost library

## 2026.1.31

* remove unuseful extractors from yt-dlp

## 2026.1.29

* update YT-DLP lib to latest version
* rewrite a read me file
* add new favorites category "watch list"
* remove cookies method

## 2025.12.12

* update YT-DLP to latest
* correct cookies mode

## 2025.9.26

* update yt-dlp to 2025.9.26
* clean up code for official release

## 2025.9.23

* update yt-dlp to 2025.9.23

## 2025.8.22

* initial release
