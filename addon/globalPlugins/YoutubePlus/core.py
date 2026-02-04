# -*- coding: utf-8 -*-
# YoutubePlus for NVDA
# Copyright (C) 2025
# This file is covered by the GNU General Public License.
# You can read the licence by clicking Help->Licence in the NVDA menu
# or by visiting http://www.gnu.org/licenses/old-licenses/gpl-2.0.html
# Shortcut: NVDA+y

import globalPluginHandler
from scriptHandler import script
import threading
import time
from datetime import datetime
import json
import os
import re
import webbrowser
from urllib.parse import urlparse, parse_qs, unquote
from contextlib import contextmanager, redirect_stderr
from http.cookiejar import MozillaCookieJar
from functools import wraps
import ui
import config
import api
import tones
import nvwave
import gui
import wx
import concurrent.futures 
import urllib.request
from collections import OrderedDict
from logHandler import log
import unicodedata
import sys

# Third-party libraries
import pytchat
import yt_dlp
from yt_dlp.utils import DownloadError, ExtractorError
import sqlite3 

# Local addon modules
from .dialogs import (
    HelpDialog,
    InfoDialog,
    TimestampDialog,
    MessagesDialog,
    CommentsDialog,
    FavsDialog,
    SubDialog,
    SearchDialog,
    ChannelVideoDialog,
    ManageSubscriptionsDialog
)

from .utils import retry_on_network_error
from .errors import NetworkRetryError, HandledError

def finally_(func, final):
    @wraps(func)
    def new(*args, **kwargs):
        try: func(*args, **kwargs)
        finally: final()
    return new

class GlobalPlugin(globalPluginHandler.GlobalPlugin):
    instance = None
    scriptCategory = _("YoutubePlus")

    youtube_regex = re.compile(r"youtu\.?be", re.IGNORECASE)

    def __init__(self, *args, **kwargs):
        super(GlobalPlugin, self).__init__(*args, **kwargs)
        log.info("YoutubePlus addon initializing.")
        GlobalPlugin.instance = self
        self._callbacks = {}
        self.chat = None
        self.active = False
        self.messages = []
        self.dialog = None
        self.video_title = ""
        self.first_chat_message_spoken = False
        self.toggling = False
        self.last_message_index = -1
        self.fav_dialog_instance = None
        self.is_long_task_running = False
        self._messages_lock = threading.Lock()
        self._fav_file_lock = threading.Lock()
        self._stop_event = threading.Event()
        self._worker_thread = None
        self._indicator_stop_event = threading.Event()
        self._pause_indicator_event = threading.Event()
        self.choice_made_event = threading.Event()
        self.user_choice = None

        self.update_timer = wx.Timer(gui.mainFrame)
        gui.mainFrame.Bind(wx.EVT_TIMER, self.on_auto_update_tick, self.update_timer)
        self.register_callback("settings_saved", self.manage_auto_update_timer)
        self._init_sub_database()
        
        threading.Thread(target=self._update_subscription_feed_worker, kwargs={'silent': True}, daemon=True).start()
        
        self.manage_auto_update_timer()
        self.help_text = _("""YoutubePlus Layer Commands (Press NVDA+Y to activate)

--- Core Actions (from a YouTube window/URL) ---
- L: Get comments from the current URL (Live Chat, Replay, or Comments)
- I: Get video info
- T: Show video chapters/timestamps
- D: Download video/audio from the current URL
- E: Search YouTube

--- Favorites & Subscriptions ---
- A: Show the "Add to..." menu (for favorites/subscriptions)
- F: Show favorite videos dialog
- C: Show favorite channels dialog
- P: Show favorite playlists dialog
- w: show watch list dialog
- S: Show subscription feed dialog
- M: Show Manage Subscriptions dialog

--- Live Chat Monitoring (while active) ---
- Shift+L: Stop live chat monitoring
- V: Show live chat messages dialog
- R: Toggle automatic speaking of incoming messages

--- Additional Keyboard Shortcuts (within addon dialogs) ---
**In Favorites and Subscription Feed Dialogs:**
- Ctrl+1 through 9: Jump to a specific tab
- Ctrl+Up/Down or Left/Right: Reorder tabs

**In the Subscription Feed Dialog:**
- F2: Rename the current category
- Ctrl+Equals: Add a new category
- Ctrl+Minus: Remove the current category
- Delete: Mark the selected video as seen
- Ctrl+Delete: Mark all videos in the current tab as seen

**In any Favorites Dialog (Videos, Channels, Playlists):**
- Shift+Up/Down: Reorder the selected item
- Delete: Remove the selected item from favorites

--- Help ---
- H: Show this help dialog
""")

    def _init_sub_database(self):
        """
        Initializes the subscription database and creates/updates tables
        to support the new comprehensive category system.
        """
        db_path = os.path.join(os.path.dirname(__file__), 'subscription.db')
        try:
            con = sqlite3.connect(db_path)
            cur = con.cursor()
            
            cur.execute('''
                CREATE TABLE IF NOT EXISTS subscribed_channels (
                    channel_url TEXT PRIMARY KEY,
                    channel_name TEXT NOT NULL,
                    content_types TEXT NOT NULL DEFAULT 'videos,shorts,streams'
                )
            ''')
            cur.execute('''
                CREATE TABLE IF NOT EXISTS videos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT, video_id TEXT UNIQUE NOT NULL,
                    channel_url TEXT NOT NULL, channel_name TEXT NOT NULL,
                    title TEXT, duration_str TEXT, upload_date TEXT
                )
            ''')
            cur.execute("PRAGMA table_info(videos)")
            columns = [col[1] for col in cur.fetchall()]
            if 'content_type' not in columns:
                cur.execute("ALTER TABLE videos ADD COLUMN content_type TEXT NOT NULL DEFAULT 'videos'")

            cur.execute('''
                CREATE TABLE IF NOT EXISTS seen_videos (video_id TEXT PRIMARY KEY)
            ''')

            cur.execute('''
                CREATE TABLE IF NOT EXISTS categories (
                    id INTEGER PRIMARY KEY,
                    name TEXT UNIQUE NOT NULL,
                    position INTEGER NOT NULL
                )
            ''')
            cur.execute('''
                CREATE TABLE IF NOT EXISTS channel_category_links (
                    channel_url TEXT NOT NULL,
                    category_id INTEGER NOT NULL,
                    PRIMARY KEY (channel_url, category_id),
                    FOREIGN KEY (channel_url) REFERENCES subscribed_channels (channel_url) ON DELETE CASCADE,
                    FOREIGN KEY (category_id) REFERENCES categories (id) ON DELETE CASCADE
                )
            ''')

            cur.execute("SELECT COUNT(*) FROM categories")
            if cur.fetchone()[0] == 0:
                log.debug("No categories found. Creating initial 'General' category.")
                cur.execute("INSERT INTO categories (name, position) VALUES (?, ?)", ('General', 0))

            con.commit()
            con.close()
            log.info("Subscription database initialized successfully.")
        except Exception:
            log.exception("Failed to initialize subscription database.")
            
    def register_callback(self, topic, callback_func):
        if topic not in self._callbacks:
            self._callbacks[topic] = []
        if callback_func not in self._callbacks[topic]:
            self._callbacks[topic].append(callback_func)
        log.debug(f"Callback registered for topic '{topic}': {callback_func.__name__}")

    def unregister_callback(self, topic, callback_func):
        if topic in self._callbacks and callback_func in self._callbacks[topic]:
            self._callbacks[topic].remove(callback_func)
            log.debug(f"Callback unregistered for topic '{topic}': {callback_func.__name__}")

    def _notify_callbacks(self, topic, data=None):
        if topic in self._callbacks:
            log.debug(f"Notifying callbacks for topic: {topic}")
            for func in self._callbacks[topic]:
                if data is not None:
                    wx.CallAfter(func, data)
                else:
                    wx.CallAfter(func)
                    
    def manage_auto_update_timer(self):
        interval_minutes = config.conf["YoutubePlus"].get("autoUpdateIntervalMinutes", 0)
        
        if self.update_timer.IsRunning():
            self.update_timer.Stop()
            
        if interval_minutes > 0:
            interval_ms = interval_minutes * 60 * 1000
            log.info(f"Starting/restarting auto-update timer with interval: {interval_minutes} minutes.")
            self.update_timer.Start(interval_ms)
        else:
            log.info("Auto-update timer is disabled.")
            
    def on_auto_update_tick(self, event):
        log.debug("Auto-update timer ticked.")
        if self.is_long_task_running:
            log.debug("Skipping auto-update because another long task is running.")
            return
            
        log.info("Starting scheduled background feed update.")
        threading.Thread(target=self._update_subscription_feed_worker, kwargs={'silent': True}, daemon=True).start()
        
    def is_youtube_url(self, text):
        """Checks if a given string contains a YouTube domain."""
        if not text:
            return False
        return bool(self.youtube_regex.search(text))
        
    def terminate(self):
        log.info("YoutubePlus addon terminating.")
        self.stopChatMonitoring(silent=True)
        self._stop_indicator()

        if MessagesDialog._instance:
            wx.CallAfter(MessagesDialog._instance.Close)
            
        super().terminate()
        log.info("YoutubePlus addon terminated.")

    def getScript(self, gesture):
        if not self.toggling: return super().getScript(gesture)
        script = super().getScript(gesture)
        if not script:
            script_name = self.__YoutubePlusGestures.get(gesture.mainKeyName)
            if script_name:
                script = getattr(self, "script_" + script_name)
        if not script: script = finally_(self.handle_error, self.finish)
        return finally_(script, self.finish)

    def finish(self):
        self.toggling = False
        self.clearGestureBindings()
        self.bindGestures(self.__gestures)

    def handle_error(self, gesture):
        """
        Handles all non-successful layer actions, including invalid keys
        and cancelling the layer. Now respects the user's notification mode.
        """
        mode = config.conf["YoutubePlus"].get("progressIndicatorMode", "beep")
        
        if mode == 'beep':
            tones.beep(100, 120)
        elif mode == 'sound':
            try:
                sound_path = os.path.join(os.path.dirname(__file__), "sounds", "close.wav")
                if os.path.exists(sound_path):
                    nvwave.playWaveFile(sound_path)
                else:
                    tones.beep(100, 120)
            except Exception:
                tones.beep(100, 120)
                
    def _is_specific_youtube_url(self, url):
        """Checks if a URL contains a video ID, playlist ID, or channel identifier."""
        if not url:
            return False
        patterns = [
            r'v=',
            r'list=',
            r'/shorts/',
            r'/live/',
            r'youtu\.be\/',
            r'/channel/',
            r'/c/',
            r'\/@'
        ]
        return any(re.search(pattern, url, re.IGNORECASE) for pattern in patterns)
        
    def _find_youtube_url(self):
        """
        Finds a YouTube URL, prioritizing a specific URL from the current window,
        but falling back to the clipboard if the window's URL is not specific.
        """
        log.debug("Searching for YouTube URL with window-first (but specific) priority.")

        def _search_source(source_func):
            """Internal helper to get text from a source function."""
            try:
                return source_func()
            except Exception:
                return None

        url_from_window = _search_source(api.getCurrentURL)

        if url_from_window and self.is_youtube_url(url_from_window):
            if self._is_specific_youtube_url(url_from_window):
                log.debug("Found specific YouTube URL in current window. Using it.")
                return url_from_window
            else:
                log.debug("Window URL is a generic YouTube page. Checking clipboard as a fallback.")

        url_from_clipboard = _search_source(api.getClipData)
        if url_from_clipboard and self._is_specific_youtube_url(url_from_clipboard):
            log.debug("Found specific YouTube URL in clipboard.")
            return url_from_clipboard

        log.info("No specific YouTube URL found in either window or clipboard.")
        return None
    
    def _clean_youtube_url(self, url):
        """Extracts the video ID from a URL and reconstructs a clean one."""
        if not url:
            return None
        match = re.search(r'(?:watch\?v=|shorts\/)([0-9A-Za-z_-]{11})', url)
        if match:
            video_id = match.group(1)
            return f"https://www.youtube.com/watch?v={video_id}"
        return url
    
    def get_data_for_url(self, url):
        """Helper method to trigger the getData logic from an already known URL."""
        log.info("Getting data for URL provided internally: %s", url)
        threading.Thread(target=self._unified_worker, args=(url, ), daemon=True).start()
            
    def _validate_video_url_and_notify(self, url):
        """
        A central validator for commands that must operate on a single video URL.
        It checks for playlists or channel pages and notifies the user.
        Returns the clean video URL if valid, otherwise returns None.
        """
        if 'list=' in url and 'v=' not in url:
            self._notify_error(
                _("This command is for videos, but the current page is a playlist."),
                log_message=f"Command blocked on pure playlist URL: {url}"
            )
            return None
        
        is_video_format = 'v=' in url or 'shorts/' in url or 'live/' in url or 'youtu.be/' in url
        
        if self._is_specific_youtube_url(url) and not is_video_format:
             self._notify_error(
                _("This command is for videos, but the current page appears to be a channel or playlist."),
                log_message=f"Command blocked on non-video URL (channel/playlist): {url}"
            )
             return None
        return self._clean_youtube_url(url)

    def _get_ydl_instance(self, extra_opts=None):
        """
        Creates and configures a yt_dlp.YoutubeDL instance.
        This method is now the single source of truth for cookie management.
        """
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            #'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
        }

        cookie_mode = config.conf["YoutubePlus"].get("cookieMode", "none")
        browser_to_use = None
        temp_cookie_file = None

        if cookie_mode != 'none':
            browser_to_use = cookie_mode.lower() 
            log.debug(f"Cookie mode set to: {browser_to_use}")
        else:
            log.debug("Cookie mode is 'none' - proceeding without cookies")

        if browser_to_use:
            try:
                log.debug(f"Attempting to use cookies from browser: {browser_to_use}")
                ydl_opts['cookies_from_browser'] = (browser_to_use,) 
            except Exception as e:
                log.warning(f"Could not set cookies_from_browser for {browser_to_use}: {e}")
                
                try:
                    from yt_dlp.cookies import extract_cookies_from_browser
                    from yt_dlp.utils import YoutubeDLError
                    import tempfile
                    
                    log.debug(f"Attempting manual cookie extraction from {browser_to_use}")
                    jar = extract_cookies_from_browser(browser_to_use)
                    
                    if jar and len(jar) > 0:
                        tmp = tempfile.NamedTemporaryFile(
                            prefix='yt_cookies_',
                            delete=False,
                            suffix='.txt',
                            mode='w'
                        )
                        temp_cookie_file = tmp.name
                        jar.filename = temp_cookie_file
                        jar.save(temp_cookie_file, ignore_discard=True, ignore_expires=True)
                        tmp.close()
                        
                        ydl_opts['cookiefile'] = temp_cookie_file
                        log.info(f"Successfully wrote browser cookies to temporary file: {temp_cookie_file}")
                    else:
                        log.warning(f"No cookies found in {browser_to_use}")
                        
                except (YoutubeDLError, FileNotFoundError, PermissionError) as extract_error:
                    log.error(f"Cookie extraction workaround failed for {browser_to_use}: {extract_error}")
                except Exception as unexpected_error:
                    log.exception(f"Unexpected error during cookie extraction: {unexpected_error}")

        if extra_opts:
            ydl_opts.update(extra_opts)

        ydl = yt_dlp.YoutubeDL(ydl_opts)
        
        if temp_cookie_file:
            original_close = ydl.__exit__
            def cleanup_close(*args, **kwargs):
                try:
                    result = original_close(*args, **kwargs)
                    if temp_cookie_file and os.path.exists(temp_cookie_file):
                        os.remove(temp_cookie_file)
                        log.debug(f"Cleaned up temporary cookie file: {temp_cookie_file}")
                    return result
                except Exception as e:
                    log.warning(f"Failed to cleanup temp cookie file: {e}")
            ydl.__exit__ = cleanup_close
        
        return ydl

    @retry_on_network_error(retries=3, delay=5)
    def get_video_info(self, url_or_id, extra_opts=None, fetch_channel_details=False):
        """
        Fetches information using yt-dlp.
        Now with corrected logic to prevent infinite playlist fetching.
        """
        log.debug("Attempting to get info for: %s", url_or_id)

        channel_regex = re.compile(r"/channel/|/c/|/@")
        is_channel = isinstance(url_or_id, str) and bool(channel_regex.search(url_or_id))

        if extra_opts is None:
            extra_opts = {}

        if is_channel:
            if fetch_channel_details:
                extra_opts['playlistend'] = 1
            else:
                extra_opts['playlist_items'] = '0'
        else:
            extra_opts['noplaylist'] = True

        try:
            with self._get_ydl_instance(extra_opts=extra_opts) as ydl:
                info = ydl.extract_info(url_or_id, download=False)
            
            return info
        except DownloadError as e:
            log.warning("get_video_info failed an attempt: %s", e)
            raise
        except Exception:
            log.exception("A non-download error occurred inside get_video_info.")
            raise
            
    @retry_on_network_error(retries=3, delay=5)
    def get_channel_videos(self, channel_url, detailed_fetch=False, channel_name_override=None):
        """
        Fetches videos from a channel URL.
        Can receive a channel_name_override to ensure consistency.
        """
        #log.debug("Fetching videos for channel: %s (Detailed: %s)", channel_url, detailed_fetch)
        fetch_count = config.conf["YoutubePlus"].get("playlist_fetch_count", 20)
        
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'playlistend': fetch_count,
            'extractor_args': {
                'youtubetab': {'skip': ['authcheck']}
            }
        }
        
        if not detailed_fetch:
            ydl_opts['extract_flat'] = 'in_playlist'
        
        try:
            with open(os.devnull, 'w') as devnull:
                with redirect_stderr(devnull):
                    with self._get_ydl_instance(extra_opts=ydl_opts) as ydl:
                        playlist_info = ydl.extract_info(channel_url, download=False)
        except (DownloadError, ExtractorError) as e:
            if "The channel is not currently live" in str(e) or "does not have a" in str(e):
                #log.debug("Channel is not live or missing tab, which can be normal.")
                return []
            raise
        
        video_list = []
        
        determined_channel_name = channel_name_override
        if not determined_channel_name:
            determined_channel_name = (
                playlist_info.get('uploader') or 
                playlist_info.get('channel') or 
                playlist_info.get('title')  # Sometimes channel name is in title for channel URLs
            )
                #log.debug("Channel name from playlist_info: %s", determined_channel_name)
        
        if 'entries' in playlist_info:
            for entry in playlist_info.get('entries', []):
                if entry and entry.get('id'):
                    if not determined_channel_name or determined_channel_name == 'Unknown Channel':
                        entry_channel_name = (
                            entry.get('uploader') or 
                            entry.get('channel') or 
                            entry.get('uploader_id')
                        )
                        if entry_channel_name and entry_channel_name != 'Unknown Channel':
                            determined_channel_name = entry_channel_name
                            #log.debug("Extracted channel name from video entry: %s", determined_channel_name)
                    video_data = {
                        'id': entry.get('id'),
                        'title': entry.get('title', 'N/A'),
                        'duration_str': self._format_duration_verbose(entry.get('duration', 0)),
                        'channel_url': channel_url,
                        'channel_name': determined_channel_name or 'Unknown Channel'
                    }
                    if detailed_fetch:
                        video_data['upload_date'] = entry.get('upload_date')
                        
                    video_list.append(video_data)
        
        if detailed_fetch:
            sort_order = config.conf["YoutubePlus"].get("sortOrder", "newest")
            reverse_flag = (sort_order == 'newest')
            video_list.sort(key=lambda v: v.get('upload_date') or '19700101', reverse=reverse_flag)
        else:
            sort_order = config.conf["YoutubePlus"].get("sortOrder", "newest")
            if sort_order == 'oldest':
                video_list.reverse()
        #log.debug("Extracted %d videos with channel name: %s", len(video_list), determined_channel_name)
        return video_list
        
    def _progress_indicator_worker(self):
        """Worker that provides progress feedback (beep or sound) for background tasks."""
        log.debug("Progress indicator worker started.")
        mode = config.conf["YoutubePlus"].get("progressIndicatorMode", "beep")
        sound_path = None
        if mode == 'sound':
            sound_path = os.path.join(os.path.dirname(__file__), "sounds", "tictac.wav")
            if not os.path.exists(sound_path):
                log.warning("Sound file not found: %s. Falling back to beep mode.", sound_path)
                mode = 'beep'
        while not self._indicator_stop_event.is_set():
            if self._pause_indicator_event.is_set():
                self._indicator_stop_event.wait(0.5)
                continue
            if mode == 'beep':
                tones.beep(440, 100)
                self._indicator_stop_event.wait(2.5)
            elif mode == 'sound':
                try:
                    nvwave.playWaveFile(sound_path)
                except Exception as e:
                    log.error("Failed to play wave file %s: %s", sound_path, e)
                    mode = 'beep'
                self._indicator_stop_event.wait(1)
            else:
                self._indicator_stop_event.wait(1)
        log.debug("Progress indicator worker stopped.")
        
    def _start_indicator(self):
        """Starts the progress indicator thread."""
        self._indicator_stop_event.clear()
        self._pause_indicator_event.clear()
        threading.Thread(target=self._progress_indicator_worker, daemon=True).start()
        
    def _stop_indicator(self):
        """Stops the progress indicator thread."""
        self._indicator_stop_event.set()
        
    def _pause_indicator(self):
        """Pauses the progress indicator."""
        self._pause_indicator_event.set()

    def _resume_indicator(self):
        """Resumes the progress indicator."""
        self._pause_indicator_event.clear()
        
    def _notify_success(self, message):
        """Plays a success sound/beep and shows a UI message based on user settings."""
        mode = config.conf["YoutubePlus"].get("progressIndicatorMode", "beep")
        if mode == 'beep':
            tones.beep(880, 100)
        elif mode == 'sound':
            try:
                sound_path = os.path.join(os.path.dirname(__file__), "sounds", "finish.wav")
                if os.path.exists(sound_path):
                    nvwave.playWaveFile(sound_path)
                else:
                    # Fallback to beep if sound file is missing
                    tones.beep(880, 100)
            except Exception:
                tones.beep(880, 100)
        wx.CallAfter(ui.message, message)

    def _notify_error(self, message, log_message=None):
        """Plays an error sound/beep, shows a UI message, and logs the error."""
        log.error(log_message or message)
        mode = config.conf["YoutubePlus"].get("progressIndicatorMode", "beep")
        if mode == 'beep':
            tones.beep(220, 200)
        elif mode == 'sound':
            try:
                sound_path = os.path.join(os.path.dirname(__file__), "sounds", "error.wav")
                if os.path.exists(sound_path):
                    nvwave.playWaveFile(sound_path)
                else:
                    tones.beep(220, 200)
            except Exception:
                tones.beep(220, 200)
        wx.CallAfter(ui.message, message)
        
    def _notify_delete(self, message):
        """Plays a delete sound/beep and shows a UI message."""
        mode = config.conf["YoutubePlus"].get("progressIndicatorMode", "beep")
        if mode == 'beep':
            tones.beep(220, 100)
        elif mode == 'sound':
            try:
                sound_path = os.path.join(os.path.dirname(__file__), "sounds", "delete.wav")
                if os.path.exists(sound_path):
                    nvwave.playWaveFile(sound_path)
                else:
                    tones.beep(220, 100)
            except Exception:
                tones.beep(220, 100)
        wx.CallAfter(ui.message, message)
        
    def _play_success_sound(self):
        """Plays only the success sound/beep based on user settings."""
        mode = config.conf["YoutubePlus"].get("progressIndicatorMode", "beep")
        if mode == 'beep':
            tones.beep(880, 100)
        elif mode == 'sound':
            try:
                sound_path = os.path.join(os.path.dirname(__file__), "sounds", "finish.wav")
                if os.path.exists(sound_path):
                    nvwave.playWaveFile(sound_path)
                else:
                    tones.beep(880, 100)
            except Exception:
                tones.beep(880, 100)
    
    def _notify_layer_activated(self):
        """Plays a sound/beep for layer activation based on user settings."""
        mode = config.conf["YoutubePlus"].get("progressIndicatorMode", "beep")
        if mode == 'beep':
            tones.beep(440, 75)
        elif mode == 'sound':
            try:
                sound_path = os.path.join(os.path.dirname(__file__), "sounds", "start.wav")
                if os.path.exists(sound_path):
                    nvwave.playWaveFile(sound_path)
                else:
                    tones.beep(440, 75)
            except Exception:
                tones.beep(440, 75)
        wx.CallAfter(ui.message, _("activate YoutubePlus"))

    def _format_comments_for_display(self, raw_comments):
        """
        Takes the raw comment data from yt-dlp and formats it into a flat list
        for display, handling pinned comments, sorting, and threading.
        """
        log.debug("Formatting %d raw comments for display.", len(raw_comments))
        pinned_comments = [c for c in raw_comments if c.get('is_pinned')]
        other_comments = [c for c in raw_comments if not c.get('is_pinned')]
        log.debug("Found %d pinned and %d other comments.", len(pinned_comments), len(other_comments))

        comments_map = {c['id']: {**c, 'replies': []} for c in other_comments if 'id' in c}
        top_level_comments = []

        for cid, c in comments_map.items():
            parent_id = c.get('parent')
            if parent_id and parent_id != 'root' and parent_id in comments_map:
                comments_map[parent_id]['replies'].append(c)
            else:
                top_level_comments.append(c)

        for c in comments_map.values():
            c['replies'].sort(key=lambda r: r.get('timestamp', 0))

        sort_order = config.conf["YoutubePlus"].get("sortOrder", "newest")
        reverse_flag = (sort_order == 'newest')
        top_level_comments.sort(key=lambda c: c.get('timestamp', 0), reverse=reverse_flag)
        log.debug("Sorted top-level comments by '%s' order.", sort_order)

        final_list = self._flatten_comments(pinned_comments)
        final_list.extend(self._flatten_comments(top_level_comments))
        return final_list
            
    def _flatten_comments(self, comments, level=0, parent_author=None):
        """
        Recursively flattens a list of comments and their replies into a single list,
        handling indentation levels for threading.
        """
        flat_list = []
        for c in comments:
            author = c.get('author')
            message = ""
            
            if paid_info := c.get('paid'):
                original_text = c.get('text', '')
                message = f"Super Thanks ({paid_info}): {original_text}"
            else:
                message = c.get('text', '')

            if parent_author and not paid_info:
                message = "reply to {author}: ".format(author=parent_author) + message

            flat_list.append({
                'author': author,
                'message': message.strip(),
                'time': c.get('_time_text', ''),
                'level': level
            })
            if c.get('replies'):
                flat_list.extend(self._flatten_comments(c['replies'], level + 1, parent_author=c.get('author')))
        return flat_list

    def _format_replay_for_display(self, replay_data):
        """
        Takes the raw live chat replay data (from the JSON subtitle file)
        and formats it into a flat list for display.
        """
        log.debug("Formatting %d raw replay items.", len(replay_data))
        flat_list = []
        for item in replay_data:
            action_item = item.get('replayChatItemAction', {}).get('actions', [{}])[0].get('addChatItemAction', {}).get('item', {})
            if not action_item:
                continue

            author = ""
            message = ""
            
            if text_renderer := action_item.get('liveChatTextMessageRenderer'):
                log.debug("Processing a liveChatTextMessageRenderer item.")
                author = text_renderer.get('authorName', {}).get('simpleText', '')
                
                message_parts = []
                for run in text_renderer.get('message', {}).get('runs', []):
                    if 'text' in run:
                        message_parts.append(run['text'])
                    elif 'emoji' in run:
                        emoji_data = run['emoji']
                        if emoji_data.get('isCustomEmoji', False):
                            label = emoji_data.get('image', {}).get('accessibility', {}).get('accessibilityData', {}).get('label', '')
                            if not label:
                                label = emoji_data.get('shortcuts', ['emoji'])[0]
                            message_parts.append(f"[{label}]")
                        else:
                            message_parts.append(emoji_data.get('emojiId', ''))
                message = "".join(message_parts)
                flat_list.append({
                    'author': author,
                    'message': message,
                    'time': '',
                    'level': 0,
                    'type': 'textMessage',
                    'amount': ''
                })

            elif paid_renderer := action_item.get('liveChatPaidMessageRenderer'):
                log.debug("Processing a liveChatPaidMessageRenderer item (Super Chat).")
                author = paid_renderer.get('authorName', {}).get('simpleText', '')
                amount = paid_renderer.get('purchaseAmountText', {}).get('simpleText', '')
                paid_message = "".join(p.get('text', '') for p in paid_renderer.get('message', {}).get('runs', []))
                message = f"Super Chat ({amount}): {paid_message}"
                flat_list.append({
                    'author': author,
                    'message': message,
                    'time': '',
                    'level': 0,
                    'type': 'superChat',
                    'amount': amount
                })

            elif sticker_renderer := action_item.get('liveChatPaidStickerRenderer'):
                log.debug("Processing a liveChatPaidStickerRenderer item (Super Sticker).")
                author = sticker_renderer.get('authorName', {}).get('simpleText', '')
                amount = sticker_renderer.get('purchaseAmountText', {}).get('simpleText', '')
                message = f"Super Sticker ({amount})"
                flat_list.append({
                    'author': author,
                    'message': message,
                    'time': '',
                    'level': 0,
                    'type': 'superSticker',
                    'amount': amount
                })

            elif membership_renderer := action_item.get('liveChatMembershipItemRenderer'):
                log.debug("Processing a liveChatMembershipItemRenderer item.")
                message_runs = membership_renderer.get('headerSubtext', {}).get('runs', [])
                full_message = "".join(run.get('text', '') for run in message_runs)
                if full_message:
                    author = "YouTube Membership"
                    message = full_message
                    flat_list.append({
                        'author': author,
                        'message': message,
                        'time': '',
                        'level': 0,
                        'type': 'membership',
                        'amount': ''
                    })

            elif mode_change_renderer := action_item.get('liveChatModeChangeMessageRenderer'):
                log.debug("Processing a liveChatModeChangeMessageRenderer item.")
                message_runs = mode_change_renderer.get('text', {}).get('runs', [])
                icon_type = mode_change_renderer.get('icon', {}).get('iconType', '')
                full_message = "".join(run.get('text', '') for run in message_runs)
                if full_message:
                    author = f"YouTube System ({icon_type})"
                    message = full_message
                    flat_list.append({
                        'author': author,
                        'message': message,
                        'time': '',
                        'level': 0,
                        'type': 'modeChange',
                        'amount': ''
                    })
        
        sort_order = config.conf["YoutubePlus"].get("sortOrder", "newest")
        if sort_order == 'newest':
            flat_list.reverse()
            
        return flat_list

    def _format_duration_verbose(self, seconds):
        if not isinstance(seconds, (int, float)) or seconds <= 0: return _("")
        seconds = int(seconds)
        parts = []
        h, rem = divmod(seconds, 3600)
        m, s = divmod(rem, 60)
        if h > 0: parts.append(_("{h} Hour").format(h=h) if h == 1 else _("{h} Hours").format(h=h))
        if m > 0: parts.append(_("{m} Minute").format(m=m) if m == 1 else _("{m} Minutes").format(m=m))
        if s > 0 or not parts: parts.append(_("{s} Second").format(s=s) if s == 1 else _("{s} Seconds").format(s=s))
        return " ".join(parts)

    def get_total_paid_amount_from_list(self, message_list):
        """
        Calculates the total amount from Super Chat and Super Sticker messages.
        """
        log.debug("Calculating total paid amount from a list of %d items.", len(message_list))
        total_amounts = {}
        for message_obj in message_list:
            if message_obj.get('type') in ('superChat', 'superSticker'):
                amount_string = message_obj.get('amount', '')
                if amount_string:
                    match = re.match(r'([^\d\s.,]+)?\s*([\d,.]+)\s*([^\d\s.,]+)?', amount_string.strip())
                    if match:
                        currency_part = (match.group(1) or match.group(3) or "").strip()
                        numeric_value_str = match.group(2).replace(',', '')

                        try:
                            amount_value = float(numeric_value_str)
                            currency_code = currency_part
                            
                            if currency_part == '$': currency_code = 'USD'
                            elif currency_part == '¥': currency_code = 'JPY'
                            elif currency_part == '€': currency_code = 'EUR'
                            elif currency_part == '฿': currency_code = 'THB'
                            elif not currency_code and amount_value > 0: currency_code = "UNKNOWN"

                            if currency_code:
                                total_amounts[currency_code] = total_amounts.get(currency_code, 0.0) + amount_value
                        except ValueError:
                            log.warning("Could not parse amount value from string: %s", numeric_value_str)
        log.debug("Paid amount calculation result: %s", total_amounts)
        return total_amounts
        
    def _show_info_dialog(self, title, info_text):
        gui.mainFrame.prePopup()
        dialog_title = _("Info of {title}").format(title=title)
        dialog = InfoDialog(gui.mainFrame, dialog_title, info_text)
        dialog.Show()
        self._play_success_sound()
        gui.mainFrame.postPopup()
        
    def show_chapters_dialog(self, title, chapters, url):
        gui.mainFrame.prePopup()
        dialog = TimestampDialog(gui.mainFrame, title, chapters, url)
        dialog.Show()
        self._play_success_sound()
        gui.mainFrame.postPopup()     
       
    def _show_choice_dialog(self, event, info):
        comment_count = info.get('comment_count', 0)
        dlg = wx.MessageDialog(gui.mainFrame, "This video has a live chat replay. What would you like to view?", "Choice", wx.YES_NO | wx.CANCEL | wx.ICON_QUESTION)
        dlg.SetYesNoCancelLabels(f"Show {comment_count} &Comments", "Show &Live Chat Replay", "Ca&ncel")
        result = dlg.ShowModal()
        dlg.Destroy()
        if result == wx.ID_YES: self.user_choice = 'comments'
        elif result == wx.ID_NO: self.user_choice = 'replay'
        else: self.user_choice = 'cancel'
        event.set()

    def _process_video_type(self, url, info):
        """Determines if a VOD has replay or just comments and starts the fetch process."""
        log.debug("Processing VOD type for video: %s", info.get('title'))
        self.video_title = info.get('title', 'Unknown Title')
        has_replay = False
        subtitles = info.get('subtitles', {})
        auto_captions = info.get('automatic_captions', {})
        
        if 'live_chat' in subtitles or 'live_chat' in auto_captions:
            has_replay = True

        comment_count = info.get('comment_count') or 0

        if info.get('was_live') and has_replay:
            self._pause_indicator()
            self.choice_made_event.clear()
            self.user_choice = None
            #log.info("Video has a live chat replay. Showing choice dialog.")
            wx.CallAfter(self._show_choice_dialog, self.choice_made_event, info)
        else:
            #log.info("Video does not have a replay, fetching comments.")
            self.user_choice = 'comments'
            self.choice_made_event.set()
        threading.Thread(target=self._start_fetch_worker_after_choice, args=(url, comment_count), daemon=True).start()

    def _unified_worker(self, url):
        """
        The main worker entry point for getting any video data.
        It now correctly handles and provides feedback for playlist and channel URLs.
        """
        clean_url = self._validate_video_url_and_notify(url)
        if not clean_url:
            return
        self._start_indicator()
        try:
            self.is_long_task_running = True
            info = self.get_video_info(url)

            if info.get('is_live'):
                threading.Thread(target=self._start_monitoring_worker, args=(url, info), daemon=True).start()
            else:
                wx.CallAfter(self._process_video_type, url, info)

        except (DownloadError, NetworkRetryError) as e:
            self._stop_indicator()
            self._notify_error(_("Failed to get video data. The video may be private, unavailable, or there was a network issue."), log_message=f"Could not get info for URL {url} after retries: {e}")
        except Exception as e:
            self._stop_indicator()
            self._notify_error(_("An unexpected error occurred."), log_message=f"An unexpected error occurred in the unified worker: {e}")
        finally:
            self.is_long_task_running = False
            
    def _start_fetch_worker_after_choice(self, url, comment_count=0):
        """Waits for the user's choice (replay vs comments) and starts the actual fetch worker."""
        log.debug("Waiting for user choice...")
        self.choice_made_event.wait()
        data_to_fetch = self.user_choice
        
        if data_to_fetch == 'cancel' or data_to_fetch is None:
            #log.info("User cancelled data fetching.")
            self._stop_indicator()
            return

        if data_to_fetch == 'comments' and comment_count == 0:
            #log.info("Aborting fetch: Video has no comments.")
            self._stop_indicator()
            self._notify_error(_("This video has no comments."), log_message="Aborting fetch: Video has no comments.")            
            return

        if data_to_fetch == 'comments':
            wx.CallAfter(ui.message, _("Loading {count} comments...").format(count=comment_count))
        else:
            wx.CallAfter(ui.message, "Loading live chat replay...")
        self._resume_indicator()
        threading.Thread(target=self._fetch_and_process_data_worker, args=(url, self.video_title, data_to_fetch, ), daemon=True).start()
        
    def _get_info_worker(self, url):
        clean_url = self._validate_video_url_and_notify(url)
        if not clean_url:
            return
        self._start_indicator()
        try:
            self.is_long_task_running = True

            info = self.get_video_info(url)
            
            if info.get('is_live'):
                wx.CallAfter(ui.message, "This is a live stream. Use the 'Get Data' (g) command to monitor live chat.")
                return

            title = info.get('title', 'N/A')
            uploader = info.get('uploader', 'N/A')
            duration = self._format_duration_verbose(info.get('duration', 0))
            upload_date_str = info.get('upload_date')
            upload_date = datetime.strptime(upload_date_str, '%Y%m%d').strftime('%d %B %Y') if upload_date_str else 'N/A'
            
            view_count_num = info.get('view_count') or 0
            like_count_num = info.get('like_count') or 0
            comment_count_num = info.get('comment_count') or 0

            view_count = f"{view_count_num:,}"
            like_count = f"{like_count_num:,}"
            comment_count = f"{comment_count_num:,}"
            
            description = info.get('description', 'N/A')
            
            info_text = (f"Title: {title}\n"
                         f"Channel: {uploader}\n"
                         f"Duration: {duration}\n"
                         f"Uploaded: {upload_date}\n"
                         f"Views: {view_count}\n"
                         f"Likes: {like_count}\n"
                         f"Comments: {comment_count}\n"
                         f"--------------------\n"
                         f"Description:\n{description}")
            wx.CallAfter(self._show_info_dialog, title, info_text)
        except (DownloadError, NetworkRetryError) as e:
            log.error("Could not get video info for 'getInfo' command. Error: %s", e)
            self._notify_error(_("Failed to get video info. The video may be private or the network is down."))
        except Exception as e:
            log.exception("Unexpected error in 'Get Info' worker.")
            self._notify_error(_("An unexpected error occurred. Please check the log for details."))
        finally:
            self.is_long_task_running = False
            self._stop_indicator()
            
    def _show_chapters_worker(self, url):
        clean_url = self._validate_video_url_and_notify(url)
        if not clean_url:
            return
        self._start_indicator()
        try:
            self.is_long_task_running = True
            info = self.get_video_info(url)
            
            chapters = info.get('chapters')
            if chapters and len(chapters) > 0:
                title = info.get('title', 'Unknown Video')
                dialog_title = _("Chapters for {title}").format(title=title)
                wx.CallAfter(self.show_chapters_dialog, dialog_title, chapters, url)
            else:
                self._notify_error(_("No chapters found in this video."))

        except (DownloadError, NetworkRetryError) as e:
            self._notify_error(_("Failed to get chapters. The video may be private or the network is down."), log_message=f"Could not get chapters for {url}: {e}")
        except Exception as e:
            log.exception("Unexpected error in 'Show Chapters' worker.")
            self._notify_error(_("An unexpected error occurred. Please check the log for details."))
        finally:
            self.is_long_task_running = False
            self._stop_indicator()

    def _fetch_and_process_data_worker(self, url_or_id, video_title, data_to_fetch):
        #log.info("Fetching '%s' data for video: %s", data_to_fetch, video_title)
        try:
            display_list, dialog_title = None, None
            is_replay_data = False # Flag to pass to CommentsDialog
            
            if data_to_fetch == 'comments':
                log.debug("Fetching comments via yt-dlp.")
                opts = {'getcomments': True, 'extract_flat': True}
                with self._get_ydl_instance(extra_opts=opts) as ydl:
                    info = ydl.extract_info(url_or_id, download=False)
                raw_data = info.get('comments')
                if not raw_data: raise ValueError("No comments found in video data.")
                
                display_list = self._format_comments_for_display(raw_data)
                dialog_title = "{count} comments of {title}".format(count=len(display_list), title=video_title)

            elif data_to_fetch == 'replay':
                log.debug("Fetching live chat replay subtitles via yt-dlp.")
                opts = {'skip_download': True, 'writesubtitles': True, 'subtitleslangs': ['live_chat']}
                with self._get_ydl_instance(extra_opts=opts) as ydl:
                    res = ydl.extract_info(url_or_id, download=True)
                
                requested_subs = res.get('requested_subtitles')
                if not requested_subs or 'live_chat' not in requested_subs:
                    raise FileNotFoundError("Live chat replay subtitles not available for this video.")
                
                chat_filepath = requested_subs['live_chat'].get('filepath')
                if not chat_filepath or not os.path.exists(chat_filepath):
                    raise FileNotFoundError("Could not find downloaded live chat replay file.")
                
                with open(chat_filepath, 'r', encoding='utf-8') as f: raw_data = [json.loads(line) for line in f]
                os.remove(chat_filepath)
                if not raw_data: raise ValueError("Live chat replay file was empty.")
                
                display_list = self._format_replay_for_display(raw_data)
                dialog_title = "{count} live chat replay of {title}".format(count=len(display_list), title=video_title)
                is_replay_data = True
            
            self._stop_indicator()
            self._play_success_sound()
            wx.CallAfter(self.show_comments_dialog, dialog_title, display_list, is_replay_data)
        except (DownloadError, FileNotFoundError, ValueError) as e:
            self._stop_indicator()
            log.error("Could not load VOD data: %s", e)
            wx.CallAfter(ui.message, _("Could not load data: {error}").format(error=e))
        except Exception as e:
            self._stop_indicator()
            log.exception("An unexpected error occurred while fetching VOD data.")
            wx.CallAfter(ui.message, _("An unexpected error occurred. Please check the log for details."))
            
    def _chat_monitor_worker(self, chat_instance):
        """The main worker loop for fetching live chat messages."""
        log.info("Chat monitor worker started for video: %s", self.video_title)
        # Define the hard limit as a constant inside the worker
        HARD_MESSAGE_LIMIT = 200000
        first_message_received = False
        limit_warning_sent = False

        while not self._stop_event.is_set():
            try:
                if not chat_instance.is_alive():
                    wx.CallAfter(ui.message, _("Connection to live chat lost. The stream may have ended."))
                    wx.CallAfter(self.stopChatMonitoring, silent=True)
                    break
                
                new_messages_batch = []
                for c in chat_instance.get().sync_items():
                    message_obj = None
                    if c.type == "textMessage":
                        message_obj = {'datetime': c.datetime, 'author': c.author.name, 'message': c.message, 'type': c.type, 'amount': ''}
                    elif c.type in ("superChat", "superSticker"):
                        message_content = c.message if hasattr(c, 'message') else ''
                        prefix = "Super Chat" if c.type == "superChat" else "Super Sticker"
                        full_message = f"{prefix} ({c.amountString}): {message_content}".strip()
                        message_obj = {'datetime': c.datetime, 'author': c.author.name, 'message': full_message, 'type': c.type, 'amount': c.amountString}

                    if message_obj:
                        new_messages_batch.append(message_obj)

                if new_messages_batch:
                    if not self.is_long_task_running:
                        self._stop_indicator()
                    
                    with self._messages_lock:
                        self.messages.extend(new_messages_batch)
                        
                        # Memory Safety Net using the hard-coded constant
                        if len(self.messages) > HARD_MESSAGE_LIMIT:
                            self.messages = self.messages[-HARD_MESSAGE_LIMIT:]
                            if not limit_warning_sent:
                                log.warning("Hard message limit (%d) reached. Older messages are being discarded.", HARD_MESSAGE_LIMIT)
                                wx.CallAfter(ui.message, _("To conserve memory, older chat messages have been discarded."))
                                limit_warning_sent = True
                    
                    if MessagesDialog._instance and MessagesDialog._instance.IsShown():
                        wx.CallAfter(MessagesDialog._instance.add_new_messages, new_messages_batch)
                    
                    if not first_message_received:
                        first_message_received = True
                        if config.conf["YoutubePlus"]["autoSpeak"]:
                            wx.CallAfter(ui.message, "Receiving live chat of {video_title}".format(video_title=self.video_title))
                        else:
                            wx.CallAfter(self.openMessagesDialog)
                    
                    if config.conf["YoutubePlus"]["autoSpeak"]:
                        for msg_obj in new_messages_batch:
                            speak_text = f"{msg_obj['author']}: {msg_obj['message']}"
                            wx.CallAfter(ui.message, speak_text)

            except Exception as e:
                log.exception("Error in chat monitor worker loop. The monitor will stop.")
                wx.CallAfter(ui.message, _("An error occurred while receiving live chat. Monitoring stopped."))
                wx.CallAfter(self.stopChatMonitoring, silent=True)
                break
            
            refresh_interval = config.conf["YoutubePlus"].get("refreshInteval", 5)
            self._stop_event.wait(timeout=refresh_interval)
        
        if chat_instance:
            chat_instance.terminate()

    def _perform_export(self):
        """
        Worker function to perform the actual file export.
        This should be run in a separate thread.
        """
        try:
            export_path = config.conf["YoutubePlus"].get("exportPath", "") or os.path.join(os.path.expanduser("~"), "Desktop")
            if not os.path.exists(export_path):
                os.makedirs(export_path)

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            safe_title = unicodedata.normalize('NFC', self.video_title)
            safe_title = "".join(c for c in safe_title if c not in '\\/*?:"<>|').strip()
            if not safe_title:
                safe_title = "LiveChat"

            filename = f"LiveChat_{safe_title}_{timestamp}.txt"
            filepath = os.path.join(export_path, filename)
            with self._messages_lock:
                with open(filepath, 'w', encoding='utf-8') as f:
                    for msg_obj in self.messages:
                        author = msg_obj.get('author', '')
                        message = msg_obj.get('message', '')
                        f.write(f"@{author}: {message}\n\n")

            log.info(f"Chat exported successfully to: {filepath}")
            wx.CallAfter(ui.message, _("Chat saved to {filename}").format(filename=filename))
            return True

        except Exception as e:
            log.error(f"Failed to export chat: {e}")
            log.exception("Full traceback:")
            wx.CallAfter(ui.message, _("Failed to save chat history."))
            return False

    def _export_chat(self):
        """
        Ask user to confirm export in the main thread.
        If confirmed, it spawns a new worker thread to handle the export.
        """
        if not self.messages:
            log.warning("No messages to export")
            return

        # This part now runs directly in the main thread via wx.CallAfter
        # from the original caller.
        message_count = len(self.messages)
        dlg = wx.MessageDialog(
            gui.mainFrame,
            _("The stream has ended. You have {count} chat messages.\n\nWould you like to save the chat history?").format(count=message_count),
            _("Save Chat History?"),
            wx.YES_NO | wx.ICON_QUESTION
        )
        result = dlg.ShowModal()
        dlg.Destroy()

        if result == wx.ID_YES:
            #log.info("User agreed to export chat. Starting export thread.")
            # Start the actual export in a new background thread
            threading.Thread(target=self._perform_export, daemon=True).start()
        else:
            log.info("User declined to export chat")
                        
    def _start_monitoring_worker(self, url, info):
        """Prepares and starts the live chat monitoring."""
        try:
            if not info.get('is_live'):
                raise ValueError("The video is not currently live.")
            # Delegate to the main thread to finish setup, as it involves GUI elements.
            wx.CallAfter(self._finish_chat_setup, info['id'], info['title'])
        except Exception as e:
            self._stop_indicator()
            log.error("Could not start live chat monitoring. Error: %s", e)
            wx.CallAfter(ui.message, f"Could not receive live chat. {e}")

    def add_item_to_favorites_worker(self, url):
        """Worker to handle adding a favorite in the background with file lock and dialog refresh."""
        ui.message(_("Adding to favorites..."))
        self._start_indicator()
        self.is_long_task_running = True
        try:
            info = self.get_video_info(url)
            
            if not info or info.get('_type', 'video') != 'video':
                wx.CallAfter(ui.message, _("The provided link is not for a single video."))
                return

            video_id = info.get('id')

            with self._fav_file_lock:
                fav_file_path = os.path.join(os.path.dirname(__file__), 'fav_video.json')
                favorites = []
                try:
                    with open(fav_file_path, 'r', encoding='utf-8') as f:
                        favorites = json.load(f)
                except (FileNotFoundError, json.JSONDecodeError):
                    favorites = []

                if any(item['video_id'] == video_id for item in favorites):
                    wx.CallAfter(ui.message, _("This video is already in your favorites."))
                    return

                has_replay = 'live_chat' in info.get('subtitles', {}) or 'live_chat' in info.get('automatic_captions', {})
                new_item = {
                    "video_id": video_id, "title": info.get('title'), "channel_name": info.get('uploader'),
                    "channel_url": info.get('channel_url'), "duration_str": self._format_duration_verbose(info.get('duration', 0)),
                    "was_live": info.get('was_live', False), "has_replay": has_replay
                }
                favorites.append(new_item)

                with open(fav_file_path, 'w', encoding='utf-8') as f:
                    json.dump(favorites, f, indent=2, ensure_ascii=False)

            self._notify_callbacks("fav_video_updated", {"action": "add"})
            self._notify_success(_("Added '{title}' to favorites.").format(title=new_item['title']))

        except Exception as e:
            self._notify_error(_("Failed to add favorite."), log_message=f"Failed to add favorite for URL {url}: {e}")
        finally:
            self.is_long_task_running = False
            self._stop_indicator()
            
    def add_channel_to_favorites_worker(self, url):
        """
        Worker to handle adding a channel to favorites.
        Now performs a two-step fetch to ensure correct channel description.
        """
        ui.message(_("Adding to favorite channels..."))
        self._start_indicator()
        self.is_long_task_running = True
        try:
            initial_info = self.get_video_info(url, extra_opts={'playlist_items': '1'})
            if isinstance(initial_info, dict) and initial_info.get('entries'):
                initial_info = initial_info['entries'][0]
            
            channel_url = initial_info.get('channel_url')
            if not channel_url:
                raise ValueError("Could not determine a valid channel URL from the provided link.")

            channel_info = self.get_video_info(channel_url, fetch_channel_details=True)
            if not channel_info:
                raise ValueError("Could not retrieve detailed information for the channel.")

            channel_name = channel_info.get('channel') or channel_info.get('uploader')
            description = channel_info.get('description', '')
            subscriber_count = channel_info.get('channel_follower_count')

            with self._fav_file_lock:
                fav_file_path = os.path.join(os.path.dirname(__file__), 'fav_channel.json')
                favorites = []
                try:
                    with open(fav_file_path, 'r', encoding='utf-8') as f:
                        favorites = json.load(f)
                except (FileNotFoundError, json.JSONDecodeError):
                    favorites = []

                if any(item.get('channel_url') == channel_url for item in favorites):
                    wx.CallAfter(ui.message, _("This channel is already in your favorites."))
                    return

                new_item = {
                    "channel_name": channel_name,
                    "channel_url": channel_url,
                    "subscriber_count": subscriber_count,
                    "description": description
                }
                favorites.append(new_item)

                with open(fav_file_path, 'w', encoding='utf-8') as f:
                    json.dump(favorites, f, indent=2, ensure_ascii=False)
            
            self._notify_callbacks("fav_channel_updated", {"action": "add"})
            self._notify_success(_("Added '{channel}' to favorites.").format(channel=new_item['channel_name']))

        except Exception as e:
            self._notify_error(_("Failed to add favorite."), log_message=f"Failed to add favorite for URL {url}: {e}")
        finally:
            self.is_long_task_running = False
            self._stop_indicator()
            
    def add_playlist_to_favorites_worker(self, url):
        """Worker to handle adding a playlist to favorites."""
        ui.message(_("Adding playlist to favorites..."))
        self._start_indicator()
        self.is_long_task_running = True
        
        try:
            list_match = re.search(r'[?&]list=([^&]+)', url)
            if not list_match or 'youtube.com' not in url.lower():
                raise ValueError("URL does not contain a valid YouTube playlist ID.")

            playlist_id = list_match.group(1)
            clean_playlist_url = f"https://www.youtube.com/playlist?list={playlist_id}"
            log.debug(f"Cleaned mixed URL to pure playlist URL: {clean_playlist_url}")
            
            ydl_opts = {'quiet': True, 'no_warnings': True, 'extract_flat': True}
            with self._get_ydl_instance(extra_opts=ydl_opts) as ydl:
                info = ydl.extract_info(clean_playlist_url, download=False)
                
            with self._fav_file_lock:
                fav_file_path = os.path.join(os.path.dirname(__file__), 'fav_playlist.json')
                favorites = []
                try:
                    with open(fav_file_path, 'r', encoding='utf-8') as f:
                        favorites = json.load(f)
                except (FileNotFoundError, json.JSONDecodeError):
                    favorites = []
                
                if any(item.get('playlist_id') == playlist_id for item in favorites):
                    wx.CallAfter(ui.message, _("This playlist is already in your favorites."))
                    return

                new_item = {
                    "playlist_title": info.get('title', 'Unknown Playlist'),
                    "playlist_url": f"https://www.youtube.com/playlist?list={playlist_id}",
                    "playlist_id": playlist_id,
                    "video_count": info.get('playlist_count') or len(info.get('entries', [])),
                    "uploader": info.get('uploader', 'Unknown'),
                    "uploader_channel_id": info.get('uploader_id', ''),
                    "uploader_url": info.get('uploader_url', ''),
                    "description": (info.get('description', '')[:500] if info.get('description') else ""),
                }
                favorites.append(new_item)
                
                with open(fav_file_path, 'w', encoding='utf-8') as f:
                    json.dump(favorites, f, indent=2, ensure_ascii=False)
            
            self._notify_callbacks("fav_playlist_updated", {"action": "add"})
            self._notify_success(_("Added '{playlist}' to favorites.").format(playlist=new_item['playlist_title']))
            
        except Exception as e:
            self._notify_error(_("Failed to add favorite playlist."), log_message=f"Failed to add playlist for URL {url}: {e}")
        finally:
            self.is_long_task_running = False
            self._stop_indicator()
            
    def _update_playlist_count_worker(self, playlist_id, new_count):
        """
        Safely updates the video_count for a specific playlist and notifies the UI
        with specific data for a targeted update.
        """
        if not playlist_id or new_count is None:
            return
        
        with self._fav_file_lock:
            fav_file_path = os.path.join(os.path.dirname(__file__), 'fav_playlist.json')
            playlists = []
            try:
                with open(fav_file_path, 'r', encoding='utf-8') as f:
                    playlists = json.load(f)
            except (FileNotFoundError, json.JSONDecodeError):
                return

            item_updated = False
            for playlist in playlists:
                if playlist.get('playlist_id') == playlist_id:
                    if playlist.get('video_count') != new_count:
                        log.info(f"Updating video count for playlist '{playlist.get('playlist_title')}' from {playlist.get('video_count')} to {new_count}.")
                        playlist['video_count'] = new_count
                        item_updated = True
                    break
            
            if item_updated:
                try:
                    with open(fav_file_path, 'w', encoding='utf-8') as f:
                        json.dump(playlists, f, indent=2, ensure_ascii=False)

                    update_data = {'playlist_id': playlist_id, 'new_count': new_count}
                    self._notify_callbacks("fav_playlist_item_updated", update_data)
                except IOError:
                    log.error("Could not save updated playlist file.")

    def _view_channel_worker(self, url, dialog_title_template, content_type_label="videos", base_channel_url=None, base_channel_name=None):
        """
        Generic worker to fetch a list of videos from any URL (channel or playlist)
        and display them in the ChannelVideoDialog.
        """
        message = dialog_title_template.format(type=content_type_label)
        ui.message(message)
        self._start_indicator()
        self.is_long_task_running = True
        try:
            is_playlist = 'list=' in url
            playlist_id_to_update = None
            new_count_to_update = None
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'extract_flat': 'in_playlist',
            }

            is_playlist = 'list=' in url
            if is_playlist:
                log.info("Fetching all videos from playlist.")
            else:
                fetch_count = config.conf["YoutubePlus"].get("playlist_fetch_count", 20)
                ydl_opts['playlistend'] = fetch_count

            with open(os.devnull, 'w') as devnull:
                with redirect_stderr(devnull):
                    try:
                        with self._get_ydl_instance(extra_opts=ydl_opts) as ydl:
                            info = ydl.extract_info(url, download=False)
                    except (DownloadError, ExtractorError) as e:
                        if "does not have a" in str(e) or "The channel is not currently live" in str(e):
                            log.debug(f"Gracefully handling expected yt-dlp info: {e}")
                            info = {'entries': []}
                        else:
                            raise e

            video_list = []
            if 'entries' in info:
                info_channel_name = info.get('uploader') or info.get('channel')
                info_channel_url = info.get('uploader_url') or info.get('channel_url')

                for entry in info.get('entries', []):
                    if entry and entry.get('id'):
                        video_list.append({
                            'id': entry.get('id'),
                            'title': entry.get('title', 'N/A'),
                            'duration_str': self._format_duration_verbose(entry.get('duration', 0)),
                            'channel_url': base_channel_url or info_channel_url, 
                            'channel_name': base_channel_name or info_channel_name
                        })
            
            sort_order = config.conf["YoutubePlus"].get("sortOrder", "newest")
            if sort_order == 'oldest':
                video_list.reverse()
            
            if not video_list:
                self._notify_error(_("No videos found."), log_message=f"No videos found for URL: {url}")
                return

            if is_playlist:
                playlist_id_to_update = info.get('id')
                new_count_to_update = info.get('playlist_count') or len(info.get('entries', []))
                dialog_title = _("{count} videos in {playlist}").format(count=len(video_list), playlist=info.get('title', 'Playlist'))
            else:
                dialog_title = _("Recent {count} {type} from {channel}").format(count=len(video_list), type=content_type_label, channel=info.get('uploader', 'Channel'))

            def show_dialog():
                dialog = ChannelVideoDialog(
                    gui.mainFrame, dialog_title, video_list, self,
                    playlist_id_to_update=playlist_id_to_update,
                    new_count_to_update=new_count_to_update
                )
                dialog.Show()
                self._play_success_sound()
            wx.CallAfter(show_dialog)

        except Exception as e:
            log.error("Failed to fetch video list for %s", url, exc_info=True)
            self._notify_error(_("Failed to fetch video list."), log_message=f"Failed to fetch video list for {url}: {e}")
        finally:
            self.is_long_task_running = False
            self._stop_indicator()
    
    def subscribe_to_channel_worker(self, url):
        """Worker to handle subscribing, now correctly handling playlist URLs and tagging content types."""
        ui.message(_("Subscribing to channel..."))
        self._start_indicator()
        self.is_long_task_running = True
        try:
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'playlist_items': '1',
            }
            with self._get_ydl_instance(extra_opts=ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)

            video_info = info['entries'][0] if info.get('_type') == 'playlist' and info.get('entries') else info
            if not video_info:
                raise ValueError("Could not retrieve valid video information from the URL.")

            channel_url = video_info.get('channel_url')
            if not channel_url:
                raise ValueError("Channel URL could not be found from the provided link.")

            db_path = os.path.join(os.path.dirname(__file__), 'subscription.db')
            con = sqlite3.connect(db_path)
            cur = con.cursor()

            cur.execute("SELECT channel_name FROM subscribed_channels WHERE channel_url = ?", (channel_url,))
            existing = cur.fetchone()
            if existing:
                con.close()
                
                def ask_unsubscribe():
                    if wx.MessageBox(
                        _("You are already subscribed to '{channel}'.\nWould you like to unsubscribe instead?").format(channel=existing[0]),
                        _("Already Subscribed"),
                        wx.YES_NO | wx.ICON_QUESTION) == wx.YES:
                        self.unsubscribe_from_channel_worker(channel_url, existing[0])
                
                wx.CallAfter(ask_unsubscribe)
                return

            default_content_types = config.conf["YoutubePlus"].get("contentTypesToFetch", ["videos", "shorts", "streams"])
            
            all_videos = []
            for content_type in default_content_types:
                try:
                    full_url = f"{channel_url.rstrip('/')}/{content_type}"
                    tab_videos = self.get_channel_videos(full_url, channel_name_override=video_info.get('uploader'))
                    if tab_videos:
                        for v in tab_videos:
                            v['content_type'] = content_type
                        all_videos.extend(tab_videos)
                except Exception as e:
                    log.warning("Failed to get videos from %s tab: %s", content_type, e)

            unique_videos = {v['id']: v for v in all_videos if v.get('id')}
            initial_videos = list(unique_videos.values())
            
            channel_name = video_info.get('uploader', 'Unknown Channel')
            content_types_str = ",".join(default_content_types)
            cur.execute("INSERT INTO subscribed_channels (channel_url, channel_name, content_types) VALUES (?, ?, ?)", (channel_url, channel_name, content_types_str))
            
            if initial_videos:
                videos_to_insert = [
                    (v.get('id'), channel_url, channel_name, v.get('title'), v.get('duration_str'), v.get('upload_date'), v.get('content_type', 'videos'))
                    for v in initial_videos
                ]
                cur.executemany("INSERT OR IGNORE INTO videos (video_id, channel_url, channel_name, title, duration_str, upload_date, content_type) VALUES (?, ?, ?, ?, ?, ?, ?)", videos_to_insert)
            
            con.commit()
            con.close()

            new_channel_data = (channel_url, channel_name)
            self._notify_callbacks("subscription_added", new_channel_data)
            self._notify_success(_("Subscribed to {channel}.").format(channel=channel_name))
        except Exception as e:
            self._notify_error(_("Failed to subscribe."), log_message=f"Failed to subscribe to URL {url}: {e}")
        finally:
            self.is_long_task_running = False
            self._stop_indicator()
            
    def unsubscribe_from_channel_worker(self, channel_url, channel_name):
        """Worker to handle unsubscribing from a channel."""
        try:
            db_path = os.path.join(os.path.dirname(__file__), 'subscription.db')
            con = sqlite3.connect(db_path)
            cur = con.cursor()
            
            cur.execute("DELETE FROM subscribed_channels WHERE channel_url = ?", (channel_url,))
            deleted_subs = cur.rowcount
            
            if deleted_subs > 0:
                cur.execute("DELETE FROM videos WHERE channel_url = ?", (channel_url,))
                cur.execute("DELETE FROM seen_videos WHERE video_id NOT IN (SELECT DISTINCT video_id FROM videos WHERE video_id IS NOT NULL)")
                con.commit()
                self._notify_callbacks("subscription_removed", {"channel_url": channel_url})
                self._notify_delete(_("Successfully unsubscribed from {channel}").format(channel=channel_name))
            else:
                self._notify_error(_("Failed to unsubscribe - channel not found in database"))

            con.close()
        except Exception as e:
            self._notify_error(_("Critical error during unsubscribe."), log_message=f"Critical error unsubscribing {channel_url}: {e}")
            
    def _update_subscription_feed_worker(self, progress_topic=None, silent=False):
        """
        Worker to check for new videos and report detailed progress back to the dialog,
        including the final summary message.
        """
        self.is_long_task_running = True
        try:
            if not silent: self._start_indicator()

            db_path = os.path.join(os.path.dirname(__file__), 'subscription.db')
            con = sqlite3.connect(db_path)
            cur = con.cursor()
            
            cur.execute("SELECT video_id FROM videos")
            existing_video_ids = {row[0] for row in cur.fetchall()}
            
            cur.execute("SELECT channel_url, channel_name, content_types FROM subscribed_channels")
            subscribed_channels = cur.fetchall()

            if not subscribed_channels:
                con.close()
                if progress_topic:
                    wx.CallAfter(self._notify_callbacks, progress_topic, {"current": 1, "total": 1, "message": _("No channels to update.")})
                elif not silent:
                    wx.CallAfter(ui.message, _("No channels to update."))
                self._notify_callbacks("subscriptions_updated")
                return

            total_tasks = sum(len(c[2].split(',')) for c in subscribed_channels if c[2])
            current_task = 0
            new_videos_to_cache = []
            
            for channel_url, channel_name, content_types_str in subscribed_channels:
                content_types = content_types_str.split(',') if content_types_str else ["videos", "shorts", "streams"]

                for content_type in content_types:
                    current_task += 1
                    if progress_topic:
                        progress_message = _("Checking {channel} ({type})...").format(channel=channel_name, type=content_type)
                        progress_data = {"current": current_task, "total": total_tasks, "message": progress_message}
                        wx.CallAfter(self._notify_callbacks, progress_topic, progress_data)

                    try:
                        latest_videos = self.get_channel_videos(f"{channel_url}/{content_type}")
                        if latest_videos:
                            for video in latest_videos:
                                video_id = video.get('id')
                                if video_id and video_id not in existing_video_ids:
                                    new_videos_to_cache.append((
                                        video_id, channel_url, channel_name,
                                        video.get('title'), video.get('duration_str'), 
                                        video.get('upload_date'), content_type
                                    ))
                                    existing_video_ids.add(video_id)
                    except Exception as e:
                        log.warning("Could not update %s for %s: %s", content_type, channel_name, e)

            if new_videos_to_cache:
                cur.executemany("""
                    INSERT OR IGNORE INTO videos (video_id, channel_url, channel_name, title, duration_str, upload_date, content_type) 
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, new_videos_to_cache)
                con.commit()
            
            con.close()
            
            if progress_topic:
                final_message = _("Update complete. Found {count} new videos.").format(count=len(new_videos_to_cache))
                final_data = {"current": total_tasks, "total": total_tasks, "message": final_message}
                wx.CallAfter(self._notify_callbacks, progress_topic, final_data)
            elif not silent:
                if len(new_videos_to_cache) > 0:
                    wx.CallAfter(ui.message, _("Found and added {count} new videos.").format(count=len(new_videos_to_cache)))
                else:
                    wx.CallAfter(ui.message, _("No new videos found."))
            self._notify_callbacks("subscriptions_updated")

        except Exception as e:
            log.error("Error updating subscription feed.", exc_info=True)
            if progress_topic:
                 wx.CallAfter(self._notify_callbacks, progress_topic, {"message": _("Error updating feed."), "current": 1, "total": 1})
        finally:
            self.is_long_task_running = False
            if not silent: self._stop_indicator()
            
    def _download_choice_worker(self, url):
        clean_url = self._validate_video_url_and_notify(url)
        if not clean_url:
            return
        self._start_indicator()
        try:
            self.is_long_task_running = True
            info = self.get_video_info(url)
            title = info.get('title', 'Unknown Video')
            duration = self._format_duration_verbose(info.get('duration', 0))
            wx.CallAfter(self._show_download_dialog, url, title, duration)
        except Exception as e:  
            log.error("Could not get video info for download. Error: %s", e, exc_info=True)
            wx.CallAfter(ui.message, _("Failed to get video info for download."))
            self._stop_indicator()
        finally:
            self.is_long_task_running = False

    def _direct_download_worker(self, url, choice):
        ui.message(_("Getting video info for download..."))
        self._start_indicator()
        try:
            self.is_long_task_running = True
            info = self.get_video_info(url)
            title = info.get('title', 'Unknown Video')
            self._perform_download_worker(url, choice, title)
        except Exception as e:
            log.error("Failed to initiate direct download for %s", url, exc_info=True)
            wx.CallAfter(ui.message, _("Failed to start download: {error}").format(error=e))
        finally:
            self.is_long_task_running = False
            
    def _show_download_dialog(self, url, title, duration):
        self._pause_indicator()
        
        dlg = wx.MessageDialog(gui.mainFrame, _("What would you like to download?"),
                                _("Download: {title} ({duration})").format(title=title, duration=duration),
                                wx.YES_NO | wx.CANCEL | wx.ICON_QUESTION)
        dlg.SetYesNoCancelLabels(_("Download &Video"), _("Download &Audio"), _("Ca&ncel"))
        result = dlg.ShowModal()
        dlg.Destroy()
        
        choice = None
        if result == wx.ID_YES:
            choice = 'video'
        elif result == wx.ID_NO:
            choice = 'audio'
        
        if choice:
            self._resume_indicator()
            threading.Thread(target=self._perform_download_worker, args=(url, choice, title, ), daemon=True).start()
        else:
            self._stop_indicator()

    def _perform_download_worker(self, url, choice, title):
        wx.CallAfter(ui.message, _("Starting download of {title}...").format(title=title))
        try:
            self.is_long_task_running = True
            save_path = config.conf["YoutubePlus"].get("exportPath", "") or os.path.join(os.path.expanduser("~"), "Desktop")
            output_template = os.path.join(save_path, '%(title)s.%(ext)s')
            
            if not os.path.exists(save_path):
                os.makedirs(save_path)

            opts = {}
            if choice == 'video':
                opts['format'] = 'best[ext=mp4]/best[ext=webm]/best'
                opts['outtmpl'] = output_template
            elif choice == 'audio':
                opts['format'] = 'bestaudio[acodec=aac]/140/bestaudio[ext=m4a]/bestaudio'
                opts['outtmpl'] = output_template

            try:
                with self._get_ydl_instance(extra_opts=opts) as ydl:
                    ydl.download([url])
                self._notify_success(_("Download complete: {title}").format(title=title))

            except DownloadError as e:
                if "Requested format is not available" in str(e) and choice == 'audio':
                    wx.CallAfter(ui.message, _("Audio-only format not found. Attempting to download a video file with audio instead..."))
                    log.warning("Audio-only format not found. Falling back to video format 18.")
                    
                    fallback_opts = opts.copy()
                    fallback_opts['format'] = '18' # เปลี่ยน format เป็น 18 (mp4 360p)
                    
                    with self._get_ydl_instance(extra_opts=fallback_opts) as ydl:
                        ydl.download([url])
                    self._notify_success(_("Download complete (as MP4 video file): {title}").format(title=title))
                else:
                    raise e

        except DownloadError as e:
            self._notify_error(_("Download failed."), log_message=f"Download failed for {title}: {e}")
        except Exception as e:
            self._notify_error(_("Download failed."), log_message=f"Download failed for {title}: {e}")
        finally:
            self.is_long_task_running = False
            self._stop_indicator()
            
    def _Youtube_worker(self, query, count, source_dialog):
        """
        A simplified worker that takes a raw query and the desired number of results.
        """
        ui.message(_("Searching for '{query}'...").format(query=query))
        self._start_indicator()
        self.is_long_task_running = True
        try:
            opts = {'quiet': True, 'no_warnings': True, 'extract_flat': 'in_playlist'}
            search_prefix = f"ytsearch{count}:{query}"

            with self._get_ydl_instance(extra_opts=opts) as ydl:
                info = ydl.extract_info(search_prefix, download=False)

            results_list = []
            if 'entries' in info:
                for entry in info.get('entries', []):
                    if entry and entry.get('id'):
                        item = {
                            'id': entry.get('id'),
                            'title': entry.get('title', 'N/A'),
                            'duration_str': self._format_duration_verbose(entry.get('duration', 0)),
                            'channel_name': entry.get('channel'),
                            'channel_url': entry.get('channel_url')
                        }
                        _type = entry.get('_type')
                        if _type == 'channel':
                            item['duration_str'] = _("Channel")
                        elif _type == 'playlist':
                            item['duration_str'] = _("Playlist ({count})").format(count=entry.get('playlist_count', 0))
                        results_list.append(item)
            
            if not results_list:
                wx.CallAfter(ui.message, _("No results found for '{query}'.").format(query=query))
            else:
                dialog_title = _("Search Results for '{query}'").format(query=query)
                wx.CallAfter(self._show_search_results, results_list, dialog_title, source_dialog)

        except Exception as e:
            log.error("Failed to perform Youtube for '%s'", query, exc_info=True)
            wx.CallAfter(ui.message, _("Failed to perform search."))
        finally:
            self.is_long_task_running = False
            self._stop_indicator()
            
    def openMessagesDialog(self):
        gui.mainFrame.prePopup()
        dialog_title = _("Live chat of {title}").format(title=self.video_title) if self.active else _("Live chat (stopped)")
        self.dialog = MessagesDialog(gui.mainFrame, dialog_title, self)
        self.dialog.Show()
        self._play_success_sound()
        gui.mainFrame.postPopup()

    def _finish_chat_setup(self, video_id, title):
        """Finalizes chat setup on the main thread and starts the worker."""
        #log.info("Finishing chat setup for video ID: %s", video_id)
        try:
            self.chat = pytchat.create(video_id=video_id)
            if not self.chat.is_alive():
                raise RuntimeError("Chat is not active on this video (pytchat check).")
            self.video_title = title
            self.active = True
            with self._messages_lock:
                self.messages = []
            self.first_chat_message_spoken = False
            self._stop_event.clear()
            self._worker_thread = threading.Thread(target=self._chat_monitor_worker, args=(self.chat,), daemon=True)
            self._worker_thread.start()
        except Exception as e:
            self._stop_indicator()
            log.exception("Failed to finalize chat setup.")
            wx.CallAfter(ui.message, f"Could not receive live chat. {e}")
            self.stopChatMonitoring(silent=True)

    def stopChatMonitoring(self, silent=False):
        if not self.active and self._worker_thread is None:
            if not silent: ui.message("Chat monitoring is not active.")
            return
        #log.info("Stopping chat monitoring...")
        self._stop_event.set() # Signal the thread to stop
        if self.chat:
            self.chat.terminate()
        
        if self._worker_thread and self._worker_thread.is_alive():
            # The thread will exit quickly due to the responsive sleep. A short join is fine.
            self._worker_thread.join(timeout=2.0)

        if not silent:
            ui.message("Chat monitoring stopped.")
        if self.messages:
            wx.CallAfter(self._export_chat)
        # Reset state
        self.active = False
        self._worker_thread = None
        self.chat = None
        self.last_message_index = -1
        # No need to clear self.messages here, so users can review the chat after stopping.
        
        if MessagesDialog._instance:
            wx.CallAfter(MessagesDialog._instance.SetTitle, _("Live chat of {title} (stopped)").format(title=self.video_title))

    def show_comments_dialog(self, title, comments_data, is_replay_data=False):
        gui.mainFrame.prePopup()
        # The CommentsDialog is self-contained after receiving the data.
        dialog = CommentsDialog(gui.mainFrame, title, comments_data, is_replay_data)
        dialog.Show()
        self._play_success_sound()
        gui.mainFrame.postPopup()

    def _show_subscription_feed_directly(self):
        """Directly shows the new tabbed subscription feed dialog."""
        #log.critical("!!! _show_subscription_feed_directly was called. This is the trigger for SubDialog to appear. !!!")
        try:
            db_path = os.path.join(os.path.dirname(__file__), 'subscription.db')
            con = sqlite3.connect(db_path)
            cur = con.cursor()

            cur.execute("SELECT COUNT(*) FROM subscribed_channels")
            if cur.fetchone()[0] == 0:
                con.close()
                ui.message(_("You haven't subscribed to any channels yet."))
                return
            
            con.close()
            
            gui.mainFrame.prePopup()
            dialog = SubDialog(gui.mainFrame, self)
            dialog.Show()
            gui.mainFrame.postPopup()

        except Exception as e:
            log.exception("Failed to load subscription feed from database.")
            ui.message(_("Error loading subscription feed from database."))

    def _show_search_results(self, results_list, title, parent_dialog):
        """Creates and shows the search results dialog with the correct parent."""
        gui.mainFrame.prePopup()
        dialog = ChannelVideoDialog(parent_dialog, title, results_list, self)
        dialog.ShowModal()
        dialog.Destroy()
        gui.mainFrame.postPopup()

    def clear_all_user_data(self):
        """Deletes all user-generated files and database tables."""
        log.debug("--- Starting deletion of all user data ---")
        try:
            addon_dir = os.path.dirname(__file__)
            
            files_to_delete = ['fav_video.json', 'fav_channel.json', 'subscription.db']
            for filename in files_to_delete:
                file_path = os.path.join(addon_dir, filename)
                if os.path.exists(file_path):
                    os.remove(file_path)
                    log.debug("Deleted file: %s", filename)
            
            # --- Re-initialize the database (creates a new, empty one) ---
            self._init_sub_database()
            
            wx.CallAfter(ui.message, _("All favorite and subscription data has been cleared."))
            log.debug("--- User data deletion complete ---")

        except Exception as e:
            log.exception("An error occurred while clearing user data.")
            wx.CallAfter(ui.message, _("An error occurred while clearing data. Please check the log."))
    
    def prune_all_videos_worker(self):
            """Worker to delete ALL videos from the database after confirmation."""
            confirm_msg = _("This will permanently delete ALL videos from your subscription feed, leaving only the list of subscribed channels. This action cannot be undone.\n\nAre you sure you want to continue?")
            
            def ask_confirmation():
                confirm = wx.MessageBox(confirm_msg, _("Confirm Clearing All Videos"), wx.YES_NO | wx.ICON_EXCLAMATION)
                if confirm != wx.YES:
                    return
                
                ui.message(_("Clearing all feed videos..."))
                threading.Thread(target=self._execute_pruning_all, daemon=True).start()
            wx.CallAfter(ask_confirmation)

    def _execute_pruning_all(self):
            """The actual database deletion part for clearing ALL videos."""
            try:
                db_path = os.path.join(os.path.dirname(__file__), 'subscription.db')
                con = sqlite3.connect(db_path)
                cur = con.cursor()
                
                cur.execute("DELETE FROM videos")
                rows_deleted = cur.rowcount
                
                con.commit()
                con.close()
                
                self.core._notify_delete(_("Clearing complete. All {count} videos were deleted.").format(count=rows_deleted))
                self._notify_callbacks("subscriptions_updated")

            except Exception as e:
                log.error("Failed to prune all videos from database.", exc_info=True)
                wx.CallAfter(ui.message, _("An error occurred while clearing all videos."))

    @script(description=_("an YoutubePlus layer commands."),
    gesture="kb:NVDA+y")
    def script_YoutubePlusLayer(self, gesture):
        if self.toggling:
            self.handle_error(gesture)
            return
        self.bindGestures(self.__YoutubePlusGestures)
        self.toggling = True
        self._notify_layer_activated()
        
    @script(description="Show Live chat or Comments / live chat Replay from current page or clipboard URL.")
    def script_getData(self, gesture):
        #log.info("Script triggered: getData")
        messy_url = self._find_youtube_url()
        if not messy_url:
            return ui.message("YouTube URL not found in current window or clipboard.")
        
        url = self._clean_youtube_url(messy_url)
        #ui.message(f"getting info...")
        threading.Thread(target=self._unified_worker, args=(url,), daemon=True).start()

    @script(description="Show video info from current page or clipboard URL.")
    def script_getInfo(self, gesture):
        #log.info("Script triggered: getInfo")
        messy_url = self._find_youtube_url()
        if not messy_url:
            return ui.message("YouTube URL not found in current window or clipboard.")
        
        url = self._clean_youtube_url(messy_url)
        ui.message(_("Getting video info..."))
        threading.Thread(target=self._get_info_worker, args=(url, ), daemon=True).start()

    @script(description="Show video chapters/timestamps from current page or clipboard URL.")
    def script_showChapters(self, gesture):
        #log.info("Script triggered: showChapters")
        messy_url = self._find_youtube_url()
        if not messy_url:
            return ui.message("YouTube URL not found in current window or clipboard.")
        
        url = self._clean_youtube_url(messy_url)
        ui.message(_("Getting chapters..."))
        threading.Thread(target=self._show_chapters_worker, args=(url, ), daemon=True).start()

    @script(description="Download video or audio from current page or clipboard URL.")
    def script_downloadClip(self, gesture):
        #log.info("Script triggered: downloadClip")
        messy_url = self._find_youtube_url()
        if not messy_url:
            return ui.message("YouTube URL not found in current window or clipboard.")
        
        url = self._clean_youtube_url(messy_url)
        ui.message(_("Getting video info for download..."))
        threading.Thread(target=self._download_choice_worker, args=(url, ), daemon=True).start()

    @script(description="Show help dialog.")
    def script_displayHelp(self, gesture):
        #log.info("Script triggered: displayHelp")
        gui.mainFrame.prePopup()
        dialog = HelpDialog(gui.mainFrame, "Help", self.help_text)
        dialog.Show()
        gui.mainFrame.postPopup()

    @script(description="Stop live chat monitoring.")
    def script_stopMonitor(self, gesture):
        #log.info("Script triggered: stopMonitor")
        self.stopChatMonitoring()

    @script(description="Show live chat messages  dialog.")
    def script_showMessagesDialog(self, gesture):
        #log.info("Script triggered: showMessagesDialog")
        if not self.active:
            ui.message("No stream is currently being monitored.")
            return
        self.openMessagesDialog()

    @script(description="Toggle automatic speaking of incoming messages from live chat monitroring.")
    def script_toggleAutoSpeak(self, gesture):
        #log.info("Script triggered: toggleAutoSpeak")
        is_enabled = not config.conf["YoutubePlus"].get("autoSpeak", True)
        config.conf["YoutubePlus"]["autoSpeak"] = is_enabled
        ui.message("Automatic message speaking enabled." if is_enabled else "Automatic message speaking disabled.")        

    @script(description=_("Show favorite videos dialog."))
    def script_showFavVideoDialog(self, gesture):
        #log.info("Script triggered: showFavVideoDialog")
        gui.mainFrame.prePopup()
        dialog = FavsDialog(gui.mainFrame, self, 0)
        dialog.Show()
        gui.mainFrame.postPopup()
    
    @script(description=_("Show favorite channels dialog."))
    def script_showFavChannelDialog(self, gesture):
        #log.info("Script triggered: showFavChannelDialog")
        gui.mainFrame.prePopup()
        dialog = FavsDialog(gui.mainFrame, self, 1)
        dialog.Show()
        gui.mainFrame.postPopup()
        
    @script(description=_("Show favorite playlists dialog."))
    def script_showFavPlaylistDialog(self, gesture):
        #log.info("Script triggered: showFavPlaylistDialog")
        gui.mainFrame.prePopup()
        dialog = FavsDialog(gui.mainFrame, self, 2)
        dialog.Show()
        gui.mainFrame.postPopup()
    
    @script(description=_("Show a menu to add the current page URL to favorites or subscriptions."))
    def script_showAddMenu(self, gesture):
        #log.info("Script triggered: showAddMenu")
        url = self._find_youtube_url()
        if not url:
            ui.message(_("No specific YouTube URL found in the current window or clipboard."))
            return
        gui.mainFrame.prePopup()
        try:
            temp_frame = wx.Frame(gui.mainFrame, -1, "AddMenu Host", size=(1,1), pos=(-100,-100))
            temp_frame.Show()

            menu = wx.Menu()
            
            self.add_menu_choices = {
                wx.ID_HIGHEST + 10: (_("Add to Favorite &Videos"), lambda: self._on_add_to_video_fav(url)),
                wx.ID_HIGHEST + 11: (_("Add to Favorite &Channels"), lambda: self._on_add_to_channel_fav(url)),
                wx.ID_HIGHEST + 12: (_("Add to Favorite &playlist"), lambda: self._on_add_to_playlist_fav(url)),
                wx.ID_HIGHEST + 13: (_("&Subscribe to Channel"), lambda: self._on_subscribe_to_channel(url)),
                wx.ID_HIGHEST + 14: (_("add to &Watch list"), lambda: self._on_add_to_watchList(url)),
            }
            self._add_menu_handlers = {id: handler for id, (label, handler) in self.add_menu_choices.items()}

            for menu_id, (label, handler) in self.add_menu_choices.items():
                menu.Append(menu_id, label)

            temp_frame.Bind(wx.EVT_MENU, self._on_add_menu_select)
            temp_frame.Bind(wx.EVT_MENU_CLOSE, lambda evt: wx.CallAfter(temp_frame.Destroy))

            wx.CallAfter(temp_frame.PopupMenu, menu)

        finally:
            gui.mainFrame.postPopup()
            
    def _on_add_menu_select(self, event):
        """Handles the selection from the 'Add' context menu."""
        menu_id = event.GetId()
        label, handler = self.add_menu_choices.get(menu_id)
        
        if handler:
            handler()

    def _on_add_to_video_fav(self, url):
        """Starts the worker to add the URL to video favorites."""
        #log.info("Menu selection: Add to Favorite Videos")
        threading.Thread(target=self.add_item_to_favorites_worker, args=(url,), daemon=True).start()
        
    def _on_add_to_channel_fav(self, url):
        """Starts the worker to add the URL to channel favorites."""
        #log.info("Menu selection: Add to Favorite Channels")
        threading.Thread(target=self.add_channel_to_favorites_worker, args=(url,), daemon=True).start()
        
    def _on_add_to_playlist_fav(self, url):
        """Starts the worker to add the URL to playlist favorites."""
        #log.info("Menu selection: Add to Favorite playlist")
        threading.Thread(target=self.add_playlist_to_favorites_worker, args=(url,), daemon=True).start()

    def _on_subscribe_to_channel(self, url):
        """Starts the worker for subscribing to a channel."""
        #log.info("Menu selection: Subscribe to Channel")
        threading.Thread(target=self.subscribe_to_channel_worker, args=(url,), daemon=True).start()
        
    def _on_add_to_watchList(self, url):
        """Starts the worker to add the URL to watch list."""
        #log.info("Menu selection: Add to watch list")
        threading.Thread(target=self.add_to_watchlist_worker, args=(url,), daemon=True).start()

    @script(description=_("Show subscription feed dialog."))
    def script_showSubDialog(self, gesture):
        #log.info("Script triggered: showSubDialog")
        wx.CallAfter(self._show_subscription_feed_directly)

    @script(description=_("Search YouTube for videos, channels, or playlists."))
    def script_showSearchDialog(self, gesture):
        gui.mainFrame.prePopup()
        dialog = SearchDialog(gui.mainFrame, self)
        dialog.Show()
        gui.mainFrame.postPopup()

    @script(description=_("Show manage subscriptions dialog."))
    def script_showManageSubDialog(self, gesture):
        #log.info("Script triggered: showManageSubDialog")
        gui.mainFrame.prePopup()
        dialog = ManageSubscriptionsDialog(gui.mainFrame, self)
        dialog.Show()
        gui.mainFrame.postPopup()

    def add_to_watchlist_worker(self, url, mark_seen=False):
        self._start_indicator()
        try:
            info = self.get_video_info(url)
            if not info:
                return
            
            video_id = info.get('id')
            title = info.get('title')
            file_path = os.path.join(os.path.dirname(__file__), 'watch_list.json')
            
            with self._fav_file_lock:
                watchlist = []
                if os.path.exists(file_path):
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            watchlist = json.load(f)
                    except (json.JSONDecodeError, TypeError):
                        watchlist = []
                
                if any(item.get('video_id') == video_id for item in watchlist):
                    ui.message(_("'{title}' is already in Watch List.").format(title=title))
                else:
                    new_item = {
                        "video_id": video_id, 
                        "title": title, 
                        "channel_name": info.get('uploader'),
                        "duration_str": self._format_duration_verbose(info.get('duration', 0)),
                        "added_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    }
                    watchlist.append(new_item)
                    with open(file_path, 'w', encoding='utf-8') as f:
                        json.dump(watchlist, f, indent=2, ensure_ascii=False)
                    self._notify_success(_("Added '{title}' to watch list.").format(title=new_item['title']))
            if mark_seen:
                self.mark_videos_as_seen(video_id, notify=True)
            else:
                self._notify_callbacks("watch_list_updated")
        except Exception as e:
            log.error(f"Add to watchlist worker error: {e}")
            ui.message(_("Error: Could not add video to Watch List."))
        finally:
            self._stop_indicator()
    
    def mark_videos_as_seen(self, video_ids, notify=True):
        """
        Mark one or multiple videos as seen in the database.
        video_ids: can be a string (single ID) or a list of strings.
        """
        if isinstance(video_ids, str):
            video_ids = [video_ids]
            
        if not video_ids:
            return

        try:
            db_path = os.path.join(os.path.dirname(__file__), 'subscription.db')
            with sqlite3.connect(db_path) as con:
                con.executemany(
                    "INSERT OR IGNORE INTO seen_videos (video_id) VALUES (?)",
                    [(vid,) for vid in video_ids]
                )
            
            if notify:
                self._notify_callbacks("subscriptions_updated")
            return True
        except Exception as e:
            log.error(f"Error marking videos as seen: {e}")
            return False
            
    @script(description=_("Show watch list dialog."))
    def script_showWatchListDialog(self, gesture):
        #log.info("Script triggered: showWatchListDialog")
        gui.mainFrame.prePopup()
        dialog = FavsDialog(gui.mainFrame, self, 3)
        dialog.Show()
        gui.mainFrame.postPopup()
    
    
    __YoutubePlusGestures = {
        "kb:a": "showAddMenu",
        "kb:f": "showFavVideoDialog",
        "kb:c": "showFavChannelDialog",
        "kb:p": "showFavPlaylistDialog",
        "kb:w": "showWatchListDialog",
        "kb:d": "downloadClip",
        "kb:e": "showSearchDialog",
        "kb:i": "getInfo",
        "kb:t": "showChapters",
        "kb:m": "showManageSubDialog",
        "kb:s": "showSubDialog",
        "kb:l": "getData",
        "kb:shift+l": "stopMonitor",
        "kb:r": "toggleAutoSpeak",
        "kb:v": "showMessagesDialog",
        "kb:h": "displayHelp"
    }
    