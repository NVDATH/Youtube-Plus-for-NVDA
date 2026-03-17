## 2026.3.17

### New Features
- Added cut/copy/paste support in Favorites Videos and Watch List (Ctrl+X/C/V), including cross-list support between the two panels
- Added cut/paste support in Favorites Channels and Favorites Playlists for reordering items within each list
- Multi-select support in all four Favorites panels using Shift+Arrow
- Search text is now preserved per tab when switching between tabs in the Favorites dialog
- Added manual backup button in Settings to back up the active profile on demand
- Added automatic daily backup triggered by the background subscription update worker
- Added restore from backup in Settings with a submenu listing up to the last 5 backups by date
- Backup files are stored in a dedicated folder and auto-rotated to keep only the 5 most recent
- Added Ukrainian (uk) translation by Георгій Галас

### Bug Fixes
- Fixed NVDA reading list items twice when opening the Favorites dialog or switching tabs
- Fixed focus not returning to the correct position after clearing the search field in Favorites
- Fixed Watch List not focusing the newly added item after adding
- Fixed Add button using the wrong worker for Watch List
- Fixed Live Chat Messages dialog showing the wrong video title after viewing other content
- Fixed Live Chat search causing IndexError when the selected item is outside the filtered results range
- Fixed Live Chat search not restoring the correct scroll position after clearing the search field
- Fixed profile list in Settings incorrectly including the backups folder as a selectable profile

### Dependencies
- Updated yt-dlp to v2026.3.13

## 2026.3.3

- **Core Engine Update:** Upgraded internal **yt-dlp to v2026.3.3** for enhanced video extraction performance and stability.

## 2026.2.28

### ✨ New Features
- **User Profiles:** Introduced a dedicated user profile system, allowing users to customize and save their preferences for a more personalized experience.
- **Quick Actions:** Added a new quick access menu to trigger frequently used functions instantly.
- **Full I18n Support:** Refactored the entire codebase to support Internationalization (I18n), enabling seamless translation via Gettext and supporting translator notes.

### 🛠️ Improvements & Fixes
- **Core Engine Update:** Upgraded internal **yt-dlp to v2026.2.21** for enhanced video extraction performance and stability.
- **Dependency Resolution:** Fixed critical internal import errors; the add-on is now fully self-contained and functions correctly without relying on other installed add-ons.
- **General Bug Fixes:** Resolved multiple bugs across various modules, including video list rendering. All features are now expected to be fully operational and stable.

## 2026.2.4

* update yt-dlp to latest 2026.2.4
* Removed potentially confusing commands from the input gesture settings.

## 2026.2.1

* update yt-dlp to latest 2026.1.31
* update some description format
* fix lost library

## 2026.1.31

- remove unuseful extractors from yt-dlp

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
