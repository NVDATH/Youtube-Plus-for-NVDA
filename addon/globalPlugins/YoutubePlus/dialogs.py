# -*- coding: utf-8 -*-
# dialogs.py for YoutubePlus NVDA Addon
# Copyright (C) 2025
# This file is covered by the GNU General Public License.
# You can read the licence by clicking Help->Licence in the NVDA menu
# or by visiting http://www.gnu.org/licenses/old-licenses/gpl-2.0.html
# Shortcut: Windows+y

import wx
import wx.lib.mixins.listctrl as listmix
import ui
import gui
import config
import os
import re
import unicodedata
import webbrowser
import addonHandler
import api
from functools import wraps
import json
import threading 
import controlTypes 
import sqlite3
from logHandler import log
import shutil
import globalVars
import globalCommands

# Initialize translations for this file
addonHandler.initTranslation()

def copy_to_clipboard(text):
    api.copyToClip(text)

confspec = {
    "activeProfile": "string(default='default')",
    "quickAction": "string(default='open_video')", 
    "progressIndicatorMode": "string(default='beep')",
    "sortOrder": "string(default='newest')",
    "playlist_fetch_count": "integer(default=20, min=5, max=100)",
    "contentTypesToFetch": "string_list(default=list('videos', 'shorts', 'streams'))",
    "autoUpdateIntervalMinutes": "integer(default=0)",
    "autoSpeak": "boolean(default=True)",
    "refreshInteval": "integer(default=5, min=1, max=60)",
    "messageLimit": "integer(default=5000, min=100, max=20000)",
    #"cookieFilePath": "string(default='')",
    "cookieMode": "string(default='none')",
    "exportPath": "string()",
    "subDialogViewMode": "string(default='unseen')",
    "searchResultCount": "integer(default=20, min=5, max=100)",
    "favVideoLastCatId": "string(default='__default__')",
    "watchListLastCatId": "string(default='__default__')",
}
config.conf.spec["YoutubePlus"] = confspec

def sanitize_filename(filename):
    filename = unicodedata.normalize('NFC', filename)
    allowed_pattern = r'[^a-zA-Z0-9\u0E00-\u0E7F \-\.]'
    sanitized = re.sub(allowed_pattern, ' ', filename)
    sanitized = re.sub(r'\s+', ' ', sanitized).strip()
    return sanitized

class BaseDialogMixin:
    """A mixin to provide common dialog functionality."""
    _escape_protection = False

    def on_char_hook(self, event):
        key = event.GetKeyCode()
        ctrl = event.ControlDown()
        if ctrl and key == ord('W'):
            self.Close()
            return
        if key == wx.WXK_ESCAPE:
            if self._escape_protection:
                if getattr(self, '_escape_pending', False):
                    self._escape_pending = False
                    self.Close()
                else:
                    self._escape_pending = True
                    # Translators: Message shown when user presses Escape once in a protected dialog.
                    ui.message(_("Press Escape again to close."))
            else:
                self.Close()
            return
        self._escape_pending = False
        event.Skip()
        
    
class BaseInfoDialog(BaseDialogMixin, wx.Dialog):
    """A base dialog for showing read-only text content."""
    
    def __init__(self, parent, title, text_content):
        super().__init__(parent, title=title)
        panel = wx.Panel(self)
        mainSizer = wx.BoxSizer(wx.VERTICAL)
        textCtrl = wx.TextCtrl(panel, value=text_content, style=wx.TE_MULTILINE | wx.TE_READONLY)
        mainSizer.Add(textCtrl, 1, wx.EXPAND | wx.ALL, 10)
        # Translators: The label of the button to close the information dialog.
        closeBtn = wx.Button(panel, label=_("C&lose"))
        closeBtn.Bind(wx.EVT_BUTTON, lambda e: self.Close())
        btnSizer = wx.BoxSizer(wx.HORIZONTAL)
        btnSizer.Add(closeBtn, 0, wx.ALIGN_CENTER)
        mainSizer.Add(btnSizer, 0, wx.ALIGN_CENTER | wx.BOTTOM, 10)
        panel.SetSizer(mainSizer)
        self.SetSize((600, 400))
        self.CentreOnScreen()
        self.Bind(wx.EVT_CLOSE, self.onClose)
        self.Bind(wx.EVT_CHAR_HOOK, self.on_char_hook) # Bind to the mixin's method

    def onClose(self, event):
        self.Destroy()
        
class HelpDialog(BaseInfoDialog):
    """Dialog to show help text, inherits from BaseInfoDialog."""
    
    def __init__(self, parent):
        # Translators: Title of the YoutubePlus help dialog.
        title = _("YouTubePlus Help & Shortcuts")
        help_text = self.get_help_text()
        super(HelpDialog, self).__init__(parent, title, help_text)

    @staticmethod
    def get_help_text():
        # Translators: Detailed help text containing keyboard shortcuts and layer commands for YouTubePlus.
        # Please preserve the layout, dashes, and line breaks for readability.
        return _("""YouTubePlus Layer Commands (Press NVDA+Y to activate)

--- Core Actions (from a YouTube window/URL) ---
- L: Get comments from the current URL (Live Chat, Replay, or Comments)
- I: Get video info
- T: Show video chapters/timestamps
- D: Download video/audio from the current URL
- B: download sub title from the current URL
- E: Search YouTube
- Q: Quick search — searches immediately using selected text or clipboard content, no dialog
- Control+H: Open Favorites window on the Search History tab

--- Favorites & Subscriptions ---
- A: Show the "Add to..." menu (for favorites/subscriptions)
- F: Show favorite videos dialog
- C: Show favorite channels dialog
- P: Show favorite playlists dialog
- W: Show watch list dialog
- S: Show subscription feed dialog
- M: Show Manage Subscriptions dialog
- U: Show User Profile Manager Dialog

--- Live Chat Monitoring (while active) ---
- Shift+L: Stop live chat monitoring
- V: Show live chat messages dialog
- R: Toggle automatic speaking of incoming messages
- Y: open YoutubePlus settings dialog

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

**In any Favorites Dialog (Videos, Channels, Playlists, Watch list):**
- Delete: Remove the selected item from favorites
- F2: rename item
- Control+c / control+x > control+v : copy or cut then paste item to move position, supports multiple selection and moving items between the Video and Watch List tabs
- Alt+O: Open the Sort dialog for the current tab (sort by field, optionally limited to the current category, optionally saved permanently)

**In the Video and Watch List tabs (category tree, left side):**
- Control+=: Add a new category
- F2: Rename the selected category
- Delete: Remove the selected category (asks whether to move or delete its items)
- Control+Shift+Up / Control+Shift+Down: Reorder the selected category
- Application/Menu key or right-click: Category context menu on the tree, video Action menu on the item list

--- Help ---
- H: Show this help dialog
""")

class InfoDialog(BaseInfoDialog):
    """Dialog to show video info, inherits from BaseInfoDialog."""
    _escape_protection = True   
    
    def __init__(self, parent, title, info_text):
        super(InfoDialog, self).__init__(parent, title, info_text)

class MessagesListCtrl(wx.ListCtrl, listmix.ListCtrlAutoWidthMixin):
    def __init__(self, parent):
        wx.ListCtrl.__init__(self, parent, style=wx.LC_REPORT | wx.LC_SINGLE_SEL | wx.BORDER_SUNKEN)
        listmix.ListCtrlAutoWidthMixin.__init__(self)
        # Translators: The header for the author column in a list of messages.
        self.InsertColumn(0, _("Author"), width=200)
        # Translators: The header for the message content column in a list of messages.
        self.InsertColumn(1, _("Message"), width=350)
        # Translators: The header for the time column indicating when the message was sent.
        self.InsertColumn(2, _("Time"), width=150)

class CommentsListCtrl(wx.ListCtrl, listmix.ListCtrlAutoWidthMixin):
    def __init__(self, parent):
        wx.ListCtrl.__init__(self, parent, style=wx.LC_REPORT | wx.LC_SINGLE_SEL | wx.BORDER_SUNKEN)
        listmix.ListCtrlAutoWidthMixin.__init__(self)
        # Translators: The header for the author column in a list of comments.
        self.InsertColumn(0, _("Author"), width=200)
        # Translators: The header for the message content column in a list of comments.
        self.InsertColumn(1, _("Message"), width=350)
        # Translators: The header for the time column indicating when the comment was sent.
        self.InsertColumn(2, _("Time"), width=150)

class TimestampDialog(BaseDialogMixin, wx.Dialog):
    _escape_protection = True   

    def __init__(self, parent, title, chapters_data, video_url):
        super().__init__(parent, title=title)
        self.chapters = chapters_data
        self.filtered_chapters = self.chapters[:]
        self.base_video_url = video_url.split('&')[0]

        panel = wx.Panel(self)
        mainSizer = wx.BoxSizer(wx.VERTICAL)

        searchSizer = wx.BoxSizer(wx.HORIZONTAL)
        # Translators: Label for the search box in Timestamp dialog.
        searchLabel = wx.StaticText(panel, label=_("&Search:"))
        self.searchTextCtrl = wx.TextCtrl(panel, style=wx.TE_PROCESS_ENTER)
        searchSizer.Add(searchLabel, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 5)
        searchSizer.Add(self.searchTextCtrl, 1, wx.EXPAND)
        mainSizer.Add(searchSizer, 0, wx.EXPAND | wx.ALL, 5)

        self.listCtrl = wx.ListCtrl(panel, style=wx.LC_REPORT | wx.LC_SINGLE_SEL)
        # Translators: Column header for chapter titles.
        self.listCtrl.InsertColumn(0, _("Title"), width=500)
        # Translators: Column header for chapter start times.
        self.listCtrl.InsertColumn(1, _("Time"), width=100)
        mainSizer.Add(self.listCtrl, 1, wx.EXPAND | wx.ALL, 10)
        
        self.currentTextElement = wx.TextCtrl(panel, style=wx.TE_MULTILINE | wx.TE_READONLY)
        mainSizer.Add(self.currentTextElement, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 10)

        btnSizer = wx.BoxSizer(wx.HORIZONTAL)
        # Translators: Button to open the selected chapter in a browser.
        self.openBtn = wx.Button(panel, label=_("&Open Chapter"))
        # Translators: Button to copy the chapter title to clipboard.
        self.copyTitleBtn = wx.Button(panel, label=_("&Copy Title"))
        # Translators: Button to copy the chapter URL with timestamp to clipboard.
        self.copyUrlBtn = wx.Button(panel, label=_("Copy &URL"))
        # Translators: Button to export all chapters to a text file.
        self.exportBtn = wx.Button(panel, label=_("&Export"))
        # Translators: Button to close the dialog.
        self.closeBtn = wx.Button(panel, label=_("C&lose"))
        
        btnSizer.Add(self.openBtn, 0, wx.RIGHT, 5)
        btnSizer.Add(self.copyTitleBtn, 0, wx.RIGHT, 5)
        btnSizer.Add(self.copyUrlBtn, 0, wx.RIGHT, 5)
        btnSizer.Add(self.exportBtn, 0, wx.RIGHT, 5)
        btnSizer.Add(self.closeBtn, 0)
        mainSizer.Add(btnSizer, 0, wx.ALIGN_CENTER | wx.BOTTOM, 10)

        panel.SetSizer(mainSizer)
        self.SetSize((700, 500))
        self.CentreOnScreen()
        
        self.populate_list()
        self.searchTextCtrl.Bind(wx.EVT_TEXT, self.on_search)
        self.listCtrl.Bind(wx.EVT_KEY_DOWN, self.on_key_down)
        self.listCtrl.Bind(wx.EVT_LIST_ITEM_SELECTED, self.on_list_item_selected)
        self.listCtrl.Bind(wx.EVT_LIST_ITEM_DESELECTED, self.on_list_item_selected)
        self.openBtn.Bind(wx.EVT_BUTTON, self.on_open)
        self.copyTitleBtn.Bind(wx.EVT_BUTTON, self.on_copy_text)
        self.copyUrlBtn.Bind(wx.EVT_BUTTON, self.on_copy_url)
        self.exportBtn.Bind(wx.EVT_BUTTON, self.on_export)
        self.closeBtn.Bind(wx.EVT_BUTTON, lambda e: self.Close())
        self.Bind(wx.EVT_CLOSE, lambda e: self.Destroy())
        self.Bind(wx.EVT_CHAR_HOOK, self.on_char_hook)
        
        wx.CallAfter(self.listCtrl.SetFocus)     
   
    def on_list_item_selected(self, event):
        selected_index = self.listCtrl.GetFirstSelected()
        if selected_index != -1:
            title_str = self.listCtrl.GetItemText(selected_index, 0)
            time_str = self.listCtrl.GetItemText(selected_index, 1)
            self.currentTextElement.SetValue("{time} - {title}".format(time=time_str, title=title_str))
        else:
            self.currentTextElement.SetValue("")

    def populate_list(self):
        self.listCtrl.Freeze()
        self.listCtrl.DeleteAllItems()
        for chapter in self.filtered_chapters:
            start_seconds = int(chapter.get('start_time', 0))
            minutes, seconds = divmod(start_seconds, 60)
            hours, minutes = divmod(minutes, 60)
            time_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
            list_index = self.listCtrl.InsertItem(self.listCtrl.GetItemCount(), chapter.get('title', ''))
            self.listCtrl.SetItem(list_index, 1, time_str)
            self.listCtrl.SetItemData(list_index, start_seconds)
        self.listCtrl.Thaw()
        if self.listCtrl.GetItemCount() > 0:
            self.listCtrl.SetItemState(0, wx.LIST_STATE_SELECTED | wx.LIST_STATE_FOCUSED, wx.LIST_STATE_SELECTED | wx.LIST_STATE_FOCUSED)
            self.listCtrl.EnsureVisible(0)
            self.on_list_item_selected(None)

    def on_search(self, event):
        search_text = self.searchTextCtrl.GetValue().lower()
        if search_text:
            self.filtered_chapters = [ch for ch in self.chapters if search_text in ch.get('title', '').lower()]
        else:
            self.filtered_chapters = self.chapters[:]
        self.populate_list()

    def on_key_down(self, event):
            key_code = event.GetKeyCode()
            if event.ControlDown() and key_code == ord('C'):
                self.on_copy_text(event)
                return
            if key_code in (wx.WXK_RETURN, wx.WXK_SPACE):
                self.on_open(event)
                return
            event.Skip()
            
    def on_open(self, event):
        selected_index = self.listCtrl.GetFirstSelected()
        if selected_index != -1:
            seconds = self.listCtrl.GetItemData(selected_index)
            timestamp_url = f"{self.base_video_url}&t={seconds}s"
            log.debug("Opening chapter URL: %s", timestamp_url)
            try:
                # Translators: Message shown when opening a URL in the web browser.
                ui.message(_("Opening in browser..."))
                webbrowser.open(timestamp_url)
            except Exception as e:
                log.warning("Failed to open URL in browser.", exc_info=True)
                # Translators: Message shown when browser fails to open.
                ui.message(_("Error opening browser: {error}").format(error=e))

    def on_copy_text(self, event):
        selected_index = self.listCtrl.GetFirstSelected()
        if selected_index != -1:
            title_str = self.listCtrl.GetItemText(selected_index, 0)
            time_str = self.listCtrl.GetItemText(selected_index, 1)
            full_text = f"{time_str} - {title_str}"
            copy_to_clipboard(full_text)
            # Translators: Message confirming that the timestamp has been copied.
            ui.message(_("Copied timestamp: {text}").format(text=full_text))

    def on_copy_url(self, event):
        selected_index = self.listCtrl.GetFirstSelected()
        if selected_index != -1:
            seconds = self.listCtrl.GetItemData(selected_index)
            timestamp_url = f"{self.base_video_url}&t={seconds}s"
            copy_to_clipboard(timestamp_url)
            # Translators: Message confirming that the URL has been copied.
            ui.message(_("Copied URL: {url}").format(url=timestamp_url))
    
    def on_export(self, event):
        default_path = config.conf["YoutubePlus"].get("exportPath", "") or os.path.expanduser("~/Desktop")
        safeTitle = sanitize_filename(f"{self.GetTitle()}")
        filename = f"{safeTitle}.txt"
        filepath = os.path.join(default_path, filename)
        log.info("Exporting '%s' to %s", self.GetTitle(), filepath)
        try:
            with open(filepath, "w", encoding="utf-8") as f:
                for chapter in self.chapters:
                    start_seconds = int(chapter.get('start_time', 0))
                    minutes, seconds = divmod(start_seconds, 60)
                    hours, minutes = divmod(minutes, 60)
                    time_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
                    title_str = chapter.get('title', '')
                    f.write(f"{time_str} - {title_str}\n")
                    # Translators: Message shown after a successful export.
            ui.message(_("Export complete"))
        except (IOError, OSError) as e:
            log.error("Failed to export chapters due to an OS/IO error.", exc_info=True)
            # Translators: Message shown when file export fails.
            ui.message(_("Error exporting file: {error}").format(error=e))
        except Exception as e:
            log.exception("An unexpected error occurred during chapter export.")
            # Translators: Message shown when an unknown error occurs during export.
            ui.message(_("An unexpected error occurred during export."))

class MessagesDialog(wx.Dialog):
    _instance = None
    def __new__(cls, *args, **kwargs):
        if MessagesDialog._instance is None:
            return super(MessagesDialog, cls).__new__(cls, *args, **kwargs)
        return MessagesDialog._instance

    def __init__(self, parent, title, core_instance):
        if not core_instance.active:
            wx.CallAfter(self.Destroy)
            return

        if MessagesDialog._instance is not None:
            return
        MessagesDialog._instance = self
        super().__init__(parent, title=title)
        self.core_instance = core_instance
        with self.core_instance._messages_lock:
            self.messages = list(self.core_instance.messages)
        # This limit is for the dialog's local view only.
        message_limit = config.conf["YoutubePlus"].get("messageLimit", 5000)
        self.messages = self.messages[-message_limit:]
        self.filteredMessages = self.messages[:]
        self.last_selected_obj = None
        
        panel = wx.Panel(self)
        mainSizer = wx.BoxSizer(wx.VERTICAL)

        searchSizer = wx.BoxSizer(wx.HORIZONTAL)
        # Translators: Label for the search box in the Chat Messages dialog.
        searchLabel = wx.StaticText(panel, label=_("&Search:"))
        self.searchTextCtrl = wx.TextCtrl(panel, style=wx.TE_PROCESS_ENTER)
        searchSizer.Add(searchLabel, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 5)
        searchSizer.Add(self.searchTextCtrl, 1, wx.EXPAND)
        mainSizer.Add(searchSizer, 0, wx.EXPAND | wx.ALL, 5)

        self.messagesListBox = MessagesListCtrl(panel)
        mainSizer.Add(self.messagesListBox, 1, wx.EXPAND | wx.ALL, 10)

        self.currentTextElement = wx.TextCtrl(panel, style=wx.TE_MULTILINE|wx.TE_READONLY)
        mainSizer.Add(self.currentTextElement, 0, wx.EXPAND | wx.ALL, 5)

        btnSizer = wx.BoxSizer(wx.HORIZONTAL)
        # Translators: Button to copy the selected message.
        self.copyBtn = wx.Button(panel, label=_("&Copy"))
        # Translators: Button to export chat messages to a file.
        self.exportBtn = wx.Button(panel, label=_("&Export"))
        # Translators: Button to close the dialog.
        self.closeBtn = wx.Button(panel, label=_("C&lose"))
        btnSizer.Add(self.copyBtn, 0, wx.RIGHT, 5)
        btnSizer.Add(self.exportBtn, 0, wx.RIGHT, 5)
        btnSizer.Add(self.closeBtn, 0)
        mainSizer.Add(btnSizer, 0, wx.ALIGN_RIGHT | wx.ALL, 10)
        panel.SetSizer(mainSizer)
        mainSizer.Fit(self)
        self.SetMinSize((700, 500))
        self.CentreOnScreen()
        
        self.searchTextCtrl.Bind(wx.EVT_TEXT, self.onSearch)
        self.copyBtn.Bind(wx.EVT_BUTTON, self.onCopy)
        self.exportBtn.Bind(wx.EVT_BUTTON, self.onExport)
        self.closeBtn.Bind(wx.EVT_BUTTON, lambda e: self.Close())
        self.Bind(wx.EVT_CHAR_HOOK, self.onCharHook)
        self.messagesListBox.Bind(wx.EVT_KEY_DOWN, self.processKey)
        self.messagesListBox.Bind(wx.EVT_LIST_ITEM_SELECTED, self.onMessageSelected)
        self.messagesListBox.Bind(wx.EVT_LIST_ITEM_DESELECTED, self.onMessageSelected)
        self.Bind(wx.EVT_CLOSE, self.onClose)
        
        self.updateList()

        last_index = self.core_instance.last_message_index
        item_count = self.messagesListBox.GetItemCount()
        if last_index is not None and last_index != -1 and last_index < item_count:
            self.messagesListBox.SetItemState(last_index, wx.LIST_STATE_SELECTED | wx.LIST_STATE_FOCUSED, wx.LIST_STATE_SELECTED | wx.LIST_STATE_FOCUSED)
            self.messagesListBox.EnsureVisible(last_index)
        elif item_count > 0:
            self.messagesListBox.SetItemState(0, wx.LIST_STATE_SELECTED | wx.LIST_STATE_FOCUSED, wx.LIST_STATE_SELECTED | wx.LIST_STATE_FOCUSED)
            self.messagesListBox.EnsureVisible(0)
        wx.CallAfter(self.messagesListBox.SetFocus)

    def onSearch(self, event):
        self.refreshMessages()

    def add_new_messages(self, new_messages):
        self.messages.extend(new_messages)
        # Apply message limit to the local copy in the dialog
        message_limit = config.conf["YoutubePlus"].get("messageLimit", 5000)
        if len(self.messages) > message_limit:
            self.messages = self.messages[-message_limit:]
        self.refreshMessages()

    def updateList(self):
        selected_index = self.messagesListBox.GetFirstSelected()
        if selected_index != -1 and selected_index < len(self.filteredMessages):
            self.last_selected_obj = self.filteredMessages[selected_index]
        item_count_before = self.messagesListBox.GetItemCount()
        is_at_bottom = (selected_index == item_count_before - 1)
        self.messagesListBox.Freeze()
        try:
            current_item_count = self.messagesListBox.GetItemCount()
            new_item_count = len(self.filteredMessages)
            if new_item_count < current_item_count:
                for i in range(current_item_count - 1, new_item_count - 1, -1):
                    self.messagesListBox.DeleteItem(i)
                current_item_count = new_item_count
            for i, msg_obj in enumerate(self.filteredMessages):
                if i < current_item_count:
                    if self.messagesListBox.GetItemText(i, 0) != msg_obj.get('author', ''):
                        self.messagesListBox.SetItem(i, 0, msg_obj.get('author', ''))
                    if self.messagesListBox.GetItemText(i, 1) != msg_obj.get('message', ''):
                        self.messagesListBox.SetItem(i, 1, msg_obj.get('message', ''))
                else:
                    self.messagesListBox.InsertItem(i, msg_obj.get('author', ''))
                    self.messagesListBox.SetItem(i, 1, msg_obj.get('message', ''))
                    self.messagesListBox.SetItem(i, 2, "")
            if self.last_selected_obj and self.last_selected_obj in self.filteredMessages:
                try:
                    new_index = self.filteredMessages.index(self.last_selected_obj)
                    self.messagesListBox.SetItemState(new_index, wx.LIST_STATE_SELECTED | wx.LIST_STATE_FOCUSED, wx.LIST_STATE_SELECTED | wx.LIST_STATE_FOCUSED)
                    self.messagesListBox.EnsureVisible(new_index)
                except ValueError:
                    if new_item_count > 0:
                        last_idx = new_item_count - 1
                        self.messagesListBox.SetItemState(last_idx, wx.LIST_STATE_SELECTED | wx.LIST_STATE_FOCUSED, wx.LIST_STATE_SELECTED | wx.LIST_STATE_FOCUSED)
                        self.messagesListBox.EnsureVisible(last_idx)
            elif (is_at_bottom or selected_index == -1) and new_item_count > 0:
                last_idx = new_item_count - 1
                self.messagesListBox.SetItemState(last_idx, wx.LIST_STATE_SELECTED | wx.LIST_STATE_FOCUSED, wx.LIST_STATE_SELECTED | wx.LIST_STATE_FOCUSED)
                self.messagesListBox.EnsureVisible(last_idx)
        finally:
            self.messagesListBox.Thaw()
            self.onMessageSelected(None)

    def refreshMessages(self):
        searchText = self.searchTextCtrl.GetValue().lower()
        if searchText and not hasattr(self, '_pre_search_obj'):
            selected_index = self.messagesListBox.GetFirstSelected()
            if selected_index != -1 and selected_index < len(self.filteredMessages):
                self._pre_search_obj = self.filteredMessages[selected_index]
        if searchText:
            self.filteredMessages = [
                m for m in self.messages
                if searchText in m.get('author', '').lower() or
                   searchText in m.get('message', '').lower()
            ]
        else:
            self.filteredMessages = self.messages[:]
        self.updateList()
        if not searchText and hasattr(self, '_pre_search_obj'):
            try:
                new_index = self.filteredMessages.index(self._pre_search_obj)
            except ValueError:
                new_index = len(self.filteredMessages) - 1
            del self._pre_search_obj
            if self.messagesListBox.GetItemCount() > 0:
                self.messagesListBox.SetItemState(-1, 0,
                    wx.LIST_STATE_SELECTED | wx.LIST_STATE_FOCUSED)
                self.messagesListBox.SetItemState(new_index,
                    wx.LIST_STATE_SELECTED | wx.LIST_STATE_FOCUSED,
                    wx.LIST_STATE_SELECTED | wx.LIST_STATE_FOCUSED)
                self.messagesListBox.EnsureVisible(new_index)
                
    def onCopy(self, event):
        selected = self.messagesListBox.GetFirstSelected()
        if selected != -1:
            msg_obj = self.filteredMessages[selected]
            full_text = f"{msg_obj.get('author')}: {msg_obj.get('message')}"
            copy_to_clipboard(full_text)
            # Translators: Notification when a message has been copied to clipboard.
            ui.message(_("message copied"))
        else:
            # Translators: Warning when user tries to copy without selecting a message.
            ui.message(_("No message selected"))

    def onExport(self, event):
        default_path = config.conf["YoutubePlus"].get("exportPath", "") or os.path.expanduser("~/Desktop")
        safeTitle = sanitize_filename(self.GetTitle())
        filename = f"{safeTitle}.txt"
        filepath = os.path.join(default_path, filename)
        log.info("Exporting all monitored chat messages for '%s' to %s", self.GetTitle(), filepath)
        try:
            with open(filepath, "w", encoding="utf-8") as f:
                with self.core_instance._messages_lock:
                    messages_to_export = list(self.core_instance.messages)
                for msg_obj in messages_to_export:
                    author = msg_obj.get('author', '')
                    message = msg_obj.get('message', '')
                    f.write(f"@{author}: {message}\n\n")
                    # Translators: Success message after exporting chat messages.
            ui.message(_("Export message complete"))
        except (IOError, OSError) as e:
            log.error("Failed to export chat messages due to an OS/IO error.", exc_info=True)
            # Translators: Error message when chat export fails.
            ui.message(_("Error exporting file: {error}").format(error=e))
        except Exception:
            log.exception("An unexpected error occurred during chat export.")
            # Translators: Error message for unexpected errors during chat export.
            ui.message(_("An unexpected error occurred during export."))

    def onCharHook(self, event):
        key = event.GetKeyCode()
        altDown = event.AltDown()
        if key == wx.WXK_ESCAPE: self.Close()
        elif altDown:
            if key == ord("C"): self.onCopy(event)
            elif key == ord("E"): self.onExport(event)
            elif key == ord("L"): self.Close()
            elif key == ord("S"): self.searchTextCtrl.SetFocus()
            elif ctrl and key == ord('W'):
                self.Close()
            else: event.Skip()
        else: event.Skip()

    def processKey(self, event):
        if event.ControlDown() and event.GetKeyCode() == ord('C'):
            self.onCopy(event)
            return
            if event.ControlDown() and event.GetKeyCode() == ord('W'):
                self.Close()
                return          
        if event.GetKeyCode() == wx.WXK_ESCAPE: self.Close()
        else: event.Skip()

    def onMessageSelected(self, event):
        selected_index = self.messagesListBox.GetFirstSelected()
        if selected_index != -1:
            self.last_selected_obj = self.filteredMessages[selected_index]
            msg_obj = self.filteredMessages[selected_index]
            full_text = f"{msg_obj.get('author')}: {msg_obj.get('message')}"
            self.currentTextElement.SetValue(full_text)
        else:
            self.currentTextElement.SetValue("")

    def onClose(self, event):
        selected_index = self.messagesListBox.GetFirstSelected()
        if selected_index != -1 and self.last_selected_obj in self.messages:
            try:
                self.core_instance.last_message_index = self.messages.index(self.last_selected_obj)
            except ValueError:
                self.core_instance.last_message_index = -1
        else:
            self.core_instance.last_message_index = selected_index
            
        MessagesDialog._instance = None
        self.Destroy()

class CommentsDialog(wx.Dialog):
    def __init__(self, parent, title, comments_data, is_replay_data=False):
        super().__init__(parent, title=title)
        self.comments_data = comments_data
        self.filteredComments = self.comments_data[:]
        self.last_selected_obj = None
        self.is_replay_data = is_replay_data

        self.panel = wx.Panel(self)
        mainSizer = wx.BoxSizer(wx.VERTICAL)

        searchSizer = wx.BoxSizer(wx.HORIZONTAL)
        # Translators: Label for the search box in Comments dialog.
        searchLabel = wx.StaticText(self.panel, label=_("&Search:"))
        self.searchTextCtrl = wx.TextCtrl(self.panel, style=wx.TE_PROCESS_ENTER)
        searchSizer.Add(searchLabel, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 5)
        searchSizer.Add(self.searchTextCtrl, 1, wx.EXPAND)
        mainSizer.Add(searchSizer, 0, wx.EXPAND | wx.ALL, 5)
        # Translators: Filter options in the comments dialog.
        filter_choices = [
            _("No Filter"),
            _("Filter by Selected Author"),
            _("Show Super Chats Only"),
            _("Show Super Stickers Only"),
            _("Show Super Thanks Only")
        ]
        self.filterComboBox = wx.ComboBox(self.panel, choices=filter_choices, style=wx.CB_READONLY)
        self.filterComboBox.SetValue(_("No Filter"))
        mainSizer.Add(self.filterComboBox, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 10)

        self.commentsListBox = CommentsListCtrl(self.panel)
        mainSizer.Add(self.commentsListBox, 1, wx.EXPAND | wx.ALL, 10)
        
        self.currentTextElement = wx.TextCtrl(self.panel, style=wx.TE_MULTILINE | wx.TE_READONLY)
        mainSizer.Add(self.currentTextElement, 0, wx.EXPAND | wx.ALL, 5)

        bottomBtnSizer = wx.BoxSizer(wx.HORIZONTAL)
        # Translators: Button to copy the selected comment.
        self.copyBtn = wx.Button(self.panel, label=_("&Copy"))
        # Translators: Button to export comments to a text file.
        self.exportBtn = wx.Button(self.panel, label=_("&Export"))
        self.totalAmountTextCtrl = wx.TextCtrl(self.panel, style=wx.TE_READONLY | wx.TE_MULTILINE | wx.TE_LEFT) 
        self.totalAmountTextCtrl.SetMinSize((150, -1)) 
        bottomBtnSizer.Add(self.totalAmountTextCtrl, 1, wx.EXPAND | wx.RIGHT, 5)

        bottomBtnSizer.Add(self.copyBtn, 0, wx.RIGHT, 5)
        bottomBtnSizer.Add(self.exportBtn, 0, wx.RIGHT, 5)
        # Translators: Button to close the dialog.
        self.closeBtn = wx.Button(self.panel, label=_("C&lose"))
        bottomBtnSizer.Add(self.closeBtn, 0)
        
        mainSizer.Add(bottomBtnSizer, 0, wx.ALIGN_RIGHT | wx.ALL, 10)
        self.panel.SetSizer(mainSizer) # << CHANGE: อ้างอิง self.panel
        mainSizer.Fit(self)
        self.SetMinSize((700, 500))
        self.CentreOnScreen()
        
        self.filterComboBox.Bind(wx.EVT_COMBOBOX, self.on_filter_select)
        self.copyBtn.Bind(wx.EVT_BUTTON, self.onCopy)
        self.exportBtn.Bind(wx.EVT_BUTTON, self.onExport)
        self.closeBtn.Bind(wx.EVT_BUTTON, lambda e: self.Close())
        self.commentsListBox.Bind(wx.EVT_KEY_DOWN, self.processKey)
        self.commentsListBox.Bind(wx.EVT_LIST_ITEM_SELECTED, self.onCommentSelected)
        self.commentsListBox.Bind(wx.EVT_LIST_ITEM_DESELECTED, self.onCommentSelected)
        self.searchTextCtrl.Bind(wx.EVT_TEXT, self.onSearch)
        self.Bind(wx.EVT_CHAR_HOOK, self.onCharHook)
        self.Bind(wx.EVT_CLOSE, self.onClose)
        
        self.totalAmountTextCtrl.Hide()
        self.populateList()
        if self.is_replay_data:
            self.update_total_amount_display()
        wx.CallAfter(self.commentsListBox.SetFocus)
        
    def update_total_amount_display(self):
        from .core import GlobalPlugin
        if not self.is_replay_data:
            return
        total_amounts = GlobalPlugin.instance.get_total_paid_amount_from_list(self.comments_data)
        if total_amounts:
            parts = []
            for currency, amount in total_amounts.items():
                parts.append(f"{currency}: {amount:,.2f}")
                # Translators: Label for the total sum of paid comments (Super Chats etc.)
            display_text = _("Total Paid Amount:\n") + "\n".join(parts)
            self.totalAmountTextCtrl.SetValue(display_text)
            self.totalAmountTextCtrl.Show(True)
        else:
            self.totalAmountTextCtrl.Show(False)
        self.panel.Layout()
        
    def on_filter_select(self, event):
        selection = self.filterComboBox.GetStringSelection()
        keyword = ""
        if selection == _("Filter by Selected Author"):
            selected_index = self.commentsListBox.GetFirstSelected()
            if selected_index != -1:
                displayed_author = self.commentsListBox.GetItemText(selected_index, 0)
                keyword = displayed_author.strip()
            else:
                keyword = ""
        elif selection == _("No Filter"):
            keyword = ""
        elif selection == _("Show Super Chats Only"):
            keyword = "Super Chat"
        elif selection == _("Show Super Stickers Only"):
            keyword = "Super Sticker"
        elif selection == _("Show Super Thanks Only"):
            keyword = "Super Thanks"
        if self.searchTextCtrl.GetValue() != keyword:
            self.searchTextCtrl.SetValue(keyword)
        else:
            self.refreshComments()
            
    def refreshComments(self):
        searchText = self.searchTextCtrl.GetValue().lower()
        log.debug("Filtering comments with text: %s", searchText)
        if searchText:
            self.filteredComments = [
                c for c in self.comments_data
                if searchText in c.get('author', '').lower() or searchText in c.get('message', '').lower()
            ]
        else:
            self.filteredComments = self.comments_data[:]
        self.populateList()

    def onSearch(self, event):
        self.refreshComments()
    def populateList(self):
        self.commentsListBox.Freeze()
        try:
            self.commentsListBox.DeleteAllItems()
            for i, item in enumerate(self.filteredComments):
                level = item.get('level', 0)
                author_display = '    ' * level + item.get('author', '')
                self.commentsListBox.InsertItem(i, author_display)
                self.commentsListBox.SetItem(i, 1, item.get('message', ''))
                self.commentsListBox.SetItem(i, 2, item.get('time', ''))
        finally:
            self.commentsListBox.Thaw()
        if self.commentsListBox.GetItemCount() > 0:
            if self.last_selected_obj and self.last_selected_obj in self.filteredComments:
                try:
                    new_index = self.filteredComments.index(self.last_selected_obj)
                    self.commentsListBox.SetItemState(new_index, wx.LIST_STATE_SELECTED | wx.LIST_STATE_FOCUSED, wx.LIST_STATE_SELECTED | wx.LIST_STATE_FOCUSED)
                    self.commentsListBox.EnsureVisible(new_index)
                except ValueError:
                    self.commentsListBox.SetItemState(0, wx.LIST_STATE_SELECTED | wx.LIST_STATE_FOCUSED, wx.LIST_STATE_SELECTED | wx.LIST_STATE_FOCUSED)
            else:
                self.commentsListBox.SetItemState(0, wx.LIST_STATE_SELECTED | wx.LIST_STATE_FOCUSED, wx.LIST_STATE_SELECTED | wx.LIST_STATE_FOCUSED)
        self.onCommentSelected(None)

    def onCopy(self, event):
        selected_index = self.commentsListBox.GetFirstSelected()
        if selected_index != -1:
            item_obj = self.filteredComments[selected_index]
            author = item_obj.get('author', '')
            message = item_obj.get('message', '')
            time_text = item_obj.get('time', '')
            level = item_obj.get('level', 0)
            indent = '    ' * level
            full_text = f"{indent}{author}: {message} ({time_text})" if time_text else f"{indent}{author}: {message}"
            copy_to_clipboard(full_text)
            # Translators: Confirmation message when a comment is copied.
            ui.message(_("Copied"))
        else:
            # Translators: Message shown when copy is pressed but no comment is selected.
            ui.message(_("Nothing selected"))

    def onExport(self, event):
        default_path = config.conf["YoutubePlus"].get("exportPath", "")
        if not default_path or not os.path.isdir(default_path):
            default_path = os.path.expanduser("~/Desktop")
        safeTitle = sanitize_filename(self.GetTitle())
        filename = f"{safeTitle}.txt"
        filepath = os.path.join(default_path, filename)
        log.info("Exporting comments for '%s' to %s", self.GetTitle(), filepath)
        try:
            with open(filepath, "w", encoding="utf-8") as f:
                for item in self.comments_data:
                    level = item.get('level', 0)
                    indent = '    ' * level
                    author = item.get('author', '')
                    text = item.get('message', '')
                    f.write(f"{indent}{author}: {text}\n\n")
                    # Translators: Success message after exporting comments.
            ui.message(_("Export complete"))
        except (IOError, OSError) as e:
            log.error("Failed to export comments due to an OS/IO error.", exc_info=True)
            # Translators: Error message when comment export fails.
            ui.message(_("Error exporting file: {error}").format(error=e))
        except Exception:
            log.exception("An unexpected error occurred during comments export.")
            # Translators: General error message for comment export failure.
            ui.message(_("An unexpected error occurred during export."))

    def onCharHook(self, event):
        key = event.GetKeyCode()
        altDown = event.AltDown()
        ctrl = event.ControlDown()
        if ctrl and key == ord('W'):
            self.Close()
        elif key == wx.WXK_ESCAPE:
            if getattr(self, '_escape_pending', False):
                self._escape_pending = False
                self.Close()
            else:
                self._escape_pending = True
                # Translators: Message shown when user presses Escape once in a protected dialog.
                ui.message(_("Press Escape again to close."))
        elif altDown:
            self._escape_pending = False
            if key == ord("C"): self.onCopy(event)
            elif key == ord("E"): self.onExport(event)
            elif key == ord("L"): self.Close()
            elif key == ord("S"): self.searchTextCtrl.SetFocus()
            else: event.Skip()
        else:
            self._escape_pending = False
            event.Skip()

    def processKey(self, event):
        if event.ControlDown() and event.GetKeyCode() == ord('C'):
            self.onCopy(event)
            return
        else:
            event.Skip()

    def onCommentSelected(self, event):
        selected_index = self.commentsListBox.GetFirstSelected()
        if selected_index != -1:
            self.last_selected_obj = self.filteredComments[selected_index]
            message_text = self.last_selected_obj.get('message', '')
            raw_text_parts = message_text.split(": ", 1)
            display_text = raw_text_parts[-1]
            self.currentTextElement.SetValue(display_text)
        else:
            self.currentTextElement.SetValue("")

    def onClose(self, event):
        self.Destroy()

class VideoActionMixin:
    """A mixin to provide a standardized 'Action' menu for any video list dialog."""
    
    def on_open_video(self, event):
        """Handles opening the selected video in a web browser."""
        video = self.get_selected_video_info()
        video_id = video.get('id') or video.get('video_id')
        if not video_id:
            # Translators: Error message when video ID is missing.
            ui.message(_("Video ID not found."))
            return
        url = f"https://www.youtube.com/watch?v={video_id}"
        # Translators: Message shown when opening a video in the browser.
        ui.message(_("Opening in browser..."))
        try:
            webbrowser.open(url)
        except Exception as e:
            log.warning("Failed to open URL in browser.", exc_info=True)
            # Translators: Error message with details when browser fails to open.
            ui.message(_("Error opening browser: {error}").format(error=e))

    def create_video_action_menu(self):
        """Creates and returns a wx.Menu with common video actions."""
        menu = wx.Menu()
        ID_VIEW_INFO = wx.NewIdRef()
        ID_VIEW_COMMENTS = wx.NewIdRef()
        ID_SHOW_CHAPTERS = wx.NewIdRef() 
        ID_DOWNLOAD_VID = wx.NewIdRef()
        ID_DOWNLOAD_AUD = wx.NewIdRef()
        ID_DOWNLOAD_SUB = wx.NewIdRef()
        ID_OPEN_VID_WEB = wx.NewIdRef()
        ID_ADD_FAV_VID = wx.NewIdRef()
        ID_ADD_FAV_CHAN = wx.NewIdRef()
        ID_ADD_WATCHLIST = wx.NewIdRef()
        ID_OPEN_CHAN_WEB = wx.NewIdRef()
        ID_SHOW_VIDS = wx.NewIdRef()
        ID_SHOW_SHORTS = wx.NewIdRef()
        ID_SHOW_LIVE = wx.NewIdRef()
        ID_SHOW_PLAYLIST = wx.NewIdRef()
        ID_SHOW_PODCAST = wx.NewIdRef()
        # Translators: Menu items for video actions.
        menu.Append(ID_VIEW_INFO, _("View Video &Info..."))
        menu.Append(ID_VIEW_COMMENTS, _("View &Comments / Replay..."))
        menu.Append(ID_SHOW_CHAPTERS, _("View Chap&ters/Timestamps...")) 
        menu.AppendSeparator()
        menu.Append(ID_DOWNLOAD_VID, _("&Download Video"))
        menu.Append(ID_DOWNLOAD_AUD, _("Download &Audio"))
        menu.Append(ID_DOWNLOAD_SUB, _("Download Su&btitles"))
        menu.AppendSeparator()
        menu.Append(ID_ADD_FAV_VID, _("Add to &Favorite Videos"))
        menu.Append(ID_ADD_FAV_CHAN, _("Add to &Favorite Channels"))
        menu.Append(ID_ADD_WATCHLIST, _("Add to &Watch List"))
        menu.AppendSeparator()
        menu.Append(ID_OPEN_VID_WEB, _("&Open video in browser"))
        menu.Append(ID_OPEN_CHAN_WEB, _("Open c&hannel in browser"))
        menu.AppendSeparator()
        menu.Append(ID_SHOW_VIDS, _("Show channel &videos"))
        menu.Append(ID_SHOW_SHORTS, _("Show channel &shorts"))
        menu.Append(ID_SHOW_LIVE, _("Show channel &live"))
        menu.Append(ID_SHOW_PLAYLIST, _("Show channel &playlist"))
        menu.Append(ID_SHOW_PODCAST, _("Show channel &podcast"))
        menu.Bind(wx.EVT_MENU, self.on_view_info, id=ID_VIEW_INFO)
        menu.Bind(wx.EVT_MENU, self.on_view_comments, id=ID_VIEW_COMMENTS)
        menu.Bind(wx.EVT_MENU, self.on_show_chapters, id=ID_SHOW_CHAPTERS)  # <--- ✅ เพิ่ม Event Binding ใหม่
        menu.Bind(wx.EVT_MENU, self.on_download_video, id=ID_DOWNLOAD_VID)
        menu.Bind(wx.EVT_MENU, self.on_download_audio, id=ID_DOWNLOAD_AUD)
        menu.Bind(wx.EVT_MENU, self.on_download_subtitles, id=ID_DOWNLOAD_SUB)
        menu.Bind(wx.EVT_MENU, self.on_open_video, id=ID_OPEN_VID_WEB)
        menu.Bind(wx.EVT_MENU, self.on_add_to_fav_video, id=ID_ADD_FAV_VID)
        menu.Bind(wx.EVT_MENU, self.on_add_to_fav_channel, id=ID_ADD_FAV_CHAN)
        menu.Bind(wx.EVT_MENU, self.on_add_to_watchlist, id=ID_ADD_WATCHLIST)
        menu.Bind(wx.EVT_MENU, self.on_open_channel, id=ID_OPEN_CHAN_WEB)
        menu.Bind(wx.EVT_MENU, lambda e: self._view_channel_content('videos'), id=ID_SHOW_VIDS)
        menu.Bind(wx.EVT_MENU, lambda e: self._view_channel_content('shorts'), id=ID_SHOW_SHORTS)
        menu.Bind(wx.EVT_MENU, lambda e: self._view_channel_content('streams'), id=ID_SHOW_LIVE)
        menu.Bind(wx.EVT_MENU, lambda e: self._view_channel_content('playlists'), id=ID_SHOW_PLAYLIST)
        menu.Bind(wx.EVT_MENU, lambda e: self._view_channel_content('podcasts'), id=ID_SHOW_PODCAST)
        return menu

    def on_download_subtitles(self, event):
        video = self.get_selected_video_info()
        if not video:
            # Translators: Error message when no video is selected for subtitle download.
            return ui.message(_("Video ID not found."))
        video_id = video.get('id') or video.get('video_id')
        if not video_id:
            return ui.message(_("Video ID not found."))
        url = f"https://youtube.com/watch?v={video_id}"
        # Translators: Status message shown when the add-on starts fetching subtitle information.
        ui.message(_("Getting subtitle info..."))
        threading.Thread(target=self.core._subtitle_worker, args=(url,), daemon=True).start()

    def on_show_chapters(self, event):
        """Handles showing the chapters/timestamps dialog for the selected video."""
        video = self.get_selected_video_info()
        if not video:
            # Translators: Error message.
            return ui.message(_("Video ID not found."))
        video_id = video.get('id') or video.get('video_id')
        if not video_id: return ui.message(_("Video ID not found."))
        url = f"https://youtube.com/watch?v={video_id}"
        # Translators: Status message when fetching chapters.
        ui.message(_("Getting chapters..."))
        threading.Thread(target=self.core._show_chapters_worker, args=(url, ), daemon=True).start()
        
    def on_add_to_fav_video(self, event):
        video = self.get_selected_video_info()
        video_id = video.get('id') or video.get('video_id')
        if not video_id:
            # Translators: Error message.
            ui.message(_("Could not get video ID to add to favorites."))
            return
        url = f"https://www.youtube.com/watch?v={video_id}"
        threading.Thread(target=self.core.add_item_to_favorites_worker, args=(url,), daemon=True).start()

    def on_add_to_fav_channel(self, event):
        video = self.get_selected_video_info()
        video_id = video.get('id') or video.get('video_id')
        if not video_id:
            # Translators: Error message.
            ui.message(_("Could not get video ID to find the channel."))
            return
        url = f"https://www.youtube.com/watch?v={video_id}"
        threading.Thread(target=self.core.add_channel_to_favorites_worker, args=(url,), daemon=True).start()

    def on_add_to_watchlist(self, event):
        class_name = self.__class__.__name__
        is_actually_sub_dialog = (class_name == "SubDialog")
        if hasattr(self, 'notebook'):
            currentPage = self.notebook.GetCurrentPage()
            if not currentPage: return
            listCtrl = currentPage.listCtrl
            tab_id = getattr(currentPage, 'tab_id', None)
        else:
            listCtrl = getattr(self, 'listCtrl', None)
            tab_id = None
        if not listCtrl: return
        selected_index = listCtrl.GetFirstSelected()
        video_to_mark = self.get_selected_video_info()
        if not video_to_mark: return
        self.pending_focus_info = {'tab_id': tab_id, 'index': selected_index}
        video_id = video_to_mark.get('video_id') or video_to_mark.get('id')
        if not video_id: return
        url = f"https://www.youtube.com/watch?v={video_id}"
        threading.Thread(
            target=self.core.add_to_watchlist_worker, 
            args=(url,), 
            kwargs={'mark_seen': is_actually_sub_dialog}, 
            daemon=True
        ).start()
        
    def on_view_info(self, event):
        video = self.get_selected_video_info()
        if not video: return
        video_id = video.get('id') or video.get('video_id')
        if not video_id:
            # Translators: Error message.
            return ui.message(_("Video ID not found."))
        url = f"https://youtube.com/watch?v={video_id}"
        threading.Thread(target=self.core._get_info_worker, args=(url,), daemon=True).start()

    def on_view_comments(self, event):
        video = self.get_selected_video_info()
        if not video: return
        video_id = video.get('id') or video.get('video_id')
        if not video_id:
            # Translators: Error message.
            return ui.message(_("Video ID not found."))
        url = f"https://youtube.com/watch?v={video_id}"
        # Translators: Message shown while fetching comments for a specific video title.
        #ui.message(_("Getting data for '{title}'...").format(title=video.get('title')))
        threading.Thread(target=self.core.get_data_for_url, args=(url,), daemon=True).start()

    def on_download_video(self, event):
        video = self.get_selected_video_info()
        if not video: return
        video_id = video.get('id') or video.get('video_id')
        if not video_id:
            # Translators: Error message.
            return ui.message(_("Video ID not found."))
        url = f"https://youtube.com/watch?v={video_id}"
        dlg = DownloadProgressDialog(gui.mainFrame, self.core)
        dlg.Show()
        threading.Thread(target=self.core._direct_download_worker, args=(url, 'video'), daemon=True).start()

    def on_download_audio(self, event):
        video = self.get_selected_video_info()
        if not video: return
        video_id = video.get('id') or video.get('video_id')
        if not video_id: 
            # Translators: Error message.
            return ui.message(_("Video ID not found."))
        url = f"https://youtube.com/watch?v={video_id}"
        dlg = DownloadProgressDialog(gui.mainFrame, self.core)
        dlg.Show()
        threading.Thread(target=self.core._direct_download_worker, args=(url, 'audio'), daemon=True).start()

    def on_open_channel(self, event):
        video = self.get_selected_video_info()
        if not video or not video.get('channel_url'): return
        webbrowser.open(video['channel_url'])

    def on_copy(self, copy_type):
        """Handles copying a specific piece of video data to the clipboard."""
        video = self.get_selected_video_info()
        if not video: return
        is_collection = video.get('is_collection', False)
        video_id = video.get('id') or video.get('video_id')
        if not video_id: return
        text_to_copy = ""
        if copy_type == 'title':
            text_to_copy = video.get('title', '')
        elif copy_type == 'url':
            if is_collection:
                text_to_copy = video.get('playlist_url', f"https://www.youtube.com/playlist?list={video_id}")
            else:
                text_to_copy = f"https://youtu.be/{video_id}"
        elif copy_type == 'channel_name':
            text_to_copy = video.get('channel_name', '')
        elif copy_type == 'channel_url':
            text_to_copy = video.get('channel_url', '')
        elif copy_type == 'summary':
            if is_collection:
                # Translators: Labels used when copying video summary to clipboard.
                text_to_copy = (
                    _("Title: {title}\n").format(title=video.get('title', '')) +
                    _("Channel: {channel}\n").format(channel=video.get('channel_name', '')) +
                    _("URL: ") + video.get('playlist_url', f"https://www.youtube.com/playlist?list={video_id}")
                )
            else:
                # Translators: Labels used when copying video summary to clipboard.
                text_to_copy = (
                    _("Title: {title}\n").format(title=video.get('title', '')) +
                    _("Channel: {channel}\n").format(channel=video.get('channel_name', '')) +
                    _("URL: ") + f"https://youtu.be/{video_id}"
                )
        if text_to_copy:
            api.copyToClip(text_to_copy)
            # Translators: Confirmation message when something is copied.
            ui.message(_("Copied"))
            
    def _view_channel_content(self, content_type):
        video = self.get_selected_video_info()
        if not video: return
        channel_url = video.get("channel_url")
        channel_name = video.get("channel_name")
        if not channel_url or not channel_name:
            # Translators: Error message.
            ui.message(_("Error: Channel information not found for this item."))
            return
        suffix_map = {
            "videos":    "/videos",
            "shorts":    "/shorts",
            "streams":   "/streams",
            "playlists": "/playlists",
            "podcasts":  "/podcasts",
        }
        label_map = {
            "videos":    _("Videos"),
            "shorts":    _("Shorts"),
            "streams":   _("Live"),
            "playlists": _("Playlists"),
            "podcasts":  _("Podcasts"),
        }
        is_collection = content_type in ("playlists", "podcasts")
        suffix = suffix_map.get(content_type, "/videos")
        label = label_map.get(content_type, _("Content"))
        full_url = channel_url.rstrip('/') + suffix
        # Translators: Status message when fetching specific content from a channel.
        # {type} will be Videos, Shorts, Live, Playlist, or Podcast.
        title_template = _("Fetching {type} from {channel}...").format(channel=channel_name, type=label)
        thread_kwargs = {
            'url': full_url,
            'dialog_title_template': title_template,
            'content_type_label': label,
            'base_channel_url': channel_url,
            'base_channel_name': channel_name,
            'is_collection': is_collection,
        }
        threading.Thread(target=self.core._view_channel_worker, kwargs=thread_kwargs, daemon=True).start()
        
    def handle_video_list_keys(self, event):
        """
        Universal handler for Enter and Space keys.
        """
        key_code = event.GetKeyCode()
        if key_code == wx.WXK_RETURN:
            self.on_open_video(event)
            return
        elif key_code == wx.WXK_SPACE:
            self.run_quick_action(event)
            return
        event.Skip()

    def run_quick_action(self, event=None):
        action = config.conf["YoutubePlus"].get("quickAction", "open_video")
        if action == "open_video":
            self.on_open_video(None)
        elif action == "info":
            self.on_view_info(None)
        elif action == "comments":
            self.on_view_comments(None)
        elif action == "chapters":
            self.on_show_chapters(None)
        elif action == "download_video":
            self.on_download_video(None)
        elif action == "download_audio":
            self.on_download_audio(None)
        elif action == "download_subtitles":
            self.on_download_subtitles(None)        
        elif action == "add_to_fav_video":
            self.on_add_to_fav_video(None)
        elif action == "add_to_fav_channel":
            self.on_add_to_fav_channel(None)
        elif action == "add_to_watchlist":
            self.on_add_to_watchlist(None)
        elif action == "copy_url":
            self.on_copy("url")
        elif action == "copy_title":
            self.on_copy("title")
        elif action == "copy_channel_name":
            self.on_copy("channel_name")
        elif action == "copy_channel_url":
            self.on_copy("channel_url")
        elif action == "copy_summary":
            self.on_copy("summary")
        elif action == "open_channel":
            self.on_open_channel(None)
        elif action == "show_channel_videos":
            self._view_channel_content("videos")
        elif action == "show_channel_shorts":
            self._view_channel_content("shorts")
        elif action == "show_channel_lives":
            self._view_channel_content("streams")
        elif action == "show_channel_playlists":
            self._view_channel_content("playlists")
        elif action == "show_channel_podcasts":
            self._view_channel_content("podcasts")

class BaseVideoListPanel(wx.Panel, VideoActionMixin):
    # Class-level clipboard shared across all instances (enables cross-list paste)
    _clipboard = []
    _clipboard_is_cut = False
    _clipboard_source = None

    _CONF_KEY = "videoListLastCatId"  # subclasses MUST override with a unique key

    def __init__(self, parent, core_instance):
        super().__init__(parent)
        self.core = core_instance
        self.items = []
        self.categories = []
        self.filtered_items = []
        self._current_sort = None
        self._saved_search_text = ""
        self._search_mode = False
        self._closing = False
        self._initial_focus_done = False
        self.last_selected_item_before_search = None

        self.file_path = self._get_file_path()
        self.cat_file_path = self._get_category_file_path()
        self.callback_topic = self._get_callback_topic()

        self._load_data()
        self._build_ui()
        self._populate_tree()
        self._restore_selected_cat()
        self._update_button_states()

        if self.callback_topic:
            self.core.register_callback(self.callback_topic, self.refresh_data)

    # ---------- Hooks subclasses must/can override ----------

    def _get_file_path(self):
        raise NotImplementedError

    def _get_category_file_path(self):
        raise NotImplementedError

    def _get_callback_topic(self):
        raise NotImplementedError

    def _get_add_button_label(self):
        raise NotImplementedError

    def _get_default_category_label(self):
        """Display name of the built-in 'uncategorized' node."""
        return _("Videos")

    def _get_search_fields(self, item):
        return [item.get('title', ''), item.get('channel_name', '')]

    def _get_item_title_for_messages(self, item):
        return item.get('title', 'N/A')

    def _get_sort_fields(self):
        return [
            ('title', _("Title")),
            ('channel_name', _("Channel")),
            ('duration_str', _("Duration")),
            ('upload_date', _("Uploaded Date")),
            ('added_at', _("Date Added")),
        ]

    def _add_worker(self):
        raise NotImplementedError

    def _sanitize_pasted_item(self, item):
        """Hook: subclasses override to strip/adjust fields on cross-list paste."""
        return dict(item)

    # ---------- UI ----------

    def _build_ui(self):
        mainSizer = wx.BoxSizer(wx.VERTICAL)

        self.splitter = wx.SplitterWindow(self, style=wx.SP_LIVE_UPDATE)
        self.treePane = wx.Panel(self.splitter)
        self.listPane = wx.Panel(self.splitter)

        tSizer = wx.BoxSizer(wx.VERTICAL)
        self.treeCtrl = wx.TreeCtrl(
            self.treePane,
            style=wx.TR_DEFAULT_STYLE | wx.TR_HAS_BUTTONS | wx.TR_HIDE_ROOT | wx.TR_FULL_ROW_HIGHLIGHT
        )
        self._root = self.treeCtrl.AddRoot("root")
        tSizer.Add(self.treeCtrl, 1, wx.EXPAND)
        self.treePane.SetSizer(tSizer)

        lSizer = wx.BoxSizer(wx.VERTICAL)
        self.listCtrl = wx.ListCtrl(self.listPane, style=wx.LC_REPORT)
        self._create_list_columns(self.listCtrl)
        lSizer.Add(self.listCtrl, 1, wx.EXPAND | wx.BOTTOM, 5)

        btnSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.actionBtn = wx.Button(self.listPane, label=_("&Action..."))
        self.copyBtn   = wx.Button(self.listPane, label=_("&Copy..."))
        self.addBtn    = wx.Button(self.listPane, label=self._get_add_button_label())
        self.removeBtn = wx.Button(self.listPane, label=_("&Remove"))
        btnSizer.Add(self.actionBtn, 0, wx.RIGHT, 5)
        btnSizer.Add(self.copyBtn,   0, wx.RIGHT, 5)
        btnSizer.AddStretchSpacer()
        btnSizer.Add(self.addBtn,    0, wx.RIGHT, 5)
        btnSizer.Add(self.removeBtn, 0)
        lSizer.Add(btnSizer, 0, wx.EXPAND)
        self.listPane.SetSizer(lSizer)

        self.splitter.SplitVertically(self.treePane, self.listPane, 200)
        mainSizer.Add(self.splitter, 1, wx.EXPAND | wx.ALL, 5)
        self.SetSizer(mainSizer)

        self.Bind(wx.EVT_CHAR_HOOK, self._on_char_hook)
        self.treeCtrl.Bind(wx.EVT_TREE_SEL_CHANGED, self._on_cat_selected)
        self.treeCtrl.Bind(wx.EVT_CONTEXT_MENU, self._on_tree_right_click)
        self.treeCtrl.Bind(wx.EVT_KEY_DOWN, self._on_tree_key_down)
        self.listCtrl.Bind(wx.EVT_LIST_ITEM_SELECTED, self.on_list_item_selected)
        self.listCtrl.Bind(wx.EVT_LIST_ITEM_DESELECTED, self.on_list_item_selected)
        self.listCtrl.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.on_open_video)
        self.listCtrl.Bind(wx.EVT_KEY_DOWN, self.on_list_key_down)
        self.listCtrl.Bind(wx.EVT_CONTEXT_MENU, self._on_list_right_click)
        self.actionBtn.Bind(wx.EVT_BUTTON, self.on_action_menu)
        self.copyBtn.Bind(wx.EVT_BUTTON, self.on_copy_menu)
        self.addBtn.Bind(wx.EVT_BUTTON, self.on_add)
        self.removeBtn.Bind(wx.EVT_BUTTON, self.on_remove)

    def _create_list_columns(self, list_ctrl):
        list_ctrl.InsertColumn(0, _("Title"), width=320)
        list_ctrl.InsertColumn(1, _("Duration"), width=90)
        list_ctrl.InsertColumn(2, _("Channel"), width=160)
        list_ctrl.InsertColumn(3, _("Date Added"), width=140)

    def on_close(self, event=None):
        self._closing = True
        if self.callback_topic:
            self.core.unregister_callback(self.callback_topic, self.refresh_data)
        self._save_data()

    # ---------- Data ----------

    def _load_data(self):
        with self.core._fav_file_lock:
            try:
                if os.path.exists(self.file_path):
                    with open(self.file_path, 'r', encoding='utf-8') as f:
                        self.items = json.load(f)
                else:
                    self.items = []
            except (FileNotFoundError, json.JSONDecodeError, TypeError):
                self.items = []
        # Migration: backfill category_id for data saved before categories existed.
        migrated = False
        for item in self.items:
            if "category_id" not in item:
                item["category_id"] = None
                migrated = True
        if migrated:
            self._save_data()
        raw_cats = self.core._load_json_list(self.cat_file_path)
        self.categories = sorted(raw_cats, key=lambda c: c.get("position", 0))

    def _save_data(self):
        with self.core._fav_file_lock:
            try:
                with open(self.file_path, 'w', encoding='utf-8') as f:
                    json.dump(self.items, f, indent=2, ensure_ascii=False)
            except (IOError, OSError):
                ui.message(_("Error: Could not save data."))

    def _save_categories(self):
        for i, cat in enumerate(self.categories):
            cat["position"] = i
        self.core._save_json_list(self.cat_file_path, self.categories)

    def _get_item_unique_key(self, item):
        return item.get('url') or item.get('title', '')

    def refresh_data(self, data=None):
        if self._closing or not self.treeCtrl:
            return
        try:
            saved_cat_id = self._get_selected_cat_id()
            self._load_data()
            self._populate_tree()
            self._restore_cat_by_id(saved_cat_id)
            current_search = getattr(self, '_saved_search_text', "")
            self.on_search(current_search)
            if data and data.get("action") == "add" and self.listCtrl.GetItemCount() > 0:
                last_index = self.listCtrl.GetItemCount() - 1
                self._focus_item(last_index)
            self._update_button_states()
        except RuntimeError:
            pass

    # ---------- Category tree ----------

    def _populate_tree(self):
        self.treeCtrl.DeleteChildren(self._root)
        for cat in self.categories:
            node = self.treeCtrl.AppendItem(self._root, cat["name"])
            self.treeCtrl.SetItemData(node, {"type": "category", "cat": cat})
        default_node = self.treeCtrl.AppendItem(self._root, self._get_default_category_label())
        self.treeCtrl.SetItemData(default_node, {"type": "default"})

    def _get_selected_cat_id(self):
        node = self.treeCtrl.GetSelection()
        if not node.IsOk():
            return None
        data = self.treeCtrl.GetItemData(node)
        if not data:
            return None
        if data.get("type") == "category":
            return data["cat"]["id"]
        return "__default__"

    def _restore_selected_cat(self):
        saved = config.conf["YoutubePlus"].get(self._CONF_KEY, "__default__")
        self._restore_cat_by_id(saved)

    def _restore_cat_by_id(self, cat_id):
        child, cookie = self.treeCtrl.GetFirstChild(self._root)
        while child.IsOk():
            data = self.treeCtrl.GetItemData(child)
            if data:
                if cat_id == "__default__" and data.get("type") == "default":
                    self.treeCtrl.SelectItem(child)
                    return
                if data.get("type") == "category" and data["cat"]["id"] == cat_id:
                    self.treeCtrl.SelectItem(child)
                    return
            child, cookie = self.treeCtrl.GetNextChild(self._root, cookie)
        first, _cookie = self.treeCtrl.GetFirstChild(self._root)
        if first.IsOk():
            self.treeCtrl.SelectItem(first)

    def _save_selected_cat(self):
        cat_id = self._get_selected_cat_id()
        if cat_id:
            config.conf["YoutubePlus"][self._CONF_KEY] = cat_id

    def _get_cat_id_for_selected_node(self):
        node = self.treeCtrl.GetSelection()
        if not node.IsOk():
            return None
        data = self.treeCtrl.GetItemData(node)
        if data and data.get("type") == "category":
            return data["cat"]["id"]
        return None  # default node

    def _get_cat_name_for_selected_node(self):
        node = self.treeCtrl.GetSelection()
        if not node.IsOk():
            return self._get_default_category_label()
        data = self.treeCtrl.GetItemData(node)
        if data and data.get("type") == "category":
            return data["cat"]["name"]
        return self._get_default_category_label()

    def _on_cat_selected(self, event):
        if self._closing:
            event.Skip()
            return
        try:
            self._save_selected_cat()
            self._search_mode = False
            self.on_search("")
            self._update_button_states()
        except RuntimeError:
            pass
        event.Skip()

    def _on_tree_right_click(self, event):
        node = self.treeCtrl.GetSelection()
        if node.IsOk():
            self.treeCtrl.SelectItem(node)
        self._show_category_menu()

    def _on_tree_key_down(self, event):
        key  = event.GetKeyCode()
        ctrl = event.ControlDown()
        node = self.treeCtrl.GetSelection()
        data = self.treeCtrl.GetItemData(node) if node.IsOk() else None
        is_cat = bool(data and data.get("type") == "category")

        if key in (wx.WXK_RETURN, wx.WXK_NUMPAD_ENTER):
            wx.CallAfter(self.listCtrl.SetFocus)
        elif key == wx.WXK_F2:
            if is_cat:
                self._category_rename(data["cat"])
        elif ctrl and key == ord("="):
            self._category_add()
        elif key == wx.WXK_DELETE:
            if is_cat:
                self._category_delete(data["cat"])
            else:
                ui.message(_("The default {label} category cannot be deleted.").format(
                    label=self._get_default_category_label()))
        else:
            event.Skip()

    def _on_char_hook(self, event):
        key = event.GetKeyCode()
        if (event.ControlDown() and event.ShiftDown()
                and key in (wx.WXK_UP, wx.WXK_DOWN)
                and wx.Window.FindFocus() is self.treeCtrl):
            node = self.treeCtrl.GetSelection()
            data = self.treeCtrl.GetItemData(node) if node.IsOk() else None
            if data and data.get("type") == "category":
                self._category_move(data["cat"], -1 if key == wx.WXK_UP else 1)
            else:
                tones.beep(200, 50)
            return
        event.Skip()

    def _show_category_menu(self):
        node = self.treeCtrl.GetSelection()
        data = self.treeCtrl.GetItemData(node) if node.IsOk() else None
        is_cat = data and data.get("type") == "category"

        menu = wx.Menu()
        menu.Append(1, _("&Add Category"))
        if is_cat:
            menu.Append(2, _("&Rename Category"))
            menu.Append(3, _("&Delete Category"))
            menu.AppendSeparator()
            menu.Append(4, _("Move &Up"))
            menu.Append(5, _("Move &Down"))

        def on_select(e):
            eid = e.GetId()
            if eid == 1:   self._category_add()
            elif eid == 2: self._category_rename(data["cat"])
            elif eid == 3: self._category_delete(data["cat"])
            elif eid == 4: self._category_move(data["cat"], -1)
            elif eid == 5: self._category_move(data["cat"], 1)

        menu.Bind(wx.EVT_MENU, on_select)
        self.PopupMenu(menu)
        menu.Destroy()

    def _category_add(self):
        dlg = wx.TextEntryDialog(self, _("Category name:"), _("Add Category"))
        if dlg.ShowModal() != wx.ID_OK:
            dlg.Destroy()
            return
        name = dlg.GetValue().strip()
        dlg.Destroy()
        if not name:
            return
        import uuid
        new_cat = {"id": str(uuid.uuid4()), "name": name, "position": len(self.categories)}
        self.categories.append(new_cat)
        self._save_categories()
        self._populate_tree()
        self._restore_cat_by_id(new_cat["id"])
        ui.message(_("Category '{name}' added.").format(name=name))

    def _category_rename(self, cat):
        dlg = wx.TextEntryDialog(self, _("New name:"), _("Rename Category"), cat["name"])
        if dlg.ShowModal() != wx.ID_OK:
            dlg.Destroy()
            return
        name = dlg.GetValue().strip()
        dlg.Destroy()
        if not name:
            return
        cat["name"] = name
        self._save_categories()
        self._populate_tree()
        self._restore_cat_by_id(cat["id"])
        ui.message(_("Renamed to '{name}'.").format(name=name))

    def _category_delete(self, cat):
        cat_id = cat["id"]
        video_count = sum(1 for v in self.items if v.get("category_id") == cat_id)
        default_label = self._get_default_category_label()

        if video_count == 0:
            if wx.MessageBox(
                _("Delete category '{name}'?").format(name=cat["name"]),
                _("Confirm"), wx.YES_NO | wx.ICON_QUESTION
            ) != wx.YES:
                return
            self.categories = [c for c in self.categories if c["id"] != cat_id]
            self._save_categories()
            self._populate_tree()
            self._restore_cat_by_id("__default__")
            self.core._notify_delete(_("Category '{name}' deleted.").format(name=cat["name"]))
            return

        dlg = wx.MessageDialog(
            self,
            _("Category '{name}' contains {count} item(s).\n\n"
              "Move them to '{default}', or delete them along with the category?")
                .format(name=cat["name"], count=video_count, default=default_label),
            _("Delete Category"),
            wx.YES_NO | wx.CANCEL | wx.ICON_QUESTION
        )
        dlg.SetYesNoCancelLabels(_("&Move to {default}").format(default=default_label),
                                  _("&Delete items too"), _("Cancel"))
        result = dlg.ShowModal()
        dlg.Destroy()
        if result == wx.ID_CANCEL:
            return

        if result == wx.ID_YES:
            for v in self.items:
                if v.get("category_id") == cat_id:
                    v["category_id"] = None
            msg = _("Category '{name}' deleted. {count} item(s) moved to {default}.").format(
                name=cat["name"], count=video_count, default=default_label)
        else:
            self.items = [v for v in self.items if v.get("category_id") != cat_id]
            msg = _("Category '{name}' and its {count} item(s) deleted.").format(
                name=cat["name"], count=video_count)

        self.categories = [c for c in self.categories if c["id"] != cat_id]
        self._save_data()
        self._save_categories()
        self._populate_tree()
        self._restore_cat_by_id("__default__")
        self.core._notify_delete(msg)

    def _category_move(self, cat, direction):
        idx = next((i for i, c in enumerate(self.categories) if c["id"] == cat["id"]), -1)
        if idx == -1:
            return
        new_idx = idx + direction
        if new_idx < 0 or new_idx >= len(self.categories):
            tones.beep(200, 50)
            return
        self.categories[idx], self.categories[new_idx] = self.categories[new_idx], self.categories[idx]
        self._save_categories()
        self._populate_tree()
        self._restore_cat_by_id(cat["id"])

    # ---------- List rendering ----------

    def _populate_list(self):
        self.listCtrl.Freeze()
        try:
            self.listCtrl.DeleteAllItems()
            has_cat_col = self.listCtrl.GetColumnCount() > 4

            if self._search_mode:
                if self.splitter.IsSplit():
                    self.splitter.Unsplit(self.treePane)
                if not has_cat_col:
                    self.listCtrl.InsertColumn(4, _("Category"), width=120)
                for i, v in enumerate(self.filtered_items):
                    cat_id = v.get("category_id")
                    cat_name = next((c["name"] for c in self.categories if c["id"] == cat_id),
                                     self._get_default_category_label())
                    self._insert_list_row(i, v)
                    self.listCtrl.SetItem(i, 4, cat_name)
            else:
                if not self.splitter.IsSplit():
                    self.splitter.SplitVertically(self.treePane, self.listPane, 200)
                if has_cat_col:
                    self.listCtrl.DeleteColumn(4)
                for i, v in enumerate(self.filtered_items):
                    self._insert_list_row(i, v)

            if self.listCtrl.GetItemCount() > 0:
                self.listCtrl.SetItemState(
                    0, wx.LIST_STATE_SELECTED | wx.LIST_STATE_FOCUSED,
                    wx.LIST_STATE_SELECTED | wx.LIST_STATE_FOCUSED)
                self.listCtrl.EnsureVisible(0)
        finally:
            self.listCtrl.Thaw()

        if not self._initial_focus_done:
            wx.CallAfter(self.listCtrl.SetFocus)
            self._initial_focus_done = True

    def _insert_list_row(self, index, video):
        self.listCtrl.InsertItem(index, video.get("title") or _("[Unavailable video]"))
        self.listCtrl.SetItem(index, 1, video.get("duration_str", ""))
        self.listCtrl.SetItem(index, 2, video.get("channel_name", ""))
        self.listCtrl.SetItem(index, 3, video.get("added_at", ""))

    def _recompute_filtered_items(self):
        if self._search_mode:
            q = self._saved_search_text.strip().lower()
            self.filtered_items = [
                v for v in self.items
                if any(q in field.lower() for field in self._get_search_fields(v))
            ]
        else:
            cat_id = self._get_cat_id_for_selected_node()
            self.filtered_items = [v for v in self.items if v.get("category_id") == cat_id]

    def on_search(self, search_text):
        self._saved_search_text = search_text
        self._search_mode = bool(search_text.strip())
        if self._search_mode and self.last_selected_item_before_search is None:
            selected_index = self.listCtrl.GetFirstSelected()
            if selected_index != -1 and selected_index < len(self.filtered_items):
                self.last_selected_item_before_search = self.filtered_items[selected_index]
        self._recompute_filtered_items()
        self._populate_list()
        self._update_button_states()
        if not self._search_mode and self.last_selected_item_before_search:
            try:
                new_index = self.filtered_items.index(self.last_selected_item_before_search)
            except ValueError:
                new_index = 0
            self.last_selected_item_before_search = None
            self._focus_item(new_index)
        elif self.listCtrl.GetItemCount() > 0:
            self._focus_item(0)

    def _focus_item(self, index):
        count = self.listCtrl.GetItemCount()
        if count == 0:
            return
        index = min(index, count - 1)
        self._is_programmatic_focus = True
        self.listCtrl.SetItemState(-1, 0, wx.LIST_STATE_SELECTED | wx.LIST_STATE_FOCUSED)
        self.listCtrl.SetItemState(
            index, wx.LIST_STATE_SELECTED | wx.LIST_STATE_FOCUSED,
            wx.LIST_STATE_SELECTED | wx.LIST_STATE_FOCUSED)
        self.listCtrl.EnsureVisible(index)
        self._is_programmatic_focus = False

    def on_list_item_selected(self, event):
        if not getattr(self, '_is_programmatic_focus', False):
            self._update_button_states()
        event.Skip()

    def get_selected_video_info(self):
        idx = self.listCtrl.GetFirstSelected()
        if idx == -1 or idx >= len(self.filtered_items):
            return None
        return self.filtered_items[idx]

    def _get_selected_items(self):
        selected = []
        idx = self.listCtrl.GetFirstSelected()
        while idx != -1:
            if idx < len(self.filtered_items):
                selected.append(self.filtered_items[idx])
            idx = self.listCtrl.GetNextSelected(idx)
        return selected

    def _update_button_states(self):
        if not self or not self.listCtrl:
            return
        has_sel = self.listCtrl.GetFirstSelected() != -1
        self.actionBtn.Enable(has_sel)
        self.copyBtn.Enable(has_sel)
        self.removeBtn.Enable(has_sel)

    def _on_list_right_click(self, event):
        if self.listCtrl.GetFirstSelected() == -1:
            event.Skip()
            return
        menu = self.create_video_action_menu()
        self.PopupMenu(menu)
        menu.Destroy()

    def on_list_key_down(self, event):
        key_code = event.GetKeyCode()
        if key_code == wx.WXK_F2:
            self.on_rename_title()
            return
        if event.ControlDown():
            if key_code == ord('C'):
                self.on_list_copy()
                return
            elif key_code == ord('X'):
                self.on_list_cut()
                return
            elif key_code == ord('V'):
                self.on_list_paste()
                return
        if key_code == wx.WXK_DELETE:
            self.on_remove(event)
            return
        if key_code == wx.WXK_TAB and not event.ShiftDown():
            wx.CallAfter(self.treeCtrl.SetFocus)
            return
        self.handle_video_list_keys(event)

    def on_action_menu(self, event):
        if self.listCtrl.GetFirstSelected() == -1:
            return
        menu = self.create_video_action_menu()
        self.PopupMenu(menu)
        menu.Destroy()

    def on_copy_menu(self, event):
        if self.listCtrl.GetFirstSelected() == -1:
            return
        menu = wx.Menu()
        menu.Append(1, _("Copy &Title"))
        menu.Append(2, _("Copy Video &URL"))
        menu.Append(3, _("Copy &Channel Name"))
        menu.Append(4, _("Copy C&hannel URL"))
        menu.AppendSeparator()
        menu.Append(5, _("Copy &Summary"))

        def on_select(e):
            id_map = {1: 'title', 2: 'url', 3: 'channel_name', 4: 'channel_url', 5: 'summary'}
            copy_type = id_map.get(e.GetId())
            if copy_type:
                self.on_copy(copy_type)
        menu.Bind(wx.EVT_MENU, on_select)
        self.PopupMenu(menu)
        menu.Destroy()

    def on_add(self, event):
        try:
            url = api.getClipData()
            if not url or not self.core.is_youtube_url(url):
                ui.message(_("No valid YouTube URL found in clipboard."))
                return
        except Exception:
            ui.message(_("Could not read from clipboard."))
            return
        threading.Thread(target=self._add_worker(), args=(url,), daemon=True).start()

    def on_remove(self, event):
        selected_items = self._get_selected_items()
        if not selected_items:
            return
        first_index = self.listCtrl.GetFirstSelected()
        count = len(selected_items)
        if count == 1:
            title = self._get_item_title_for_messages(selected_items[0])
            confirm_msg = _("Are you sure you want to remove '{title}'?").format(title=title)
        else:
            confirm_msg = _("Are you sure you want to remove {count} selected items?").format(count=count)
        if wx.MessageBox(confirm_msg, _("Confirm Removal"), wx.YES_NO | wx.ICON_QUESTION, self) != wx.YES:
            return
        remove_keys = {self._get_item_unique_key(i) for i in selected_items}
        self.items = [i for i in self.items if self._get_item_unique_key(i) not in remove_keys]
        self._save_data()
        current_search = getattr(self, '_saved_search_text', "")
        self.on_search(current_search)
        item_count = self.listCtrl.GetItemCount()
        if item_count > 0:
            self._focus_item(min(first_index, item_count - 1))
        self._update_button_states()
        wx.CallAfter(self.listCtrl.SetFocus)
        self.core._notify_delete(_("Item removed.") if count == 1 else
                                 _("{count} items removed.").format(count=count))

    def on_rename_title(self):
        selected_items = self._get_selected_items()
        if len(selected_items) != 1:
            return
        item = selected_items[0]
        current_title = item.get('title', '')
        with wx.TextEntryDialog(self, _("Enter new title:"), _("Rename"), value=current_title) as dlg:
            if dlg.ShowModal() != wx.ID_OK:
                return
            new_title = dlg.GetValue().strip()
            if not new_title or new_title == current_title:
                return
        key = self._get_item_unique_key(item)
        for master_item in self.items:
            if self._get_item_unique_key(master_item) == key:
                master_item['title'] = new_title
                break
        self._save_data()
        selected_index = self.listCtrl.GetFirstSelected()
        for i, f_item in enumerate(self.filtered_items):
            if self._get_item_unique_key(f_item) == key:
                f_item['title'] = new_title
                self.listCtrl.SetItem(i, 0, new_title)
                break
        if selected_index != -1:
            self.listCtrl.SetItemState(
                selected_index, wx.LIST_STATE_SELECTED | wx.LIST_STATE_FOCUSED,
                wx.LIST_STATE_SELECTED | wx.LIST_STATE_FOCUSED)
        wx.CallAfter(self.listCtrl.SetFocus)

    # ---------- Sort ----------

    def on_sort(self, event):
        fields = self._get_sort_fields()
        field_labels = [f[1] for f in fields]
        dlg = wx.Dialog(self, title=_("Sort List"))
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(wx.StaticText(dlg, label=_("Sort by:")), 0, wx.ALL, 5)
        fieldCombo = wx.ComboBox(dlg, choices=field_labels, style=wx.CB_READONLY)
        if self._current_sort:
            keys = [f[0] for f in fields]
            sel = keys.index(self._current_sort[0]) if self._current_sort[0] in keys else 0
        else:
            sel = 0
        fieldCombo.SetSelection(sel)
        sizer.Add(fieldCombo, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 5)
        ascRadio = wx.RadioButton(dlg, label=_("&Ascending"), style=wx.RB_GROUP)
        descRadio = wx.RadioButton(dlg, label=_("&Descending"))
        if self._current_sort and not self._current_sort[1]:
            descRadio.SetValue(True)
        else:
            ascRadio.SetValue(True)
        sizer.Add(ascRadio, 0, wx.LEFT | wx.TOP, 5)
        sizer.Add(descRadio, 0, wx.LEFT, 5)

        onlyCurrentCheck = wx.CheckBox(dlg, label=_("Sort only the current &category"))
        onlyCurrentCheck.SetValue(False)
        sizer.Add(onlyCurrentCheck, 0, wx.LEFT | wx.TOP, 8)
        permanentChk = wx.CheckBox(dlg, label=_("&Apply permanently (saves to file)"))
        permanentChk.SetValue(False)
        sizer.Add(permanentChk, 0, wx.LEFT | wx.TOP, 5)

        btnSizer = wx.StdDialogButtonSizer()
        okBtn = wx.Button(dlg, wx.ID_OK)
        cancelBtn = wx.Button(dlg, wx.ID_CANCEL)
        clearBtn = wx.Button(dlg, label=_("C&lear Sort"))
        btnSizer.AddButton(okBtn)
        btnSizer.AddButton(cancelBtn)
        btnSizer.Realize()
        outerBtnSizer = wx.BoxSizer(wx.HORIZONTAL)
        outerBtnSizer.Add(clearBtn, 0, wx.ALL, 5)
        outerBtnSizer.AddStretchSpacer()
        outerBtnSizer.Add(btnSizer, 0)
        sizer.Add(outerBtnSizer, 0, wx.EXPAND | wx.ALL, 5)
        dlg.SetSizer(sizer)
        sizer.Fit(dlg)
        dlg.CentreOnScreen()
        clearBtn.Bind(wx.EVT_BUTTON, lambda e: dlg.EndModal(wx.ID_RESET))

        result = dlg.ShowModal()
        selected_field_key = fields[fieldCombo.GetSelection()][0]
        ascending = ascRadio.GetValue()
        only_current = onlyCurrentCheck.GetValue()
        permanent = permanentChk.GetValue()
        dlg.Destroy()

        if result == wx.ID_RESET:
            self._current_sort = None
            self._load_data()
            current_search = getattr(self, '_saved_search_text', "")
            self.on_search(current_search)
            ui.message(_("Sort cleared."))
            return
        if result != wx.ID_OK:
            return

        self._current_sort = (selected_field_key, ascending)
        self._apply_sort(permanent, only_current)

    def _apply_sort(self, permanent=False, only_current=False):
        if not self._current_sort:
            return
        field_key, ascending = self._current_sort

        # Original duration parser — duration_str is verbose text ("1 Hour 23 Minutes"),
        # produced by core._format_duration_verbose, NOT "H:MM:SS".
        def parse_duration(duration_str):
            if not duration_str:
                return 0
            total = 0
            patterns = {
                'hour': 3600, 'hours': 3600,
                'minute': 60, 'minutes': 60,
                'second': 1, 'seconds': 1,
            }
            for word, multiplier in patterns.items():
                match = re.search(r'(\d+)\s+' + word, duration_str.lower())
                if match:
                    total += int(match.group(1)) * multiplier
            return total

        def sort_key(item):
            val = item.get(field_key, '')
            if val is None:
                val = ''
            if field_key == 'duration_str':
                return parse_duration(str(val))
            return str(val).lower()

        target_cat_id = self._get_cat_id_for_selected_node() if only_current else None

        if permanent:
            if only_current:
                indices = [i for i, v in enumerate(self.items) if v.get("category_id") == target_cat_id]
                subset = sorted((self.items[i] for i in indices), key=sort_key, reverse=not ascending)
                for idx, item in zip(indices, subset):
                    self.items[idx] = item
            else:
                self.items.sort(key=sort_key, reverse=not ascending)
            self._save_data()
            self._current_sort = None
            current_search = getattr(self, '_saved_search_text', "")
            self.on_search(current_search)
            ui.message(_("List sorted and saved."))
        else:
            if only_current:
                indices = [i for i, v in enumerate(self.filtered_items) if v.get("category_id") == target_cat_id]
                subset = sorted((self.filtered_items[i] for i in indices), key=sort_key, reverse=not ascending)
                for idx, item in zip(indices, subset):
                    self.filtered_items[idx] = item
            else:
                self.filtered_items.sort(key=sort_key, reverse=not ascending)
            self._populate_list()
            ui.message(_("List sorted temporarily."))

        if self.listCtrl.GetItemCount() > 0:
            self._focus_item(0)
            wx.CallAfter(self.listCtrl.SetFocus)

    # ---------- Cut / Copy / Paste ----------

    def on_list_copy(self):
        selected = self._get_selected_items()
        if not selected:
            return
        BaseVideoListPanel._clipboard = [dict(i) for i in selected]
        BaseVideoListPanel._clipboard_is_cut = False
        BaseVideoListPanel._clipboard_source = self
        ui.message(_("{count} item(s) copied.").format(count=len(selected)))

    def on_list_cut(self):
        selected = self._get_selected_items()
        if not selected:
            return
        BaseVideoListPanel._clipboard = [dict(i) for i in selected]
        BaseVideoListPanel._clipboard_is_cut = True
        BaseVideoListPanel._clipboard_source = self
        ui.message(_("{count} item(s) cut.").format(count=len(selected)))

    def on_list_paste(self):
        if not BaseVideoListPanel._clipboard:
            ui.message(_("Clipboard is empty."))
            return

        is_same_list = BaseVideoListPanel._clipboard_source is self
        is_cut = BaseVideoListPanel._clipboard_is_cut
        clipboard_keys = [self._get_item_unique_key(i) for i in BaseVideoListPanel._clipboard]
        target_cat_id = self._get_cat_id_for_selected_node()
        cat_name = self._get_cat_name_for_selected_node()

        selected_items = self._get_selected_items()
        if selected_items:
            last_selected = selected_items[-1]
            try:
                insert_pos = self.items.index(last_selected) + 1
            except ValueError:
                insert_pos = len(self.items)
        else:
            insert_pos = len(self.items)

        added_count = 0
        replaced_count = 0
        skipped = 0

        if is_same_list and is_cut:
            items_to_move = [dict(i) for i in BaseVideoListPanel._clipboard]
            move_keys = set(clipboard_keys)
            removed_before = sum(
                1 for i in self.items[:insert_pos]
                if self._get_item_unique_key(i) in move_keys
            )
            adjusted_pos = insert_pos - removed_before
            self.items = [i for i in self.items if self._get_item_unique_key(i) not in move_keys]
            for offset, item in enumerate(items_to_move):
                item["category_id"] = target_cat_id
                self.items.insert(adjusted_pos + offset, item)
            self._save_data()
            added_count = len(items_to_move)
            BaseVideoListPanel._clipboard = []
            BaseVideoListPanel._clipboard_is_cut = False
            BaseVideoListPanel._clipboard_source = None

        else:
            existing_keys = {self._get_item_unique_key(i) for i in self.items}
            if is_same_list and not is_cut:
                existing_keys -= set(clipboard_keys)

            duplicate_items = [] if is_same_list else [
                i for i in BaseVideoListPanel._clipboard
                if self._get_item_unique_key(i) in existing_keys
            ]

            replace_duplicates = False
            if duplicate_items:
                source_name = self._get_list_display_name(BaseVideoListPanel._clipboard_source)
                dest_name = self._get_list_display_name(self)
                op = _("Cut") if is_cut else _("Copy")
                dup_count = len(duplicate_items)
                if dup_count == 1:
                    title = self._get_item_title_for_messages(duplicate_items[0])
                    confirm_msg = _(
                        "{op} '{title}' from {src} to {dst} — this item already exists. Replace it?"
                    ).format(op=op, title=title, src=source_name, dst=dest_name)
                else:
                    confirm_msg = _(
                        "{op} from {src} to {dst} — {count} item(s) already exist. Replace all?"
                    ).format(op=op, count=dup_count, src=source_name, dst=dest_name)
                replace_duplicates = (
                    wx.MessageBox(confirm_msg, _("Confirm Replace"),
                                  wx.YES_NO | wx.ICON_QUESTION, self) == wx.YES
                )

            for item in BaseVideoListPanel._clipboard:
                key = self._get_item_unique_key(item)
                if key in existing_keys:
                    if replace_duplicates:
                        for i, existing in enumerate(self.items):
                            if self._get_item_unique_key(existing) == key:
                                new_item = self._sanitize_pasted_item(item)
                                new_item["category_id"] = target_cat_id
                                self.items[i] = new_item
                                break
                        replaced_count += 1
                    else:
                        skipped += 1
                else:
                    new_item = self._sanitize_pasted_item(item)
                    new_item["category_id"] = target_cat_id
                    self.items.insert(insert_pos + added_count, new_item)
                    existing_keys.add(key)
                    added_count += 1

            if added_count or replaced_count:
                self._save_data()

            if is_cut and not is_same_list:
                source = BaseVideoListPanel._clipboard_source
                cut_keys = set(clipboard_keys)
                src_focused_item, src_focused_idx = self._get_focused_item(source)
                source.items = [i for i in source.items
                                 if self._get_item_unique_key(i) not in cut_keys]
                source._save_data()
                source.on_search("")
                self._restore_focus(source, src_focused_item, src_focused_idx)
                source._update_button_states()

            if is_cut:
                BaseVideoListPanel._clipboard = []
                BaseVideoListPanel._clipboard_is_cut = False
                BaseVideoListPanel._clipboard_source = None

        self.on_search("")

        if added_count:
            inserted_keys = set(clipboard_keys[:added_count])
            for idx in range(self.listCtrl.GetItemCount()):
                if self._get_item_unique_key(self.filtered_items[idx]) in inserted_keys:
                    self._focus_item(idx)
                    break
        elif is_same_list and is_cut:
            for idx in range(self.listCtrl.GetItemCount()):
                if self._get_item_unique_key(self.filtered_items[idx]) in set(clipboard_keys):
                    self._focus_item(idx)
                    break
        else:
            if selected_items:
                sel_idx = self.listCtrl.GetFirstSelected()
                self._restore_focus(self, selected_items[-1], max(sel_idx, 0))

        self._update_button_states()

        total_done = added_count + replaced_count
        if total_done > 0 and skipped == 0:
            msg = _("{count} item(s) pasted to {cat}.").format(count=total_done, cat=cat_name)
        elif total_done > 0 and skipped > 0:
            msg = _("{done} item(s) pasted to {cat}, {skipped} skipped.").format(
                done=total_done, cat=cat_name, skipped=skipped)
        else:
            msg = _("All items already exist in this list.")
        ui.message(msg)

    def _restore_focus(self, panel, anchor_item, anchor_idx):
        count = panel.listCtrl.GetItemCount()
        if count == 0:
            return
        if anchor_item is not None:
            try:
                idx = panel.filtered_items.index(anchor_item)
                panel._focus_item(idx)
                return
            except ValueError:
                pass
        idx = min(anchor_idx, count - 1)
        panel._focus_item(idx)

    def _get_list_display_name(self, panel):
        return getattr(panel, '_list_display_name', panel.__class__.__name__)

    def _get_focused_item(self, panel):
        idx = panel.listCtrl.GetFirstSelected()
        if idx != -1 and idx < len(panel.filtered_items):
            return panel.filtered_items[idx], idx
        return None, -1

class FavVideoPanel(BaseVideoListPanel):
    _CONF_KEY = "favVideoLastCatId"
    _list_display_name = _("Favorite Videos")

    def _get_file_path(self):
        return self.core.get_profile_path("fav_video.json")

    def _get_category_file_path(self):
        return self.core.get_profile_path("fav_video_categories.json")

    def _get_callback_topic(self):
        return "fav_video_updated"

    def _get_add_button_label(self):
        return _("Add &new favorite video from clipboard")

    def _get_default_category_label(self):
        return _("Videos")

    def _add_worker(self):
        return self.core.add_item_to_favorites_worker

class WatchListPanel(BaseVideoListPanel):
    _CONF_KEY = "watchListLastCatId"
    _list_display_name = _("Watch List")

    def _get_file_path(self):
        return self.core.get_profile_path("watch_list.json")

    def _get_category_file_path(self):
        return self.core.get_profile_path("watch_list_categories.json")

    def _get_callback_topic(self):
        return "watch_list_updated"

    def _get_add_button_label(self):
        return _("Add &new watch list from clipboard")

    def _get_default_category_label(self):
        return _("Watch List")

    def _add_worker(self):
        return self.core.add_to_watchlist_worker

    def _sanitize_pasted_item(self, item):
        return dict(item)

class FavChannelPanel(wx.Panel):
    def __init__(self, parent, core_instance):
        wx.Panel.__init__(self, parent)
        self.core = core_instance
        self.channel = []
        self.filtered_channel = []
        self._is_first_load = True
        self.last_selected_item_before_search = None
        self._current_sort = None
        self._is_programmatic_selection = False
        self.fav_file_path = self.core.get_profile_path("fav_channel.json")
        #_escape_protection = True   

        mainSizer = wx.BoxSizer(wx.VERTICAL)

        self.listCtrl = wx.ListCtrl(self, style=wx.LC_REPORT)
        # translator: Column header for the channel name
        self.listCtrl.InsertColumn(0, _("Channel"), width=450)
        # translator: Column header for the number of subscribers
        self.listCtrl.InsertColumn(1, _("Subscribers"), width=150)
        mainSizer.Add(self.listCtrl, 1, wx.EXPAND | wx.ALL, 5)
        # translator: The label for the box that displays the selected channel's details/description
        self.descriptionBox = wx.StaticBoxSizer(wx.VERTICAL, self, label=_("Channel Description"))
        self.descriptionText = wx.TextCtrl(self, style=wx.TE_MULTILINE | wx.TE_READONLY)
        self.descriptionBox.Add(self.descriptionText, 1, wx.EXPAND | wx.ALL, 5)
        mainSizer.Add(self.descriptionBox, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 5)

        btnSizer = wx.BoxSizer(wx.HORIZONTAL)
        # translator: Button to open the selected channel URL in a browser. The '&' precedes the shortcut key.
        self.openBtn = wx.Button(self, label=_("Open channel on &browser"))
        # Translators: Button to view content of the selected channel.
        self.viewContentBtn = wx.Button(self, label=_("View &channel Content..."))
        # Translators: Button to add a new channel from clipboard content.
        self.addBtn = wx.Button(self, label=_("Add &new favorite channel from clipboard"))
        # translator: Button to remove the selected channel from favorites. The '&' precedes the shortcut key.
        self.removeBtn = wx.Button(self, label=_("&Remove"))

        btnSizer.Add(self.openBtn, 0, wx.RIGHT, 5)
        btnSizer.Add(self.viewContentBtn, 0, wx.RIGHT, 5)
        btnSizer.AddStretchSpacer()
        btnSizer.Add(self.addBtn, 0, wx.RIGHT, 5)
        btnSizer.Add(self.removeBtn, 0, wx.RIGHT, 5)
        mainSizer.Add(btnSizer, 0, wx.EXPAND | wx.ALL, 10)

        self.SetSizer(mainSizer)
        self.core.register_callback("fav_channel_updated", self.refresh_favChannel)
        self._load_channel()
        self._populate_list()
        has_any_items = self.listCtrl.GetItemCount() > 0
        self.descriptionBox.GetStaticBox().Show(has_any_items)
        self._update_button_states()

        self.addBtn.Bind(wx.EVT_BUTTON, self.on_add)
        self.removeBtn.Bind(wx.EVT_BUTTON, self.on_remove)
        self.openBtn.Bind(wx.EVT_BUTTON, self.on_open)
        self.viewContentBtn.Bind(wx.EVT_BUTTON, self.on_view_channel_content)
        self.listCtrl.Bind(wx.EVT_LIST_ITEM_SELECTED, self._on_channel_select)
        self.listCtrl.Bind(wx.EVT_LIST_ITEM_DESELECTED, self._on_channel_select)
        self.listCtrl.Bind(wx.EVT_KEY_DOWN, self.on_list_key_down)
        
    def _on_channel_select(self, event):
        if self._is_programmatic_selection:
            return
        selected_index = self.listCtrl.GetFirstSelected()
        if selected_index != -1:
            item = self.filtered_channel[selected_index]
            # Translators: Default text when no description is available.
            self.descriptionText.SetValue(item.get('description', _("N/A")))
        else:
            self.descriptionText.SetValue("")

    def on_close(self, event):
        self.core.unregister_callback("fav_channel_updated", self.refresh_favChannel)
        self._save_channel()
        
    def refresh_favChannel(self, data=None):
        if not self.listCtrl:
            return
        self._load_channel()
        self.on_search("")
        if data and data.get("action") == "add":
            item_count = self.listCtrl.GetItemCount()
            if item_count > 0:
                last_index = item_count - 1
                self.listCtrl.SetItemState(last_index, wx.LIST_STATE_SELECTED | wx.LIST_STATE_FOCUSED, wx.LIST_STATE_SELECTED | wx.LIST_STATE_FOCUSED)
                self.listCtrl.EnsureVisible(last_index)
        self._update_button_states()
    
    def on_add(self, event):
        try:
            url = api.getClipData()
            if not url or not self.core.is_youtube_url(url):
                # Translators: Message shown when no valid YouTube URL is in the clipboard.
                ui.message(_("No valid YouTube URL found in clipboard."))
                return
        except:
            # Translators: Error message when the clipboard cannot be read.
            ui.message(_("Could not read from clipboard."))
            return
        threading.Thread(target=self.core.add_channel_to_favorites_worker, args=(url,), daemon=True).start()

    def _load_channel(self):
        with self.core._fav_file_lock:
            try:
                with open(self.fav_file_path, 'r', encoding='utf-8') as f:
                    self.channel = json.load(f)
            except (FileNotFoundError, json.JSONDecodeError):
                self.channel = []
        self.filtered_channel = self.channel[:]

    def _save_channel(self):
        with self.core._fav_file_lock:
            with open(self.fav_file_path, 'w', encoding='utf-8') as f:
                json.dump(self.channel, f, indent=2, ensure_ascii=False)

    def _populate_list(self):
        self.listCtrl.Freeze()
        try:
            self.listCtrl.DeleteAllItems()
            for index, item in enumerate(self.filtered_channel):
                self.listCtrl.InsertItem(index, item.get('channel_name', 'N/A'))
                sub_count = item.get('subscriber_count')
                sub_count_str = str(sub_count) if sub_count is not None else _("N/A")
                self.listCtrl.SetItem(index, 1, sub_count_str)
            if self._is_first_load and self.listCtrl.GetItemCount() > 0:
                self.listCtrl.SetItemState(0, wx.LIST_STATE_SELECTED | wx.LIST_STATE_FOCUSED, wx.LIST_STATE_SELECTED | wx.LIST_STATE_FOCUSED)
                self._is_first_load = False
        finally:
            self.listCtrl.Thaw()
            
    def on_search(self, search_text):
        search_text = search_text.lower()
        if search_text and self.last_selected_item_before_search is None:
            selected_index = self.listCtrl.GetFirstSelected()
            if selected_index != -1:
                self.last_selected_item_before_search = self.filtered_channel[selected_index]
        if search_text:
            self.filtered_channel = [item for item in self.channel if search_text in item.get('channel_name', '').lower()]
        else:
            self.filtered_channel = self.channel[:]
        self._populate_list()
        if not search_text and self.last_selected_item_before_search:
            try:
                new_index = self.filtered_channel.index(self.last_selected_item_before_search)
                self.listCtrl.SetItemState(new_index, wx.LIST_STATE_SELECTED | wx.LIST_STATE_FOCUSED, wx.LIST_STATE_SELECTED | wx.LIST_STATE_FOCUSED)
                self.listCtrl.EnsureVisible(new_index)
            except ValueError:
                if self.listCtrl.GetItemCount() > 0:
                    self.listCtrl.SetItemState(0, wx.LIST_STATE_SELECTED | wx.LIST_STATE_FOCUSED, wx.LIST_STATE_SELECTED | wx.LIST_STATE_FOCUSED)
            self.last_selected_item_before_search = None
        elif search_text and self.listCtrl.GetItemCount() > 0:
            self.listCtrl.SetItemState(0, wx.LIST_STATE_SELECTED | wx.LIST_STATE_FOCUSED, wx.LIST_STATE_SELECTED | wx.LIST_STATE_FOCUSED)
            self.listCtrl.EnsureVisible(0)
            
    def _update_button_states(self):
        has_selection = self.listCtrl.GetFirstSelected() != -1
        self.openBtn.Enable(has_selection)
        self.viewContentBtn.Enable(has_selection)
        self.removeBtn.Enable(has_selection)
        has_any_items = self.listCtrl.GetItemCount() > 0
        if self.descriptionBox.GetStaticBox().IsShown() != has_any_items:
            self.descriptionBox.GetStaticBox().Show(has_any_items)
            self.descriptionBox.ShowItems(has_any_items)
            self.GetSizer().Layout()
        
    def on_remove(self, event):
        selected = []
        idx = self.listCtrl.GetFirstSelected()
        while idx != -1:
            selected.append(idx)
            idx = self.listCtrl.GetNextSelected(idx)
        if not selected:
            return
        first_index = selected[0]
        count = len(selected)
        if count == 1:
            channel_name = self.filtered_channel[selected[0]].get('channel_name', _("this channel"))
            # Translators: Confirmation message before removing a single channel. {name} is the channel name.
            confirm_msg = _("Are you sure you want to remove '{name}'?").format(name=channel_name)
        else:
            # Translators: Confirmation message before removing multiple channels. {count} is the number of channels.
            confirm_msg = _("Are you sure you want to remove {count} selected channels?").format(count=count)
        # Translators: Title of the removal confirmation dialog.
        if wx.MessageBox(confirm_msg, _("Confirm Removal"), wx.YES_NO | wx.ICON_QUESTION) != wx.YES:
            return
        items_to_remove = [self.filtered_channel[i] for i in selected]
        for item in items_to_remove:
            self.channel.remove(item)
        self._save_channel()
        current_search = getattr(self, '_saved_search_text', "")
        self.on_search(current_search)
        #self.on_search("")
        item_count = self.listCtrl.GetItemCount()
        if item_count > 0:
            new_selection = min(first_index, item_count - 1)
            self.listCtrl.SetItemState(new_selection,
                wx.LIST_STATE_SELECTED | wx.LIST_STATE_FOCUSED,
                wx.LIST_STATE_SELECTED | wx.LIST_STATE_FOCUSED)
            self.listCtrl.EnsureVisible(new_selection)
        self._update_button_states()
        wx.CallAfter(self.listCtrl.SetFocus)
        # Translators: Notification after one channel is successfully removed.
        # Translators: Notification after multiple channels are successfully removed. {count} is the number removed.
        self.core._notify_delete(_("Channel removed.") if count == 1 else
                                 _("{count} channels removed.").format(count=count))
                                 
    def on_open(self, event):
        selected_index = self.listCtrl.GetFirstSelected()
        if selected_index == -1: return
        item = self.filtered_channel[selected_index]
        if item.get("channel_url"): webbrowser.open(item.get("channel_url"))
    
    def on_view_channel_content(self, event):
        selected_index = self.listCtrl.GetFirstSelected()
        if selected_index == -1: return
        item = self.filtered_channel[selected_index]
        channel_url = item.get("channel_url")
        channel_name = item.get("channel_name")
        if not channel_url:
            return ui.message(_("Error: Channel URL not found."))
        menu = wx.Menu()
        menu_choices = {
            wx.ID_HIGHEST + 1: (_("Videos"),    "/videos",    False),
            wx.ID_HIGHEST + 2: (_("Shorts"),    "/shorts",    False),
            wx.ID_HIGHEST + 3: (_("Live"),      "/streams",   False),
            wx.ID_HIGHEST + 4: (_("Playlists"), "/playlists", True),
            wx.ID_HIGHEST + 5: (_("Podcasts"),  "/podcasts",  True),
        }
        for menu_id, (label, suffix, is_col) in menu_choices.items():
            menu.Append(menu_id, label)
        def on_menu_select(e):
            label, suffix, is_collection = menu_choices.get(e.GetId())
            full_url = channel_url.rstrip('/') + suffix
            title_template = _("Fetching {type} from {channel}...").format(channel=channel_name, type=label)
            thread_kwargs = {
                'url': full_url,
                'dialog_title_template': title_template,
                'content_type_label': label,
                'base_channel_url': channel_url,
                'base_channel_name': channel_name,
                'is_collection': is_collection,
            }
            threading.Thread(target=self.core._view_channel_worker, kwargs=thread_kwargs, daemon=True).start()
        menu.Bind(wx.EVT_MENU, on_menu_select)
        self.PopupMenu(menu)
        menu.Destroy()
        
    def on_list_key_down(self, event):
        key_code = event.GetKeyCode()
        if key_code == wx.WXK_F2:
            self.on_rename_channel() 
            return
        if event.ControlDown():
            if key_code == ord('X'):
                self.on_list_cut()
                return
            elif key_code == ord('V'):
                self.on_list_paste()
                return
            elif key_code == ord('C'):
                self.on_list_copy()
                return
        if key_code in [wx.WXK_RETURN, wx.WXK_NUMPAD_ENTER, wx.WXK_SPACE]:
            self.on_open(event) 
        elif key_code == wx.WXK_DELETE:
            self.on_remove(event)
        else:
            event.Skip()
        
    def on_list_cut(self):
        selected = []
        idx = self.listCtrl.GetFirstSelected()
        while idx != -1:
            selected.append(idx)
            idx = self.listCtrl.GetNextSelected(idx)
        if not selected:
            return
        self._cut_indices = selected
        # Translators: Notification spoken by NVDA after cutting one or more channel items ready to be moved.
        ui.message(_("Cut."))

    def on_list_paste(self):
        if not hasattr(self, '_cut_indices') or not self._cut_indices:
            # Translators: Notification when there is nothing to paste.
            ui.message(_("Clipboard is empty."))
            return
        target_index = self.listCtrl.GetFirstSelected()
        if target_index == -1:
            self._cut_indices = None
            return
        items_to_move = [self.filtered_channel[i] for i in self._cut_indices]
        self.filtered_channel = [item for i, item in enumerate(self.filtered_channel) if i not in self._cut_indices]
        insert_pos = target_index - sum(1 for i in self._cut_indices if i < target_index)+1
        for offset, item in enumerate(items_to_move):
            self.filtered_channel.insert(insert_pos + offset, item)
        self.channel = self.filtered_channel[:]
        self._save_channel()
        self._populate_list()
        for offset in range(len(items_to_move)):
            self.listCtrl.SetItemState(insert_pos + offset,
                wx.LIST_STATE_SELECTED | wx.LIST_STATE_FOCUSED,
                wx.LIST_STATE_SELECTED | wx.LIST_STATE_FOCUSED)
        self.listCtrl.EnsureVisible(insert_pos)
        self._cut_indices = None
        # Translators: Notification spoken by NVDA after one or more channel items are successfully moved.
        ui.message(_("Moved."))

    def _get_sort_fields(self):
        return [
            # Translators: Sort field option for channel name.
            ('channel_name', _("Channel")),
            # Translators: Sort field option for subscriber count.
            ('subscriber_count', _("Subscribers")),
            # Translators: Sort field option for date added to the list.
            ('added_at', _("Date Added")),
        ]

    def on_sort(self, event):
        fields = self._get_sort_fields()
        field_labels = [f[1] for f in fields]
        dlg = wx.Dialog(self, title=_("Sort List"))
        sizer = wx.BoxSizer(wx.VERTICAL)
        # Translators: Label for sort field selection.
        sizer.Add(wx.StaticText(dlg, label=_("Sort by:")), 0, wx.ALL, 5)
        fieldCombo = wx.ComboBox(dlg, choices=field_labels, style=wx.CB_READONLY)
        if self._current_sort:
            current_keys = [f[0] for f in fields]
            if self._current_sort[0] in current_keys:
                fieldCombo.SetSelection(current_keys.index(self._current_sort[0]))
            else:
                fieldCombo.SetSelection(0)
        else:
            fieldCombo.SetSelection(0)
        sizer.Add(fieldCombo, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 5)
        # Translators: Radio button for ascending sort order.
        ascRadio = wx.RadioButton(dlg, label=_("&Ascending"), style=wx.RB_GROUP)
        # Translators: Radio button for descending sort order.
        descRadio = wx.RadioButton(dlg, label=_("&Descending"))
        if self._current_sort and not self._current_sort[1]:
            descRadio.SetValue(True)
        else:
            ascRadio.SetValue(True)
        sizer.Add(ascRadio, 0, wx.LEFT | wx.TOP, 5)
        sizer.Add(descRadio, 0, wx.LEFT, 5)
        # Translators: Checkbox to apply sort permanently to the saved file.
        permanentChk = wx.CheckBox(dlg, label=_("&Apply permanently (saves to file)"))
        sizer.Add(permanentChk, 0, wx.ALL, 5)
        btnSizer = wx.StdDialogButtonSizer()
        okBtn = wx.Button(dlg, wx.ID_OK)
        cancelBtn = wx.Button(dlg, wx.ID_CANCEL)
        # Translators: Button to clear current sort and restore original order.
        clearBtn = wx.Button(dlg, label=_("C&lear Sort"))
        btnSizer.AddButton(okBtn)
        btnSizer.AddButton(cancelBtn)
        btnSizer.Realize()
        outerBtnSizer = wx.BoxSizer(wx.HORIZONTAL)
        outerBtnSizer.Add(clearBtn, 0, wx.ALL, 5)
        outerBtnSizer.AddStretchSpacer()
        outerBtnSizer.Add(btnSizer, 0)
        sizer.Add(outerBtnSizer, 0, wx.EXPAND | wx.ALL, 5)
        dlg.SetSizer(sizer)
        sizer.Fit(dlg)
        dlg.CentreOnScreen()
        def on_clear(e):
            dlg.EndModal(wx.ID_RESET)
        clearBtn.Bind(wx.EVT_BUTTON, on_clear)
        result = dlg.ShowModal()
        selected_field_key = fields[fieldCombo.GetSelection()][0]
        ascending = ascRadio.GetValue()
        permanent = permanentChk.GetValue()
        dlg.Destroy()
        if result == wx.ID_RESET:
            self._current_sort = None
            self._load_channel()
            self.on_search("")
            # Translators: Notification after sort is cleared and original order is restored.
            ui.message(_("Sort cleared."))
            return
        if result != wx.ID_OK:
            return
        self._current_sort = (selected_field_key, ascending)
        self._apply_sort(permanent)

    def _apply_sort(self, permanent=False):
        if not self._current_sort:
            return
        field_key, ascending = self._current_sort
        def sort_key(item):
            val = item.get(field_key, '')
            if val is None:
                val = ''
            try:
                return (0, int(val))
            except (ValueError, TypeError):
                return (1, str(val).lower())
        if permanent:
            self.channel.sort(key=sort_key, reverse=not ascending)
            self._save_channel()
            self._current_sort = None
            self.on_search("")
            # Translators: Notification after sort is applied permanently and saved.
            ui.message(_("List sorted and saved."))
        else:
            self.filtered_channel.sort(key=sort_key, reverse=not ascending)
            self._populate_list()
            # Translators: Notification after temporary sort is applied.
            ui.message(_("List sorted temporarily."))
        if self.listCtrl.GetItemCount() > 0:
            self.listCtrl.SetItemState(0,
                wx.LIST_STATE_SELECTED | wx.LIST_STATE_FOCUSED,
                wx.LIST_STATE_SELECTED | wx.LIST_STATE_FOCUSED)
            self.listCtrl.EnsureVisible(0)
            wx.CallAfter(self.listCtrl.SetFocus)

    def on_rename_channel(self):
        selected = []
        idx = self.listCtrl.GetFirstSelected()
        while idx != -1:
            selected.append(idx)
            idx = self.listCtrl.GetNextSelected(idx)
        if len(selected) != 1:
            return
        selected_index = selected[0]
        item = self.filtered_channel[selected_index]
        current_name = item.get('channel_name', '')
        # Translators: Prompt shown when renaming a channel title.
        with wx.TextEntryDialog(
            self,
            _("Enter new channel name:"),
            _("Rename Channel"),
            value=current_name
        ) as dlg:
            if dlg.ShowModal() != wx.ID_OK:
                return
            new_name = dlg.GetValue().strip()
            if not new_name or new_name == current_name:
                return
        for i, master_item in enumerate(self.channel):
            if master_item == item:
                self.channel[i]['channel_name'] = new_name
                break
        self.filtered_channel[selected_index]['channel_name'] = new_name
        self.listCtrl.SetItem(selected_index, 0, new_name)
        self._save_channel()
        self.listCtrl.SetItemState(
            selected_index,
            wx.LIST_STATE_SELECTED | wx.LIST_STATE_FOCUSED,
            wx.LIST_STATE_SELECTED | wx.LIST_STATE_FOCUSED
        )
        wx.CallAfter(self.listCtrl.SetFocus)
        
class FavPlaylistPanel(wx.Panel):
    def __init__(self, parent, core_instance):
        wx.Panel.__init__(self, parent)
        self.core = core_instance
        self.playlists = []
        self.filtered_playlists = []
        self._is_first_load = True
        self.last_selected_item_before_search = None
        self._current_sort = None
        self.fav_file_path = self.core.get_profile_path("fav_playlist.json")
        #_escape_protection = True   

        mainSizer = wx.BoxSizer(wx.VERTICAL)

        self.listCtrl = wx.ListCtrl(self, style=wx.LC_REPORT)
        # Translators: Column header for the title of a playlist.
        self.listCtrl.InsertColumn(0, _("Playlist Title"), width=350)
        # Translators: Column header for the name of the channel/uploader.
        self.listCtrl.InsertColumn(1, _("Channel"), width=200)
        # Translators: Column header for the number of videos in a playlist.
        self.listCtrl.InsertColumn(2, _("Videos"), width=80)
        mainSizer.Add(self.listCtrl, 1, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 10)

        btnSizer = wx.BoxSizer(wx.HORIZONTAL)
        # Translators: Button to show videos within the selected playlist.
        self.showVideosBtn = wx.Button(self, label=_("Show &Videos..."))
        # Translators: Button to open the playlist on the YouTube website.
        self.openWebBtn = wx.Button(self, label=_("Open on &browser"))
        # Translators: Button to add a new favorite playlist from the clipboard.
        self.addBtn = wx.Button(self, label=_("Add &new favorite playlist from clipboard"))
        # Translators: Button to remove the selected playlist from favorites.
        self.removeBtn = wx.Button(self, label=_("&Remove"))

        btnSizer.Add(self.showVideosBtn, 0, wx.RIGHT, 5)
        btnSizer.Add(self.openWebBtn, 0, wx.RIGHT, 5)
        btnSizer.AddStretchSpacer()
        btnSizer.Add(self.addBtn, 0, wx.RIGHT, 5)
        btnSizer.Add(self.removeBtn, 0, wx.RIGHT, 5)
        mainSizer.Add(btnSizer, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 10)

        self.SetSizer(mainSizer)
        
        self.core.register_callback("fav_playlist_updated", self.refresh_favPlaylists)
        self.core.register_callback("fav_playlist_item_updated", self.on_playlist_item_update)
        self._load_playlists()
        self._populate_list()  
        self._update_button_states()

        self.showVideosBtn.Bind(wx.EVT_BUTTON, self.on_show_videos)
        self.openWebBtn.Bind(wx.EVT_BUTTON, self.on_open_web)
        self.addBtn.Bind(wx.EVT_BUTTON, self.on_add)
        self.removeBtn.Bind(wx.EVT_BUTTON, self.on_remove)
        self.listCtrl.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.on_show_videos)
        self.listCtrl.Bind(wx.EVT_KEY_DOWN, self.on_list_key_down)
        
    def on_close(self, event):
        self.core.unregister_callback("fav_playlist_updated", self.refresh_favPlaylists)
        self.core.unregister_callback("fav_playlist_item_updated", self.on_playlist_item_update)
        self._save_playlists()

    def on_playlist_item_update(self, data):
        """Handles a targeted update for a single playlist's video count."""
        playlist_id = data.get('playlist_id')
        new_count = data.get('new_count')
        if not playlist_id or new_count is None:
            return
        for index, item in enumerate(self.filtered_playlists):
            if item.get('playlist_id') == playlist_id:
                item['video_count'] = new_count
                self.listCtrl.SetItem(index, 2, str(new_count))
                break

    def on_list_key_down(self, event):
        key_code = event.GetKeyCode()
        if key_code == wx.WXK_F2:
            self.on_rename_playlist()
            return
        if event.ControlDown():
            if key_code == ord('X'):
                self.on_list_cut()
                return
            elif key_code == ord('V'):
                self.on_list_paste()
                return
            elif key_code == ord('C'):
                self.on_list_copy()
                return
        if key_code == wx.WXK_RETURN or key_code == wx.WXK_SPACE:
            self.on_show_videos(event) 
        elif key_code == wx.WXK_DELETE:
            self.on_remove(event)
        else:
            event.Skip()
        
    def on_list_cut(self):
        selected = []
        idx = self.listCtrl.GetFirstSelected()
        while idx != -1:
            selected.append(idx)
            idx = self.listCtrl.GetNextSelected(idx)
        if not selected:
            return
        self._cut_indices = selected
        # Translators: Notification spoken by NVDA after cutting one or more playlist items ready to be moved.
        ui.message(_("Cut."))

    def on_list_paste(self):
        if not hasattr(self, '_cut_indices') or not self._cut_indices:
            # Translators: Notification when there is nothing to paste.
            ui.message(_("Clipboard is empty."))
            return
        target_index = self.listCtrl.GetFirstSelected()
        if target_index == -1:
            self._cut_indices = None
            return
        items_to_move = [self.filtered_playlists[i] for i in self._cut_indices]
        self.filtered_playlists = [item for i, item in enumerate(self.filtered_playlists) if i not in self._cut_indices]
        insert_pos = target_index - sum(1 for i in self._cut_indices if i < target_index)+1
        for offset, item in enumerate(items_to_move):
            self.filtered_playlists.insert(insert_pos + offset, item)
        self.playlists = self.filtered_playlists[:]
        self._save_playlists()
        self._populate_list()
        for offset in range(len(items_to_move)):
            self.listCtrl.SetItemState(insert_pos + offset,
                wx.LIST_STATE_SELECTED | wx.LIST_STATE_FOCUSED,
                wx.LIST_STATE_SELECTED | wx.LIST_STATE_FOCUSED)
        self.listCtrl.EnsureVisible(insert_pos)
        self._cut_indices = None
        # Translators: Notification spoken by NVDA after one or more playlist items are successfully moved.
        ui.message(_("Moved."))
        
    def _update_button_states(self):
        has_items = self.listCtrl.GetItemCount() > 0
        self.showVideosBtn.Enable(has_items)
        self.openWebBtn.Enable(has_items)
        self.removeBtn.Enable(has_items)
    
    def on_remove(self, event):
        selected = []
        idx = self.listCtrl.GetFirstSelected()
        while idx != -1:
            selected.append(idx)
            idx = self.listCtrl.GetNextSelected(idx)
        if not selected:
            return
        first_index = selected[0]
        count = len(selected)
        if count == 1:
            title = self.filtered_playlists[selected[0]].get('playlist_title', _("this playlist"))
            # Translators: Confirmation message before removing a single playlist. {title} is the playlist title.
            confirm_msg = _("Are you sure you want to remove '{title}'?").format(title=title)
        else:
            # Translators: Confirmation message before removing multiple playlists. {count} is the number of playlists.
            confirm_msg = _("Are you sure you want to remove {count} selected playlists?").format(count=count)
        # Translators: Title of the removal confirmation dialog.
        if wx.MessageBox(confirm_msg, _("Confirm Removal"), wx.YES_NO | wx.ICON_QUESTION, self) != wx.YES:
            return
        items_to_remove = [self.filtered_playlists[i] for i in selected]
        for item in items_to_remove:
            self.playlists.remove(item)
        self._save_playlists()
        current_search = getattr(self, '_saved_search_text', "")
        self.on_search(current_search)
        #self.on_search("")
        item_count = self.listCtrl.GetItemCount()
        if item_count > 0:
            new_selection = min(first_index, item_count - 1)
            self.listCtrl.SetItemState(new_selection,
                wx.LIST_STATE_SELECTED | wx.LIST_STATE_FOCUSED,
                wx.LIST_STATE_SELECTED | wx.LIST_STATE_FOCUSED)
            self.listCtrl.EnsureVisible(new_selection)
        self._update_button_states()
        wx.CallAfter(self.listCtrl.SetFocus)
        # Translators: Notification after one playlist is successfully removed.
        # Translators: Notification after multiple playlists are successfully removed. {count} is the number removed.
        self.core._notify_delete(_("Playlist removed.") if count == 1 else
                                 _("{count} playlists removed.").format(count=count))        
                                 
    def _load_playlists(self):
        with self.core._fav_file_lock:
            try:
                with open(self.fav_file_path, 'r', encoding='utf-8') as f:
                    self.playlists = json.load(f)
            except (FileNotFoundError, json.JSONDecodeError):
                self.playlists = []
        self.filtered_playlists = self.playlists[:]

    def _save_playlists(self):
        with self.core._fav_file_lock:
            try:
                with open(self.fav_file_path, 'w', encoding='utf-8') as f:
                    json.dump(self.playlists, f, indent=2, ensure_ascii=False)
            except IOError:
                # Translators: Error message when playlist data cannot be saved.
                ui.message(_("Error: Could not save playlist list."))

    def on_add(self, event):
        try:
            url = api.getClipData()
            list_match = re.search(r'[?&]list=([^&]+)', url or "")
            if not url or not self.core.is_youtube_url(url) or not list_match:
                # Translators: Message shown when the clipboard does not contain a valid YouTube playlist URL.
                ui.message(_("No valid YouTube playlist URL found in clipboard."))
                return
        except Exception:
            # Translators: Error message when the clipboard is inaccessible.
            ui.message(_("Could not read from clipboard."))
            return
        threading.Thread(target=self.core.add_playlist_to_favorites_worker, args=(url,), daemon=True).start()

    def on_search(self, search_text):
        search_text = search_text.lower()
        if search_text and self.last_selected_item_before_search is None:
            selected_index = self.listCtrl.GetFirstSelected()
            if selected_index != -1:
                self.last_selected_item_before_search = self.filtered_playlists[selected_index]
        if search_text:
            self.filtered_playlists = [
                item for item in self.playlists
                if search_text in item.get('playlist_title', '').lower() or 
                   search_text in item.get('uploader', '').lower()
            ]
        else:
            self.filtered_playlists = self.playlists[:]
        self._populate_list()
        if not search_text and self.last_selected_item_before_search:
            try:
                new_index = self.filtered_playlists.index(self.last_selected_item_before_search)
                self.listCtrl.SetItemState(new_index, wx.LIST_STATE_SELECTED | wx.LIST_STATE_FOCUSED, wx.LIST_STATE_SELECTED | wx.LIST_STATE_FOCUSED)
                self.listCtrl.EnsureVisible(new_index)
            except ValueError:
                if self.listCtrl.GetItemCount() > 0:
                    self.listCtrl.SetItemState(0, wx.LIST_STATE_SELECTED | wx.LIST_STATE_FOCUSED, wx.LIST_STATE_SELECTED | wx.LIST_STATE_FOCUSED)
            self.last_selected_item_before_search = None
        elif search_text and self.listCtrl.GetItemCount() > 0:
            self.listCtrl.SetItemState(0, wx.LIST_STATE_SELECTED | wx.LIST_STATE_FOCUSED, wx.LIST_STATE_SELECTED | wx.LIST_STATE_FOCUSED)
            self.listCtrl.EnsureVisible(0)
            
    def _populate_list(self):
        self.listCtrl.Freeze()
        try:
            self.listCtrl.DeleteAllItems()
            for index, item in enumerate(self.filtered_playlists):
                # Translators: Default text for playlist title or channel if missing.
                default_val = _("N/A")
                self.listCtrl.InsertItem(index, item.get('playlist_title', default_val))
                self.listCtrl.SetItem(index, 1, item.get('uploader', 'N/A'))
                self.listCtrl.SetItem(index, 2, str(item.get('video_count', 0)))
            if self._is_first_load and self.listCtrl.GetItemCount() > 0:
                self.listCtrl.SetItemState(0, wx.LIST_STATE_SELECTED | wx.LIST_STATE_FOCUSED, wx.LIST_STATE_SELECTED | wx.LIST_STATE_FOCUSED)
                self._is_first_load = False
        finally:
            self.listCtrl.Thaw()
            
    def on_show_videos(self, event):
        selected_index = self.listCtrl.GetFirstSelected()
        if selected_index == -1: return
        playlist = self.filtered_playlists[selected_index]
        # Translators: Message shown while fetching videos from a playlist. {playlist} is the playlist title.
        dialog_title_template = _("Fetching videos from '{playlist}'...").format(playlist=playlist['playlist_title'])
        threading.Thread(target=self.core._view_channel_worker, args=(playlist['playlist_url'], dialog_title_template), daemon=True).start()
        
    def on_open_web(self, event):
        selected_index = self.listCtrl.GetFirstSelected()
        if selected_index == -1: return
        playlist = self.filtered_playlists[selected_index]
        webbrowser.open(playlist.get('playlist_url'))
            
    def refresh_favPlaylists(self, data=None):
        if not self.listCtrl:
            return
        self._load_playlists()
        self.on_search("")
        if data and data.get("action") == "add":
            item_count = self.listCtrl.GetItemCount()
            if item_count > 0:
                last_index = item_count - 1
                self.listCtrl.SetItemState(last_index, wx.LIST_STATE_SELECTED | wx.LIST_STATE_FOCUSED, wx.LIST_STATE_SELECTED | wx.LIST_STATE_FOCUSED)
                self.listCtrl.EnsureVisible(last_index)
        self._update_button_states()

    def _get_sort_fields(self):
        return [
            # Translators: Sort field option for playlist title.
            ('playlist_title', _("Title")),
            # Translators: Sort field option for channel/uploader name.
            ('uploader', _("Channel")),
            # Translators: Sort field option for number of videos in playlist.
            ('video_count', _("Videos")),
            # Translators: Sort field option for date added to the list.
            ('added_at', _("Date Added")),
        ]

    def on_sort(self, event):
        fields = self._get_sort_fields()
        field_labels = [f[1] for f in fields]
        dlg = wx.Dialog(self, title=_("Sort List"))
        sizer = wx.BoxSizer(wx.VERTICAL)
        # Translators: Label for sort field selection.
        sizer.Add(wx.StaticText(dlg, label=_("Sort by:")), 0, wx.ALL, 5)
        fieldCombo = wx.ComboBox(dlg, choices=field_labels, style=wx.CB_READONLY)
        if self._current_sort:
            current_keys = [f[0] for f in fields]
            if self._current_sort[0] in current_keys:
                fieldCombo.SetSelection(current_keys.index(self._current_sort[0]))
            else:
                fieldCombo.SetSelection(0)
        else:
            fieldCombo.SetSelection(0)
        sizer.Add(fieldCombo, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 5)
        # Translators: Radio button for ascending sort order.
        ascRadio = wx.RadioButton(dlg, label=_("&Ascending"), style=wx.RB_GROUP)
        # Translators: Radio button for descending sort order.
        descRadio = wx.RadioButton(dlg, label=_("&Descending"))
        if self._current_sort and not self._current_sort[1]:
            descRadio.SetValue(True)
        else:
            ascRadio.SetValue(True)
        sizer.Add(ascRadio, 0, wx.LEFT | wx.TOP, 5)
        sizer.Add(descRadio, 0, wx.LEFT, 5)
        # Translators: Checkbox to apply sort permanently to the saved file.
        permanentChk = wx.CheckBox(dlg, label=_("&Apply permanently (saves to file)"))
        sizer.Add(permanentChk, 0, wx.ALL, 5)
        btnSizer = wx.StdDialogButtonSizer()
        okBtn = wx.Button(dlg, wx.ID_OK)
        cancelBtn = wx.Button(dlg, wx.ID_CANCEL)
        # Translators: Button to clear current sort and restore original order.
        clearBtn = wx.Button(dlg, label=_("C&lear Sort"))
        btnSizer.AddButton(okBtn)
        btnSizer.AddButton(cancelBtn)
        btnSizer.Realize()
        outerBtnSizer = wx.BoxSizer(wx.HORIZONTAL)
        outerBtnSizer.Add(clearBtn, 0, wx.ALL, 5)
        outerBtnSizer.AddStretchSpacer()
        outerBtnSizer.Add(btnSizer, 0)
        sizer.Add(outerBtnSizer, 0, wx.EXPAND | wx.ALL, 5)
        dlg.SetSizer(sizer)
        sizer.Fit(dlg)
        dlg.CentreOnScreen()
        def on_clear(e):
            dlg.EndModal(wx.ID_RESET)
        clearBtn.Bind(wx.EVT_BUTTON, on_clear)
        result = dlg.ShowModal()
        selected_field_key = fields[fieldCombo.GetSelection()][0]
        ascending = ascRadio.GetValue()
        permanent = permanentChk.GetValue()
        dlg.Destroy()
        if result == wx.ID_RESET:
            self._current_sort = None
            self._load_playlists()
            self.on_search("")
            # Translators: Notification after sort is cleared and original order is restored.
            ui.message(_("Sort cleared."))
            return
        if result != wx.ID_OK:
            return
        self._current_sort = (selected_field_key, ascending)
        self._apply_sort(permanent)

    def _apply_sort(self, permanent=False):
        if not self._current_sort:
            return
        field_key, ascending = self._current_sort
        def sort_key(item):
            val = item.get(field_key, '')
            if val is None:
                val = ''
            try:
                return (0, int(val))
            except (ValueError, TypeError):
                return (1, str(val).lower())
        if permanent:
            self.playlists.sort(key=sort_key, reverse=not ascending)
            self._save_playlists()
            self._current_sort = None
            self.on_search("")
            # Translators: Notification after sort is applied permanently and saved.
            ui.message(_("List sorted and saved."))
        else:
            self.filtered_playlists.sort(key=sort_key, reverse=not ascending)
            self._populate_list()
            # Translators: Notification after temporary sort is applied.
            ui.message(_("List sorted temporarily."))
        if self.listCtrl.GetItemCount() > 0:
            self.listCtrl.SetItemState(0,
                wx.LIST_STATE_SELECTED | wx.LIST_STATE_FOCUSED,
                wx.LIST_STATE_SELECTED | wx.LIST_STATE_FOCUSED)
            self.listCtrl.EnsureVisible(0)
            wx.CallAfter(self.listCtrl.SetFocus)

    def on_rename_playlist(self):
        selected = []
        idx = self.listCtrl.GetFirstSelected()
        while idx != -1:
            selected.append(idx)
            idx = self.listCtrl.GetNextSelected(idx)
        if len(selected) != 1:
            return
        selected_index = selected[0]
        item = self.filtered_playlists[selected_index]
        current_title = item.get('playlist_title', '')
        # Translators: Prompt shown when renaming a playlist title.
        with wx.TextEntryDialog(
            self,
            _("Enter new playlist title:"),
            _("Rename Playlist"),
            value=current_title
        ) as dlg:
            if dlg.ShowModal() != wx.ID_OK:
                return
            new_title = dlg.GetValue().strip()
            if not new_title or new_title == current_title:
                return
        for i, master_item in enumerate(self.playlists):
            if master_item == item:
                self.playlists[i]['playlist_title'] = new_title
                break
        self.filtered_playlists[selected_index]['playlist_title'] = new_title
        self.listCtrl.SetItem(selected_index, 0, new_title)
        self._save_playlists()
        self.listCtrl.SetItemState(
            selected_index,
            wx.LIST_STATE_SELECTED | wx.LIST_STATE_FOCUSED,
            wx.LIST_STATE_SELECTED | wx.LIST_STATE_FOCUSED
        )
        wx.CallAfter(self.listCtrl.SetFocus)
        
class FavsDialog(BaseDialogMixin, wx.Dialog):
    _instance = None 

    def __new__(cls, *args, **kwargs): 
        if cls._instance is None:
            return super(FavsDialog, cls).__new__(cls, *args, **kwargs)
        cls._instance.Raise()
        return cls._instance

    def __init__(self, parent, core_instance, initial_tab_index=0):
        if self.__class__._instance is not None:
            return
        active_profile = config.conf["YoutubePlus"]["activeProfile"]
        # Translators: The title of the favorites dialog, followed by the name of the active user profile.
        title = _("Favorites - YoutubePlus") + " - [{profile}]".format(profile=active_profile)
        super().__init__(parent, title=title)
        self.core = core_instance
        self.panels = {}
        # Translators: Names of the tabs in the favorites dialog.
        self.tabs_info = [
            {'id': 'videos', 'panel_class': FavVideoPanel, 'name': _("Videos")},
            {'id': 'channels', 'panel_class': FavChannelPanel, 'name': _("Channels")},
            {'id': 'playlists', 'panel_class': FavPlaylistPanel, 'name': _("Playlists")},
            {'id': 'watchlist', 'panel_class': WatchListPanel, 'name': _("Watch List")},
            {'id': 'search_history', 'panel_class': SearchHistoryPanel, 'name': _("Search History")},
        ]

        default_order = [t['id'] for t in self.tabs_info]
        saved_order_str = config.conf["YoutubePlus"].get("favTabOrder", "")
        saved_order_list = saved_order_str.split(',') if saved_order_str else default_order

        all_tabs_dict = {t['id']: t for t in self.tabs_info}

        self.ordered_tabs = []
        for tab_id in saved_order_list:
            if tab_id in all_tabs_dict:
                self.ordered_tabs.append(all_tabs_dict.pop(tab_id))
        self.ordered_tabs.extend(all_tabs_dict.values())

        panel = wx.Panel(self)
        sizer = wx.BoxSizer(wx.VERTICAL)

        searchSizer = wx.BoxSizer(wx.HORIZONTAL)
        # Translators: Label for the search text control.
        self.searchLabel = wx.StaticText(panel, label=_("&Search:"))
        self.searchCtrl = wx.TextCtrl(panel, style=wx.TE_PROCESS_ENTER)
        # Translators: Button to open sort dialog.
        self.sortBtn = wx.Button(panel, label=_("S&ort..."))
        searchSizer.Add(self.searchLabel, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 5)
        searchSizer.Add(self.searchCtrl, 1, wx.EXPAND)
        searchSizer.Add(self.sortBtn, 0)
        self.sortBtn.Bind(wx.EVT_BUTTON, self.on_sort)
        sizer.Add(searchSizer, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 10)
        self._searchSizer = searchSizer
        self._mainPanel = panel

        self.notebook = wx.Notebook(panel)
        self._build_tabs()
        initial_tab_id = default_order[initial_tab_index]
        visual_index = next((i for i, t in enumerate(self.ordered_tabs) if t['id'] == initial_tab_id), 0)
        self.notebook.SetSelection(visual_index)
        sizer.Add(self.notebook, 1, wx.EXPAND | wx.ALL, 5)

        # Translators: Button to close the dialog.
        close_btn = wx.Button(panel, wx.ID_CLOSE, _("C&lose"))
        close_btn.Bind(wx.EVT_BUTTON, lambda e: self.Close())

        btn_sizer = wx.BoxSizer(wx.HORIZONTAL)
        btn_sizer.AddStretchSpacer()
        btn_sizer.Add(close_btn, 0, wx.ALL, 5)
        sizer.Add(btn_sizer, 0, wx.EXPAND | wx.RIGHT | wx.BOTTOM, 5)

        panel.SetSizer(sizer)
        self.SetSize((950, 600))
        self.CentreOnScreen()

        self.Bind(wx.EVT_CLOSE, self.on_close)
        self.Bind(wx.EVT_CHAR_HOOK, self.on_char_hook)
        self.searchCtrl.Bind(wx.EVT_TEXT, self.on_search)
        self.notebook.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGED, self.on_tab_changed)
        # อัปเดต visibility ทุกครั้งที่ list เพิ่ม/ลบ item ใน panel ใดก็ตาม
        self.Bind(wx.EVT_LIST_INSERT_ITEM,      lambda e: self._update_search_sort_visibility())
        self.Bind(wx.EVT_LIST_DELETE_ALL_ITEMS, lambda e: self._update_search_sort_visibility())
        self.Bind(wx.EVT_LIST_DELETE_ITEM,      lambda e: self._update_search_sort_visibility())
        self.Bind(wx.EVT_TREE_ITEM_EXPANDED,    lambda e: (self._update_search_sort_visibility(), e.Skip()))
        self.Bind(wx.EVT_TREE_DELETE_ITEM,      lambda e: (self._update_search_sort_visibility(), e.Skip()))
        wx.CallAfter(self.on_tab_changed, None)

    def on_search(self, event):
        search_text = self.searchCtrl.GetValue()
        current_page = self.notebook.GetCurrentPage()
        if not current_page:
            return
        current_page._saved_search_text = search_text
        if hasattr(current_page, 'on_search'):
            current_page.on_search(search_text)

    def on_sort(self, event):
        current_page = self.notebook.GetCurrentPage()
        if not current_page or not hasattr(current_page, 'on_sort'):
            return
        current_page.on_sort(event)
    
    def on_tab_changed(self, event):
        self._update_dialog_title()
        tab_title = self.notebook.GetPageText(self.notebook.GetSelection())
        ui.message(tab_title)
        current_page = self.notebook.GetCurrentPage()
        if not current_page:
            if event: event.Skip()
            return
        saved_search = getattr(current_page, '_saved_search_text', "")
        self.searchCtrl.ChangeValue(saved_search)
        self._update_search_sort_visibility()
        if hasattr(current_page, 'listCtrl'):
            wx.CallAfter(current_page.listCtrl.SetFocus)
        if event:
            event.Skip()

    def _update_search_sort_visibility(self):
        current_page = self.notebook.GetCurrentPage()
        if not current_page:
            return
        try:
            if hasattr(current_page, 'listCtrl'):
                ctrl = current_page.listCtrl
                if isinstance(ctrl, wx.TreeCtrl):
                    root = ctrl.GetRootItem()
                    has_items = root.IsOk() and ctrl.GetChildrenCount(root, False) > 0
                else:
                    has_items = ctrl.GetItemCount() > 0
            else:
                has_items = False
        except Exception:
            has_items = False
        has_sort = hasattr(current_page, 'on_sort') and has_items
        self.sortBtn.Show(has_sort)
        self.searchLabel.Show(has_items)
        self.searchCtrl.Show(has_items)
        self._mainPanel.Layout()
        
    def _update_dialog_title(self):
        """Helper method to update the dialog's title based on the current tab."""
        currentPage = self.notebook.GetCurrentPage()
        if not currentPage: return
        tab_title = self.notebook.GetPageText(self.notebook.GetSelection())
        active_profile = config.conf["YoutubePlus"]["activeProfile"]
        # Translators: The title of the dialog which includes the current tab name and the active profile name.
        # {tab_name} could be "Videos" or "Channels". {profile} is the user-defined profile name.
        full_title = _("{tab_name} - Favorites - YoutubePlus").format(tab_name=tab_title) + " - [{profile}]".format(profile=active_profile)
        self.SetTitle(full_title)

    def _focus_initial_tab(self):
        current_page = self.notebook.GetCurrentPage()
        if not current_page:
            return
        if hasattr(current_page, 'listCtrl'):
            if hasattr(current_page, '_focus_item'):
                current_page._focus_item(0)
            current_page.listCtrl.SetFocus()
            
    def _build_tabs(self, select_tab_id=None):
        self.notebook.DeleteAllPages()
        self.panels = {}
        for tab_info in self.ordered_tabs:
            panel_class = tab_info['panel_class']
            panel = panel_class(self.notebook, self.core)
            self.notebook.AddPage(panel, tab_info['name'])
            self.panels[tab_info['id']] = panel
        if select_tab_id:
            visual_index = next((i for i, t in enumerate(self.ordered_tabs) if t['id'] == select_tab_id), -1)
            if visual_index != -1:
                self.notebook.SetSelection(visual_index)
        wx.CallLater(100, self._focus_initial_tab)
        
    def _move_tab(self, direction):
        current_index = self.notebook.GetSelection()
        new_index = current_index + direction
        if new_index < 0 or new_index >= len(self.ordered_tabs):
            return
        tab_to_move = self.ordered_tabs.pop(current_index)
        self.ordered_tabs.insert(new_index, tab_to_move)
        wx.CallAfter(self._build_tabs, select_tab_id=tab_to_move['id'])
        
    def on_char_hook(self, event):
        control_down = event.ControlDown()
        key_code = event.GetKeyCode()
        if control_down:
            if key_code in (wx.WXK_UP, wx.WXK_LEFT):
                self._move_tab(-1)
                return
            if key_code in (wx.WXK_DOWN, wx.WXK_RIGHT):
                self._move_tab(1)
                return
            if ord('1') <= key_code <= ord('9'):
                target_tab_index = key_code - ord('1')
                if target_tab_index < self.notebook.GetPageCount():
                    self.notebook.SetSelection(target_tab_index)
                return
        super().on_char_hook(event)

    def on_close(self, event):
        current_order_ids = [t['id'] for t in self.ordered_tabs]
        config.conf["YoutubePlus"]["favTabOrder"] = ",".join(current_order_ids)
        for panel in self.panels.values():
            if hasattr(panel, 'on_close'):
                panel.on_close(event)
        self.__class__._instance = None
        self.Destroy()

class SearchHistoryPanel(wx.Panel):
    """Panel showing search history, accessible as a tab in FavDialog."""

    def __init__(self, parent, core_instance):
        wx.Panel.__init__(self, parent)
        self.core = core_instance
        self.history = []
        self.history_file = self.core.get_profile_path("search_history.json")
        self._current_sort = None

        mainSizer = wx.BoxSizer(wx.VERTICAL)

        self.listCtrl = wx.ListCtrl(self, style=wx.LC_REPORT | wx.LC_SINGLE_SEL)
        # Translators: Column header for the search keyword in search history.
        self.listCtrl.InsertColumn(0, _("Keyword"), width=300)
        # Translators: Column header for the number of results fetched in search history.
        self.listCtrl.InsertColumn(1, _("Results"), width=70)
        # Translators: Column header for the date and time the search was performed.
        self.listCtrl.InsertColumn(2, _("Searched At"), width=160)
        mainSizer.Add(self.listCtrl, 1, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 10)

        btnSizer = wx.BoxSizer(wx.HORIZONTAL)
        # Translators: Button to re-run the selected search query.
        self.searchBtn = wx.Button(self, label=_("Search &Again"))
        # Translators: Button to open search dialog to add a new search.
        self.addBtn = wx.Button(self, label=_("&New Search"))
        # Translators: Button to remove the selected search history entry.
        self.removeBtn = wx.Button(self, label=_("&Remove"))
        # Translators: Button to clear all search history entries.
        self.clearAllBtn = wx.Button(self, label=_("&Clear All"))
        btnSizer.Add(self.searchBtn, 0, wx.RIGHT, 5)
        btnSizer.Add(self.addBtn, 0, wx.RIGHT, 5)
        btnSizer.AddStretchSpacer()
        btnSizer.Add(self.removeBtn, 0, wx.RIGHT, 5)
        btnSizer.Add(self.clearAllBtn, 0)
        mainSizer.Add(btnSizer, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 10)

        self.SetSizer(mainSizer)

        self.core.register_callback("search_history_updated", self._on_history_updated)
        self._load_and_populate()
        self._update_button_states()

        self.listCtrl.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.on_search_again)
        self.listCtrl.Bind(wx.EVT_KEY_DOWN, self.on_list_key_down)
        self.listCtrl.Bind(wx.EVT_LIST_ITEM_SELECTED, lambda e: self._update_button_states())
        self.listCtrl.Bind(wx.EVT_LIST_ITEM_DESELECTED, lambda e: self._update_button_states())
        self.searchBtn.Bind(wx.EVT_BUTTON, self.on_search_again)
        self.addBtn.Bind(wx.EVT_BUTTON, self.on_new_search)
        self.removeBtn.Bind(wx.EVT_BUTTON, self.on_remove)
        self.clearAllBtn.Bind(wx.EVT_BUTTON, self.on_clear_all)

    def _load_and_populate(self):
        if not self or not self.listCtrl or not self.listCtrl.IsShown():
            return
        self.history = self.core._load_json_list(self.history_file)
        self.listCtrl.DeleteAllItems()
        for index, item in enumerate(self.history):
            self.listCtrl.InsertItem(index, item.get('keyword', ''))
            self.listCtrl.SetItem(index, 1, str(item.get('result_count', '')))
            self.listCtrl.SetItem(index, 2, item.get('searched_at', ''))
        if self.listCtrl.GetItemCount() > 0:
            self.listCtrl.SetItemState(
                0,
                wx.LIST_STATE_SELECTED | wx.LIST_STATE_FOCUSED,
                wx.LIST_STATE_SELECTED | wx.LIST_STATE_FOCUSED
            )

    def _on_history_updated(self, data=None):
        wx.CallAfter(self._load_and_populate)
        wx.CallAfter(self._update_button_states)

    def on_close(self, event=None):
        self.core.unregister_callback("search_history_updated", self._on_history_updated)

    def _get_sort_fields(self):
        return [
            ('keyword',     _("Keyword")),
            ('result_count', _("Results")),
            ('searched_at', _("Searched At")),
        ]

    def on_sort(self, event):
        fields = self._get_sort_fields()
        field_labels = [f[1] for f in fields]
        dlg = wx.Dialog(self, title=_("Sort List"))
        sizer = wx.BoxSizer(wx.VERTICAL)
        # Translators: Label for sort field selection.
        sizer.Add(wx.StaticText(dlg, label=_("Sort by:")), 0, wx.ALL, 5)
        fieldCombo = wx.ComboBox(dlg, choices=field_labels, style=wx.CB_READONLY)
        if self._current_sort:
            current_keys = [f[0] for f in fields]
            if self._current_sort[0] in current_keys:
                fieldCombo.SetSelection(current_keys.index(self._current_sort[0]))
            else:
                fieldCombo.SetSelection(0)
        else:
            fieldCombo.SetSelection(0)
        sizer.Add(fieldCombo, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 5)
        # Translators: Radio button for ascending sort order.
        ascRadio = wx.RadioButton(dlg, label=_("&Ascending"), style=wx.RB_GROUP)
        # Translators: Radio button for descending sort order.
        descRadio = wx.RadioButton(dlg, label=_("&Descending"))
        if self._current_sort and not self._current_sort[1]:
            descRadio.SetValue(True)
        else:
            ascRadio.SetValue(True)
        sizer.Add(ascRadio, 0, wx.LEFT | wx.TOP, 5)
        sizer.Add(descRadio, 0, wx.LEFT, 5)
        btnSizer = wx.StdDialogButtonSizer()
        okBtn = wx.Button(dlg, wx.ID_OK)
        cancelBtn = wx.Button(dlg, wx.ID_CANCEL)
        # Translators: Button to clear current sort and restore original order.
        clearBtn = wx.Button(dlg, label=_("C&lear Sort"))
        btnSizer.AddButton(okBtn)
        btnSizer.AddButton(cancelBtn)
        btnSizer.Realize()
        outerBtnSizer = wx.BoxSizer(wx.HORIZONTAL)
        outerBtnSizer.Add(clearBtn, 0, wx.ALL, 5)
        outerBtnSizer.AddStretchSpacer()
        outerBtnSizer.Add(btnSizer, 0)
        sizer.Add(outerBtnSizer, 0, wx.EXPAND | wx.ALL, 5)
        dlg.SetSizer(sizer)
        sizer.Fit(dlg)
        dlg.CentreOnScreen()
        clearBtn.Bind(wx.EVT_BUTTON, lambda e: dlg.EndModal(wx.ID_RESET))
        result = dlg.ShowModal()
        selected_field_key = fields[fieldCombo.GetSelection()][0]
        ascending = ascRadio.GetValue()
        dlg.Destroy()
        if result == wx.ID_RESET:
            self._current_sort = None
            self._load_and_populate()
            # Translators: Notification after sort is cleared.
            ui.message(_("Sort cleared."))
            return
        if result != wx.ID_OK:
            return
        self._current_sort = (selected_field_key, ascending)
        self._apply_sort()

    def _apply_sort(self):
        if not self._current_sort:
            return
        field_key, ascending = self._current_sort
        def sort_key(item):
            val = item.get(field_key, '')
            if val is None:
                val = ''
            try:
                return (0, int(val))
            except (ValueError, TypeError):
                return (1, str(val).lower())
        self.history.sort(key=sort_key, reverse=not ascending)
        self.listCtrl.DeleteAllItems()
        for index, item in enumerate(self.history):
            self.listCtrl.InsertItem(index, item.get('keyword', ''))
            self.listCtrl.SetItem(index, 1, str(item.get('result_count', '')))
            self.listCtrl.SetItem(index, 2, item.get('searched_at', ''))
        if self.listCtrl.GetItemCount() > 0:
            self.listCtrl.SetItemState(
                0,
                wx.LIST_STATE_SELECTED | wx.LIST_STATE_FOCUSED,
                wx.LIST_STATE_SELECTED | wx.LIST_STATE_FOCUSED
            )
            wx.CallAfter(self.listCtrl.SetFocus)
        # Translators: Notification after sort is applied.
        ui.message(_("List sorted."))

    def _update_button_states(self):
        if not self or not self.listCtrl:
            return
        has_items     = self.listCtrl.GetItemCount() > 0
        has_selection = self.listCtrl.GetFirstSelected() != -1
        self.searchBtn.Enable(has_selection)
        self.removeBtn.Enable(has_selection)
        self.clearAllBtn.Enable(has_items)

    def _get_selected_item(self):
        idx = self.listCtrl.GetFirstSelected()
        if idx == -1:
            return None, -1
        return self.history[idx], idx

    # ── Key handler ───────────────────────────────────────────────────────────

    def on_list_key_down(self, event):
        key = event.GetKeyCode()
        if key in (wx.WXK_RETURN, wx.WXK_NUMPAD_ENTER, wx.WXK_SPACE):
            self.on_search_again(event)
        elif key == wx.WXK_DELETE:
            self.on_remove(event)
        else:
            event.Skip()

    # ── Actions ───────────────────────────────────────────────────────────────

    def on_search_again(self, event):
        item, _ = self._get_selected_item()
        if not item:
            return
        keyword = item.get('keyword', '')
        count   = item.get('result_count', config.conf["YoutubePlus"].get("searchResultCount", 20))
        if not keyword:
            return
        threading.Thread(
            target=self.core._Youtube_worker,
            args=(keyword, count, gui.mainFrame),
            daemon=True
        ).start()

    def on_search(self, search_text):
        """Filter history list by keyword."""
        self.listCtrl.DeleteAllItems()
        query = search_text.strip().lower()
        filtered = [h for h in self.history if query in h.get('keyword', '').lower()] if query else self.history
        for index, item in enumerate(filtered):
            self.listCtrl.InsertItem(index, item.get('keyword', ''))
            self.listCtrl.SetItem(index, 1, str(item.get('result_count', '')))
            self.listCtrl.SetItem(index, 2, item.get('searched_at', ''))
        if self.listCtrl.GetItemCount() > 0:
            self.listCtrl.SetItemState(0, wx.LIST_STATE_SELECTED | wx.LIST_STATE_FOCUSED, wx.LIST_STATE_SELECTED | wx.LIST_STATE_FOCUSED)
        self._update_button_states()

    def on_new_search(self, event):
        """เปิด SearchDialog เพื่อค้นหาใหม่"""
        from .dialogs import SearchDialog
        gui.mainFrame.prePopup()
        dialog = SearchDialog(gui.mainFrame, self.core)
        dialog.Show()
        gui.mainFrame.postPopup()

    def on_remove(self, event):
        item, idx = self._get_selected_item()
        if not item:
            return
        del self.history[idx]
        self.core._save_json_list(self.history_file, self.history)
        self.listCtrl.DeleteItem(idx)
        new_count = self.listCtrl.GetItemCount()
        if new_count > 0:
            new_sel = min(idx, new_count - 1)
            self.listCtrl.SetItemState(
                new_sel,
                wx.LIST_STATE_SELECTED | wx.LIST_STATE_FOCUSED,
                wx.LIST_STATE_SELECTED | wx.LIST_STATE_FOCUSED
            )
        self._update_button_states()
        # Translators: Notification after a search history entry is removed.
        self.core._notify_delete(_("Search history entry removed."))

    def on_clear_all(self, event):
        # Translators: Confirmation message before clearing all search history.
        if wx.MessageBox(
            _("Clear all search history?"),
            # Translators: Title of the confirmation dialog for clearing search history.
            _("Confirm"),
            wx.YES_NO | wx.ICON_QUESTION
        ) != wx.YES:
            return
        self.history = []
        self.core._save_json_list(self.history_file, self.history)
        self.listCtrl.DeleteAllItems()
        self._update_button_states()


class SearchDialog(BaseDialogMixin, wx.Dialog):
    """
    A simplified and robust search dialog.
    """

    def __init__(self, parent, core_instance):
        # Translators: Title of the dialog for searching YouTube.
        super().__init__(parent, title=_("Search YouTube"))
        self.core = core_instance

        history_file = self.core.get_profile_path("search_history.json")
        history_data = self.core._load_json_list(history_file)
        
        self.history_keywords = []
        for item in history_data:
            kw = item.get('keyword', '')
            if kw and kw not in self.history_keywords:
                self.history_keywords.append(kw)

        panel = wx.Panel(self)
        mainSizer = wx.BoxSizer(wx.VERTICAL)
        sHelper = gui.guiHelper.BoxSizerHelper(self, sizer=mainSizer)
        
        # Translators: Label for the search query input field.
        sHelper.addItem(wx.StaticText(panel, label=_("&Search for:")))
        
        self.queryText = sHelper.addItem(wx.ComboBox(
            panel, 
            value="", # ให้ค่าเริ่มต้นเป็นช่องว่างเปล่า
            choices=self.history_keywords, # ยัดประวัติการค้นหาเข้าไปให้เป็นตัวเลือก
            style=wx.CB_DROPDOWN | wx.TE_PROCESS_ENTER
        ))

        # Translators: Label for selecting the number of search results to retrieve.
        sHelper.addItem(wx.StaticText(panel, label=_("Number of &results to fetch:")))
        last_count = config.conf["YoutubePlus"].get("searchResultCount", 20)
        self.countSpin = sHelper.addItem(wx.SpinCtrl(panel, min=5, max=50, initial=last_count))

        btnSizer = wx.BoxSizer(wx.HORIZONTAL)
        # Translators: Button to initiate the search.
        self.searchBtn = wx.Button(panel, wx.ID_OK, label=_("&Search"))
        # Translators: Button to cancel the search and close the dialog.
        self.cancelBtn = wx.Button(panel, wx.ID_CANCEL, label=_("Ca&ncel"))
        btnSizer.Add(self.searchBtn)
        btnSizer.Add(self.cancelBtn, flag=wx.LEFT, border=5)
        sHelper.addItem(btnSizer, flag=wx.ALIGN_CENTER | wx.TOP, border=10)

        panel.SetSizer(mainSizer)
        self.Fit()
        self.CentreOnScreen()

        self.searchBtn.SetDefault()

        self.Bind(wx.EVT_CHAR_HOOK, self.on_char_hook)
        self.searchBtn.Bind(wx.EVT_BUTTON, self.on_search)
        self.cancelBtn.Bind(wx.EVT_BUTTON, self.on_close)
        
        self.queryText.Bind(wx.EVT_TEXT_ENTER, self.on_search)
        wx.CallAfter(self.queryText.SetFocus)
        
    def on_close(self, event):
        self.Destroy()

    def on_search(self, event):
        """Gathers data, saves the count, and calls the core worker."""
        query = self.queryText.GetValue().strip()
        count = self.countSpin.GetValue()
        if not query:
            # Translators: Error message shown when the search field is empty.
            ui.message(_("Please enter a search term."))
            return
        config.conf["YoutubePlus"]["searchResultCount"] = count
        threading.Thread(target=self.core._Youtube_worker,
                         args=(query, count, self),
                         daemon=True).start()

class ChannelVideoDialog(BaseDialogMixin, VideoActionMixin, wx.Dialog):
    """A dialog to display a list of videos, now with a full action menu."""
    _escape_protection = True   

    def __init__(self, parent, title, video_list, core_instance, playlist_id_to_update=None, new_count_to_update=None, source_url=None, content_type_label="videos", is_collection=False):
        super().__init__(parent, title=title)
        self.videos = video_list
        self.core = core_instance
        self.playlist_id_to_update = playlist_id_to_update
        self.new_count_to_update = new_count_to_update
        self.is_collection = is_collection
        self.source_url = source_url
        self.content_type_label = content_type_label
        panel = wx.Panel(self)
        mainSizer = wx.BoxSizer(wx.VERTICAL)
        self.listCtrl = wx.ListCtrl(panel, style=wx.LC_REPORT | wx.LC_SINGLE_SEL)
        self.listCtrl.InsertColumn(0, _("Title"), width=450)
        # Translators: Column header showing video count for playlists, or duration for videos.
        col2_label = _("Videos") if is_collection else _("Duration")
        self.listCtrl.InsertColumn(1, col2_label, width=120)
        mainSizer.Add(self.listCtrl, 1, wx.EXPAND | wx.ALL, 10)
        btnSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.actionBtn = wx.Button(panel, label=_("&Action..."))
        self.copyBtn = wx.Button(panel, label=_("&Copy..."))
        # Translators: Button to load all videos without the fetch limit.
        self.loadAllBtn = wx.Button(panel, label=_("Load All"))
        self.closeBtn = wx.Button(panel, label=_("C&lose"))
        btnSizer.Add(self.actionBtn, 0, wx.RIGHT, 5)
        btnSizer.Add(self.copyBtn, 0, wx.RIGHT, 5)
        btnSizer.Add(self.loadAllBtn, 0, wx.RIGHT, 5)
        btnSizer.AddStretchSpacer()
        btnSizer.Add(self.closeBtn, 0)
        mainSizer.Add(btnSizer, 0, wx.EXPAND | wx.ALL, 10)
        panel.SetSizer(mainSizer)
        self.SetSize((700, 500))
        self.CentreOnScreen()
        self._populate_list()
        if self.listCtrl.GetItemCount() > 0:
            self.listCtrl.SetItemState(0, wx.LIST_STATE_SELECTED | wx.LIST_STATE_FOCUSED, wx.LIST_STATE_SELECTED | wx.LIST_STATE_FOCUSED)
            self.listCtrl.EnsureVisible(0)
        if not self.source_url:
            self.loadAllBtn.Hide()
        self.Bind(wx.EVT_CLOSE, self.on_close)
        self.Bind(wx.EVT_CHAR_HOOK, self.on_char_hook)
        self.actionBtn.Bind(wx.EVT_BUTTON, self.on_action_menu)
        self.copyBtn.Bind(wx.EVT_BUTTON, self.on_copy_menu)
        self.loadAllBtn.Bind(wx.EVT_BUTTON, self.on_load_all)
        self.closeBtn.Bind(wx.EVT_BUTTON, self.on_close)
        self.listCtrl.Bind(wx.EVT_KEY_DOWN, self.on_list_key_down)
        wx.CallAfter(self.listCtrl.SetFocus)
        
    def get_selected_video_info(self):
        """Required method for the Action Mixin."""
        selected_index = self.listCtrl.GetFirstSelected()
        if selected_index == -1: return None
        return self.videos[selected_index]

    def on_action_menu(self, event):
        """Shows the action menu from the mixin."""
        if self.listCtrl.GetFirstSelected() == -1: return
        menu = self.create_video_action_menu()
        self.PopupMenu(menu)
        menu.Destroy()

    def on_copy_menu(self, event):
            if self.listCtrl.GetFirstSelected() == -1: return
            menu = wx.Menu()
            # Translators: Menu item to copy the video title to clipboard.
            menu.Append(1, _("Copy &Title"))
            # Translators: Menu item to copy the video URL to clipboard.
            menu.Append(2, _("Copy Video &URL"))
            # Translators: Menu item to copy the channel name to clipboard.
            menu.Append(3, _("Copy &Channel Name"))
            # Translators: Menu item to copy the channel URL to clipboard.
            menu.Append(4, _("Copy C&hannel URL"))
            menu.AppendSeparator()
            # Translators: Menu item to copy the video summary to clipboard.
            menu.Append(5, _("Copy &Summary"))

            def on_select(e):
                id_map = {1: 'title', 2: 'url', 3: 'channel_name', 4: 'channel_url', 5: 'summary'}
                copy_type = id_map.get(e.GetId())
                if copy_type:
                    self.on_copy(copy_type)
            
            menu.Bind(wx.EVT_MENU, on_select)
            self.PopupMenu(menu)
            menu.Destroy()
    
    def on_close(self, event):
        if self.playlist_id_to_update and self.new_count_to_update is not None:
            threading.Thread(
                target=self.core._update_playlist_count_worker,
                args=(self.playlist_id_to_update, self.new_count_to_update),
                daemon=True
            ).start()
        self.Destroy()
        
    def _populate_list(self):
        for index, video in enumerate(self.videos):
            # Translators: Default text for a video title if it's missing.
            default_val = _("N/A")
            self.listCtrl.InsertItem(index, video.get('title') or default_val)
            self.listCtrl.SetItem(index, 1, video.get('duration_str', ''))

    def on_list_key_down(self, event):
        key_code = event.GetKeyCode()
        if key_code in (wx.WXK_RETURN, wx.WXK_NUMPAD_ENTER, wx.WXK_SPACE):
            self.handle_video_list_keys(event)
            return
        event.Skip()

    def on_load_all(self, event):
        self.loadAllBtn.Disable()
        thread_kwargs = {
            'url': self.source_url,
            'dialog_title_template': self.GetTitle(),
            'content_type_label': self.content_type_label,
            'load_all': True,
        }
        self.Destroy()
        threading.Thread(target=self.core._view_channel_worker, kwargs=thread_kwargs, daemon=True).start()     
     
class ChannelCollectionDialog(BaseDialogMixin, wx.Dialog):
    """
    Browse dialog for playlist-based content types (playlists, podcasts).
    Shows list of playlists with title + video count.
    Enter/Space expands a playlist into ChannelVideoDialog.
    """
    _escape_protection = True   

    def __init__(self, parent, title, items, core_instance, source_url=None, content_type_label=""):
        super().__init__(parent, title=title)
        self.items = items          
        self.core = core_instance
        self    .source_url = source_url
        self.content_type_label = content_type_label
    
        panel = wx.Panel(self)
        mainSizer = wx.BoxSizer(wx.VERTICAL)

        self.listCtrl = wx.ListCtrl(panel, style=wx.LC_REPORT | wx.LC_SINGLE_SEL)
        # Translators: Column header for the playlist title.
        self.listCtrl.InsertColumn(0, _("Playlist Title"), width=400)
        # Translators: Column header for the number of videos in a playlist.
        self.listCtrl.InsertColumn(1, _("Videos"), width=80)

        mainSizer.Add(self.listCtrl, 1, wx.EXPAND | wx.ALL, 10)

        btnSizer = wx.BoxSizer(wx.HORIZONTAL)
        # Translators: Button to add selected playlist to favorites.
        self.addFavBtn = wx.Button(panel, label=_("Add to &Favorites"))
        # Translators: Button to show videos inside the selected playlist.
        self.showVideosBtn = wx.Button(panel, label=_("Show &Videos..."))
        # Translators: Button to open the selected playlist in a browser.
        self.openWebBtn = wx.Button(panel, label=_("Open on &Browser"))
        # Translators: Button to copy info from selected playlist.
        self.copyBtn = wx.Button(panel, label=_("&Copy..."))
        # Translators: Button to load all videos without the fetch limit.
        self.loadAllBtn = wx.Button(panel, label=_("Load All"))
        # Translators: Button to close this dialog.
        self.closeBtn = wx.Button(panel, label=_("C&lose"))
        btnSizer.Add(self.addFavBtn, 0, wx.RIGHT, 5)
        btnSizer.Add(self.showVideosBtn, 0, wx.RIGHT, 5)
        btnSizer.Add(self.openWebBtn, 0, wx.RIGHT, 5)
        btnSizer.Add(self.copyBtn, 0, wx.RIGHT, 5)
        btnSizer.Add(self.loadAllBtn, 0, wx.RIGHT, 5)
        btnSizer.AddStretchSpacer()
        btnSizer.Add(self.closeBtn, 0)
        mainSizer.Add(btnSizer, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 10)

        panel.SetSizer(mainSizer)
        self.SetSize((580, 450))
        self.CentreOnScreen()

        self._populate_list()
        if not self.source_url:
            self.loadAllBtn.Hide()
        self.addFavBtn.Bind(wx.EVT_BUTTON, self.on_add_to_favorites)
        self.Bind(wx.EVT_CLOSE, lambda e: self.Destroy())
        self.Bind(wx.EVT_CHAR_HOOK, self.on_char_hook)
        self.showVideosBtn.Bind(wx.EVT_BUTTON, self.on_show_videos)
        self.openWebBtn.Bind(wx.EVT_BUTTON, self.on_open_web)
        self.copyBtn.Bind(wx.EVT_BUTTON, self.on_copy_menu)
        self.loadAllBtn.Bind(wx.EVT_BUTTON, self.on_load_all)
        self.closeBtn.Bind(wx.EVT_BUTTON, lambda e: self.Destroy())
        self.listCtrl.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.on_show_videos)
        self.listCtrl.Bind(wx.EVT_KEY_DOWN, self.on_list_key_down)

        if self.listCtrl.GetItemCount() > 0:
            self.listCtrl.SetItemState(
                0,
                wx.LIST_STATE_SELECTED | wx.LIST_STATE_FOCUSED,
                wx.LIST_STATE_SELECTED | wx.LIST_STATE_FOCUSED
            )
        wx.CallAfter(self.listCtrl.SetFocus)

    def _populate_list(self):
        self.listCtrl.DeleteAllItems()
        for index, item in enumerate(self.items):
            self.listCtrl.InsertItem(index, item.get('title', _("N/A")))
            count = item.get('duration_str', '')   # worker เก็บ video_count ใน duration_str
            self.listCtrl.SetItem(index, 1, str(count) if count else '-')

    def on_list_key_down(self, event):
        key = event.GetKeyCode()
        if key in (wx.WXK_RETURN, wx.WXK_NUMPAD_ENTER, wx.WXK_SPACE):
            self.on_show_videos(event)
            return
        event.Skip()

    def _get_selected(self):
        idx = self.listCtrl.GetFirstSelected()
        if idx == -1:
            return None
        return self.items[idx]

    def on_show_videos(self, event):
        item = self._get_selected()
        if not item:
            return
        playlist_url = item.get('playlist_url')
        if not playlist_url:
            ui.message(_("Playlist URL not found."))
            return
        # Translators: Status shown while fetching videos from a playlist. {title} is the playlist name.
        title_template = _("Fetching videos from '{title}'...").format(title=item.get('title', ''))
        threading.Thread(
            target=self.core._view_channel_worker,
            args=(playlist_url, title_template),
            daemon=True
        ).start()

    def on_open_web(self, event):
        item = self._get_selected()
        if not item:
            return
        url = item.get('playlist_url', '')
        if url:
            webbrowser.open(url)

    def on_copy_menu(self, event):
        item = self._get_selected()
        if not item:
            return
        menu = wx.Menu()
        # Translators: Menu item to copy the playlist title.
        menu.Append(1, _("Copy &Title"))
        # Translators: Menu item to copy the playlist URL.
        menu.Append(2, _("Copy Playlist &URL"))
        # Translators: Menu item to copy both title and URL as a summary.
        menu.Append(3, _("Copy &Summary"))

        def on_select(e):
            mid = e.GetId()
            text = ''
            if mid == 1:
                text = item.get('title', '')
            elif mid == 2:
                text = item.get('playlist_url', '')
            elif mid == 3:
                text = (
                    _("Title: {title}\n").format(title=item.get('title', '')) +
                    _("URL: ") + item.get('playlist_url', '')
                )
            if text:
                api.copyToClip(text)
                ui.message(_("Copied"))

        menu.Bind(wx.EVT_MENU, on_select)
        self.PopupMenu(menu)
        menu.Destroy()

    def on_load_all(self, event):
        source_url = self.source_url
        content_type_label = self.content_type_label
        thread_kwargs = {
            'url': source_url,
            'dialog_title_template': self.GetTitle(),
            'content_type_label': content_type_label,
            'load_all': True,
            'is_collection': True,
        }
        self.Destroy()
        threading.Thread(target=self.core._view_channel_worker, kwargs=thread_kwargs, daemon=True).start()

    def on_add_to_favorites(self, event):
        item = self._get_selected()
        if not item:
            return
        url = item.get('playlist_url')
        if not url:
            ui.message(_("Playlist URL not found."))
            return
        threading.Thread(
            target=self.core.add_playlist_to_favorites_worker,
            args=(url,),
            daemon=True
        ).start()

class ManageSubscriptionsDialog(BaseDialogMixin, wx.Dialog):
    """
    Dialog to manage subscribed channels, categories, and content types.
    Auto-saves when switching channels or closing — no Save button needed.
    """
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            return super(ManageSubscriptionsDialog, cls).__new__(cls, *args, **kwargs)
        cls._instance.Raise()
        return cls._instance

    def __init__(self, parent, core_instance):
        if self.__class__._instance is not None:
            return
        # Translators: Title of the subscription management dialog.
        super().__init__(parent, title=_("Manage Subscriptions"))
        self.__class__._instance = self

        self.core = core_instance
        self.db_path = self.core.get_profile_path("subscription.db")
        self.all_channels = []
        self.categories = []
        self._current_channel_url = None   # track ช่องที่ถูก load ใน right panel
        self._dirty = False                # มีการแก้ไขที่ยังไม่ได้ save

        panel = wx.Panel(self)
        topSizer = wx.BoxSizer(wx.VERTICAL)
        mainSplitSizer = wx.BoxSizer(wx.HORIZONTAL)

        leftPanel = wx.Panel(panel)
        leftSizer = wx.BoxSizer(wx.VERTICAL)
        # Translators: Label for the list of subscribed channels.
        leftSizer.Add(wx.StaticText(leftPanel, label=_("Subscribed &Channels:")), 0, wx.BOTTOM, 5)
        self.channelListCtrl = wx.ListCtrl(leftPanel, style=wx.LC_REPORT | wx.LC_SINGLE_SEL)
        # Translators: Column header for channel name.
        self.channelListCtrl.InsertColumn(0, _("Channel Name"), width=300)
        leftSizer.Add(self.channelListCtrl, 1, wx.EXPAND)

        filterSizer = wx.BoxSizer(wx.HORIZONTAL)
        # Translators: Label for filtering channels by category.
        filterSizer.Add(wx.StaticText(leftPanel, label=_("Filter by Category:")), 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 5)
        self.categoryFilterCombo = wx.ComboBox(leftPanel, style=wx.CB_READONLY)
        filterSizer.Add(self.categoryFilterCombo, 1, wx.EXPAND)
        leftSizer.Add(filterSizer, 0, wx.EXPAND | wx.TOP, 5)
        leftPanel.SetSizer(leftSizer)

        self.rightPanel = wx.Panel(panel)
        rightSizer = wx.BoxSizer(wx.VERTICAL)
        # Translators: Section title for assigning categories to a channel.
        catBox = wx.StaticBoxSizer(wx.VERTICAL, self.rightPanel, label=_("Assign to Categories"))
        catHelper = gui.guiHelper.BoxSizerHelper(self, sizer=catBox)
        self.categoryCheckList = catHelper.addItem(gui.nvdaControls.CustomCheckListBox(self.rightPanel))
        rightSizer.Add(catBox, 1, wx.EXPAND | wx.ALL, 5)
        # Translators: Section title for selecting what content types to fetch.
        typeBox = wx.StaticBoxSizer(wx.VERTICAL, self.rightPanel, label=_("Content Types to Fetch"))
        typeHelper = gui.guiHelper.BoxSizerHelper(self, sizer=typeBox)
        # Translators: Options for fetching different YouTube content formats.
        self.contentTypesList = typeHelper.addItem(gui.nvdaControls.CustomCheckListBox(self.rightPanel, choices=[_("Videos"), _("Shorts"), _("Live")]))
        rightSizer.Add(typeBox, 0, wx.EXPAND | wx.ALL, 5)
        # Translators: Section title for channel actions.
        actionBox = wx.StaticBoxSizer(wx.VERTICAL, self.rightPanel, label=_("Actions"))
        actionHelper = gui.guiHelper.BoxSizerHelper(self, sizer=actionBox)
        # Translators: Button to view content from the selected channel.
        self.viewContentBtn = actionHelper.addItem(wx.Button(self.rightPanel, label=_("View &Content...")))
        # Translators: Button to subscribe to a channel using a URL from the clipboard.
        self.addBtn = actionHelper.addItem(wx.Button(self.rightPanel, label=_("Add &new subscribe channel from Clipboard...")))
        # Translators: Button to unsubscribe from the selected channel.
        self.unsubBtn = actionHelper.addItem(wx.Button(self.rightPanel, label=_("&Unsubscribe from this Channel")))
        rightSizer.Add(actionBox, 0, wx.EXPAND | wx.ALL, 5)
        self.rightPanel.SetSizer(rightSizer)

        mainSplitSizer.Add(leftPanel, 1, wx.EXPAND | wx.ALL, 5)
        mainSplitSizer.Add(self.rightPanel, 1, wx.EXPAND | wx.ALL, 5)
        topSizer.Add(mainSplitSizer, 1, wx.EXPAND)

        btnSizer = wx.BoxSizer(wx.HORIZONTAL)
        # Translators: Button to close the dialog.
        self.closeBtn = wx.Button(panel, wx.ID_CANCEL, label=_("C&lose"))
        btnSizer.AddStretchSpacer()
        btnSizer.Add(self.closeBtn, 0)
        topSizer.Add(btnSizer, 0, wx.ALIGN_RIGHT | wx.ALL, 10)

        panel.SetSizer(topSizer)
        self.SetSize((800, 500))
        self.CentreOnScreen()

        self.core.register_callback("subscription_added", self._on_subscription_added)
        self.core.register_callback("subscription_removed", self._on_subscription_removed)
        self._load_all_data()
        self._populate_category_filter()
        self._populate_channel_list()

        self.Bind(wx.EVT_CLOSE, self.on_close)
        self.Bind(wx.EVT_CHAR_HOOK, self.on_char_hook)
        self.closeBtn.Bind(wx.EVT_BUTTON, lambda e: self.Close())
        self.categoryFilterCombo.Bind(wx.EVT_COMBOBOX, self._on_filter_changed)
        self.channelListCtrl.Bind(wx.EVT_LIST_ITEM_SELECTED, self._on_channel_selected)
        self.channelListCtrl.Bind(wx.EVT_LIST_ITEM_DESELECTED, self._update_ui_state)
        self.categoryCheckList.Bind(wx.EVT_CHECKLISTBOX, self._on_setting_changed)
        self.contentTypesList.Bind(wx.EVT_CHECKLISTBOX, self._on_setting_changed)
        self.unsubBtn.Bind(wx.EVT_BUTTON, self.on_unsubscribe)
        self.viewContentBtn.Bind(wx.EVT_BUTTON, self.on_view_channel_content)
        self.addBtn.Bind(wx.EVT_BUTTON, self.on_add_subscription)

    # ── Auto-save logic ──────────────────────────────────────────

    def _on_setting_changed(self, event):
        """Mark dirty whenever user checks/unchecks anything."""
        self._dirty = True
        event.Skip()

    def _save_current_channel(self):
        """
        Save categories and content types for the currently loaded channel.
        Called automatically before switching channels or closing.
        Returns True on success or if nothing to save.
        """
        if not self._dirty or not self._current_channel_url:
            return True
        channel_url = self._current_channel_url
        try:
            with sqlite3.connect(self.db_path) as con:
                cur = con.cursor()
                cur.execute("DELETE FROM channel_category_links WHERE channel_url = ?", (channel_url,))
                for index in self.categoryCheckList.CheckedItems:
                    cat_id, __ = self.categories[index]
                    cur.execute(
                        "INSERT INTO channel_category_links (channel_url, category_id) VALUES (?, ?)",
                        (channel_url, cat_id)
                    )
                internal_types = ["videos", "shorts", "streams"]
                types_to_save = [internal_types[i] for i in self.contentTypesList.CheckedItems]
                cur.execute(
                    "UPDATE subscribed_channels SET content_types = ? WHERE channel_url = ?",
                    (",".join(types_to_save), channel_url)
                )
                con.commit()
            self._dirty = False
            # Translators: Brief announcement after auto-saving channel settings.
            ui.message(_("Changes saved."))
            return True
        except Exception as e:
            log.error("Failed to auto-save subscription changes: %s", e)
            return False

    def _on_filter_changed(self, event):
        """Save current channel before repopulating list with new filter."""
        self._save_current_channel()
        self._populate_channel_list()

    def _on_channel_selected(self, event):
        """Save previous channel's settings before loading the newly selected one."""
        self._save_current_channel()
        self._update_right_panel(event)

    def _load_all_data(self):
        """Loads all channels and categories from the database."""
        try:
            with sqlite3.connect(self.db_path) as con:
                cur = con.cursor()
                cur.execute("SELECT channel_url, channel_name FROM subscribed_channels ORDER BY channel_name COLLATE NOCASE")
                self.all_channels = cur.fetchall()
                cur.execute("SELECT id, name FROM categories ORDER BY position")
                self.categories = cur.fetchall()
        except Exception as e:
            log.error("Failed to load subscription management data: %s", e)

    def _populate_category_filter(self):
        """Populates the category filter ComboBox."""
        self.categoryFilterCombo.Clear()
        # Translators: Filter option to show all subscribed channels.
        self.categoryFilterCombo.Append(_("All Channels"), -1)
        for cat_id, name in self.categories:
            self.categoryFilterCombo.Append(name, cat_id)
        self.categoryFilterCombo.SetSelection(0)

    def _populate_channel_list(self):
        """Populates the channel list based on the category filter."""
        selected_channel_url = self._current_channel_url
        self.channelListCtrl.DeleteAllItems()
        filter_selection = self.categoryFilterCombo.GetSelection()
        channels_to_show = []
        if filter_selection <= 0:
            channels_to_show = self.all_channels
        else:
            cat_id = self.categoryFilterCombo.GetClientData(filter_selection)
            try:
                with sqlite3.connect(self.db_path) as con:
                    cur = con.cursor()
                    cur.execute("""
                        SELECT sc.channel_url, sc.channel_name FROM subscribed_channels sc
                        JOIN channel_category_links ccl ON sc.channel_url = ccl.channel_url
                        WHERE ccl.category_id = ? ORDER BY sc.channel_name COLLATE NOCASE
                    """, (cat_id,))
                    channels_to_show = cur.fetchall()
            except Exception as e:
                log.error("Failed to filter channels by category: %s", e)
        new_selection_index = -1
        for index, (url, name) in enumerate(channels_to_show):
            self.channelListCtrl.InsertItem(index, name)
            original_index = next((i for i, v in enumerate(self.all_channels) if v[0] == url), -1)
            self.channelListCtrl.SetItemData(index, original_index)
            if url == selected_channel_url:
                new_selection_index = index
        if new_selection_index != -1:
            self.channelListCtrl.SetItemState(
                new_selection_index,
                wx.LIST_STATE_SELECTED | wx.LIST_STATE_FOCUSED,
                wx.LIST_STATE_SELECTED | wx.LIST_STATE_FOCUSED
            )
        elif self.channelListCtrl.GetItemCount() > 0:
            self.channelListCtrl.SetItemState(
                0,
                wx.LIST_STATE_SELECTED | wx.LIST_STATE_FOCUSED,
                wx.LIST_STATE_SELECTED | wx.LIST_STATE_FOCUSED
            )
            self.channelListCtrl.EnsureVisible(0)
            event = wx.ListEvent(wx.wxEVT_LIST_ITEM_SELECTED, self.channelListCtrl.GetId())
            event.SetIndex(0)
            wx.PostEvent(self.channelListCtrl.GetEventHandler(), event)
        self._update_ui_state()

    def _update_ui_state(self, event=None):
        """Enable/disable controls based on selection state."""
        has_any_channels = bool(self.all_channels)
        is_channel_selected = self.channelListCtrl.GetFirstSelected() != -1
        self.categoryFilterCombo.Enable(has_any_channels)
        self.channelListCtrl.Enable(has_any_channels)
        self.rightPanel.Show(has_any_channels)
        for ctrl in [self.categoryCheckList, self.contentTypesList, self.unsubBtn]:
            ctrl.Enable(is_channel_selected and has_any_channels)
        self.Layout()

    def _update_right_panel(self, event=None):
        """Load categories and content types for the selected channel."""
        self._update_ui_state()
        selected_index = self.channelListCtrl.GetFirstSelected()
        self.categoryCheckList.Clear()
        self.contentTypesList.CheckedItems = []
        if selected_index == -1:
            self._current_channel_url = None
            return
        original_index = self.channelListCtrl.GetItemData(selected_index)
        channel_url, __ = self.all_channels[original_index]
        self._current_channel_url = channel_url
        self._dirty = False   # reset หลังโหลดข้อมูลใหม่
        try:
            with sqlite3.connect(self.db_path) as con:
                cur = con.cursor()
                cur.execute("SELECT category_id FROM channel_category_links WHERE channel_url = ?", (channel_url,))
                assigned_cat_ids = {row[0] for row in cur.fetchall()}
                cur.execute("SELECT content_types FROM subscribed_channels WHERE channel_url = ?", (channel_url,))
                content_types_str = cur.fetchone()[0]
            self.categoryCheckList.Set([cat[1] for cat in self.categories])
            self.categoryCheckList.CheckedItems = [
                i for i, (cat_id, _) in enumerate(self.categories) if cat_id in assigned_cat_ids
            ]
            internal_types = ["videos", "shorts", "streams"]
            saved_types = content_types_str.split(',') if content_types_str else []
            self.contentTypesList.CheckedItems = [i for i, t in enumerate(internal_types) if t in saved_types]
        except Exception as e:
            log.error("Failed to update channel details panel: %s", e)

    def _on_subscription_added(self, new_channel_data):
        self.all_channels.append(new_channel_data)
        self.all_channels.sort(key=lambda x: x[1].lower())
        self._populate_channel_list()

    def _on_subscription_removed(self, data):
        channel_url_to_remove = data.get("channel_url")
        if not channel_url_to_remove:
            return
        if self._current_channel_url == channel_url_to_remove:
            self._current_channel_url = None
            self._dirty = False
        self.all_channels = [ch for ch in self.all_channels if ch[0] != channel_url_to_remove]
        self._populate_channel_list()

    def on_close(self, event):
        """Save pending changes before closing, then clean up."""
        self._save_current_channel()
        self.core.unregister_callback("subscription_added", self._on_subscription_added)
        self.core.unregister_callback("subscription_removed", self._on_subscription_removed)
        self.core._notify_callbacks("subscriptions_updated")
        self.__class__._instance = None
        self.Destroy()

    def on_view_channel_content(self, event):
        selected_index = self.channelListCtrl.GetFirstSelected()
        if selected_index == -1: return
        original_index = self.channelListCtrl.GetItemData(selected_index)
        channel_url, channel_name = self.all_channels[original_index]
        if not channel_url:
            ui.message(_("Error: Channel URL not found."))
            return
        menu = wx.Menu()
        menu_choices = {
            wx.ID_HIGHEST + 1: (_("Videos"),    "/videos",    False),
            wx.ID_HIGHEST + 2: (_("Shorts"),    "/shorts",    False),
            wx.ID_HIGHEST + 3: (_("Live"),      "/streams",   False),
            wx.ID_HIGHEST + 4: (_("Playlists"), "/playlists", True),
            wx.ID_HIGHEST + 5: (_("Podcasts"),  "/podcasts",  True),
        }
        for menu_id, (label, suffix, is_col) in menu_choices.items():
            menu.Append(menu_id, label)
        def on_menu_select(e):
            label, suffix, is_collection = menu_choices.get(e.GetId())
            full_url = channel_url.rstrip('/') + suffix
            title_text = _("Fetching {type} from {channel}...").format(channel=channel_name, type=label)
            thread_kwargs = {
                'url': full_url,
                'dialog_title_template': title_text,
                'content_type_label': label,
                'base_channel_url': channel_url,
                'base_channel_name': channel_name,
                'is_collection': is_collection,
            }
            threading.Thread(target=self.core._view_channel_worker, kwargs=thread_kwargs, daemon=True).start()
        menu.Bind(wx.EVT_MENU, on_menu_select)
        self.PopupMenu(menu)
        menu.Destroy()

    def on_add_subscription(self, event):
        try:
            url = api.getClipData()
            if not url or not self.core.is_youtube_url(url):
                ui.message(_("No valid YouTube URL found in clipboard."))
                return
        except Exception:
            # Translators: Error message when clipboard access fails.
            ui.message(_("Could not read from clipboard."))
            return
        threading.Thread(target=self.core.subscribe_to_channel_worker, args=(url,), daemon=True).start()

    def on_unsubscribe(self, event):
        selected_index = self.channelListCtrl.GetFirstSelected()
        if selected_index == -1:
            return
        original_index = self.channelListCtrl.GetItemData(selected_index)
        channel_url, channel_name = self.all_channels[original_index]
        # Translators: Confirmation message for unsubscribing. {name} is the channel name.
        msg_template = _("Are you sure you want to unsubscribe from '{name}'?")
        # Translators: Title for the unsubscribe confirmation dialog.
        confirm_title = _("Confirm Unsubscribe")
        if wx.MessageBox(msg_template.format(name=channel_name), confirm_title, wx.YES_NO | wx.ICON_QUESTION) != wx.YES:
            return
        threading.Thread(target=self.core.unsubscribe_from_channel_worker, args=(channel_url, channel_name), daemon=True).start()


class SubDialog(BaseDialogMixin, VideoActionMixin, wx.Dialog):
    """
    The definitive, fully-featured tabbed subscription feed dialog with all fixes applied.
    """
    _instance = None 

    def __new__(cls, *args, **kwargs):  # <--- ✅ เพิ่มเมธอดนี้ทั้งหมด
        if cls._instance is None:
            return super(SubDialog, cls).__new__(cls, *args, **kwargs)
        cls._instance.Raise()
        return cls._instance

    def __init__(self, parent, core_instance):
        if self.__class__._instance is not None:
            return
        # Translators: Title of the main subscription feed window.
        super().__init__(parent, title=_("Subscription Feed"))
        self.__class__._instance = self # Register the new instance
        self.core = core_instance
        self.db_path = self.core.get_profile_path("subscription.db")
        self.all_videos = []
        self.user_categories = []
        self.tab_order = []
        self.view_mode = "unseen" # unseen or all
        self.progress_dialog = None
        self.pending_focus_info = None
        panel = wx.Panel(self)
        mainSizer = wx.BoxSizer(wx.VERTICAL)
        
        self.notebook = wx.Notebook(panel)
        mainSizer.Add(self.notebook, 1, wx.EXPAND | wx.ALL, 5)

        btnSizer = wx.BoxSizer(wx.HORIZONTAL)
        # Translators: Button to add a new channel subscription.
        self.addBtn = wx.Button(panel, label=_("Add &new Subscription from clipboard URL."))
        # Translators: Button to refresh the subscription feed.
        self.updateBtn = wx.Button(panel, label=_("&Update Feed"))
        # Translators: Button to open more options menu.
        self.moreBtn = wx.Button(panel, label=_("&More..."))
        # Translators: Button to close the dialog.
        self.closeBtn = wx.Button(panel, wx.ID_CANCEL, label=_("C&lose"))

        btnSizer.Add(self.addBtn, 0, wx.RIGHT, 5)
        btnSizer.AddStretchSpacer()
        btnSizer.Add(self.updateBtn, 0, wx.RIGHT, 5)
        btnSizer.Add(self.moreBtn, 0, wx.RIGHT, 5)
        btnSizer.Add(self.closeBtn, 0)
        mainSizer.Add(btnSizer, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 10)

        panel.SetSizer(mainSizer)
        self.SetSize((950, 600))
        self.CentreOnScreen()
        
        self._build_all_tabs()
        
        self.core.register_callback("subscriptions_updated", self._on_subscriptions_updated)
        self.core.register_callback("sub_feed_progress", self._on_progress_update)
        
        self.Bind(wx.EVT_CLOSE, self.on_close)
        self.Bind(wx.EVT_CHAR_HOOK, self.on_char_hook)
        self.addBtn.Bind(wx.EVT_BUTTON, self.on_add_subscription)
        self.moreBtn.Bind(wx.EVT_BUTTON, self.on_more_menu)
        self.updateBtn.Bind(wx.EVT_BUTTON, self.on_update_feed)
        self.notebook.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGED, self.on_tab_changed)

    def on_close(self, event):
        if self.progress_dialog: self.progress_dialog.Destroy()
        self.core.unregister_callback("subscriptions_updated", self._on_subscriptions_updated)
        self.core.unregister_callback("sub_feed_progress", self._on_progress_update)
        current_tab_order = [str(self.notebook.GetPage(i).tab_id) for i in range(self.notebook.GetPageCount())]
        config.conf["YoutubePlus"]["subTabOrder"] = ",".join(current_tab_order)
        currentPage = self.notebook.GetCurrentPage()
        if currentPage:
            config.conf["YoutubePlus"]["lastSubTabId"] = str(currentPage.tab_id)
        self.__class__._instance = None
        self.Destroy()

    def _save_all_tab_positions(self):
        positions = {}
        for i in range(self.notebook.GetPageCount()):
            page = self.notebook.GetPage(i)
            if hasattr(page, 'listCtrl') and hasattr(page, 'tab_id'):
                idx = page.listCtrl.GetFirstSelected()
                positions[str(page.tab_id)] = idx if idx != -1 else 0
        return positions

    def _on_subscriptions_updated(self):
        currentPage = self.notebook.GetCurrentPage()
        last_tab_id = currentPage.tab_id if currentPage else "all"
        saved_positions = self._save_all_tab_positions()
        deleted_id = self.pending_focus_info.get('deleted_video_id') if self.pending_focus_info else None
        self.pending_focus_info = None
        if self.progress_dialog:
            self.progress_dialog.Update(self.progress_dialog.GetRange())
            self.progress_dialog = None
        self._build_all_tabs(
            select_tab_id=last_tab_id,
            saved_positions=saved_positions,
            deleted_video_id=deleted_id
        )
        
    def _build_all_tabs(self, select_tab_id=None, saved_positions=None, deleted_video_id=None):
        try:
            con = sqlite3.connect(self.db_path)
            cur = con.cursor()
            sort_order = config.conf["YoutubePlus"].get("sortOrder", "newest")
            order_by_clause = "ORDER BY v.id DESC" if sort_order == 'newest' else "ORDER BY v.id ASC"
            sql_query = ""
            if self.view_mode == "unseen":
                sql_query = f"SELECT v.video_id, v.channel_name, v.title, v.duration_str, v.channel_url, v.upload_date, v.content_type FROM videos v WHERE v.video_id NOT IN (SELECT video_id FROM seen_videos) {order_by_clause}"
            else:
                sql_query = f"SELECT v.video_id, v.channel_name, v.title, v.duration_str, v.channel_url, v.upload_date, v.content_type FROM videos v {order_by_clause}"
            cur.execute(sql_query)
            self.all_videos = [{'id': r[0], 'channel_name': r[1], 'title': r[2], 'duration_str': r[3], 'channel_url': r[4], 'upload_date': r[5], 'content_type': r[6]} for r in cur.fetchall()]
            cur.execute("SELECT id, name FROM categories ORDER BY position ASC")
            self.user_categories = cur.fetchall()
            con.close()
        except Exception as e:
            log.error("Failed to load data for SubDialog: %s", e)
            self.all_videos, self.user_categories = [], []
        # Translators: Default tab names for different types of content.
        fixed_tabs = [
            {'id': 'all', 'name': _("All")},
            {'id': 'videos', 'name': _("Videos")},
            {'id': 'shorts', 'name': _("Shorts")},
            {'id': 'streams', 'name': _("Live")}
        ]
        user_tabs = [{'id': cat_id, 'name': name} for cat_id, name in self.user_categories]
        default_order_tabs = fixed_tabs + user_tabs
        saved_order = config.conf["YoutubePlus"].get("subTabOrder", "").split(',')
        all_tabs_dict = {str(t['id']): t for t in default_order_tabs}
        self.tab_order = []
        if saved_order and saved_order[0]:
            for tab_id_str in saved_order:
                if tab_id_str in all_tabs_dict:
                    self.tab_order.append(all_tabs_dict.pop(tab_id_str))
        self.tab_order.extend(all_tabs_dict.values())
        self.notebook.DeleteAllPages()
        for tab_info in self.tab_order:
            page = self._create_tab_panel(
                tab_info['id'],
                saved_position=saved_positions.get(str(tab_info['id']), 0) if saved_positions else 0,
                deleted_video_id=deleted_video_id
            )
            self.notebook.AddPage(page, tab_info['name'])
        tab_to_select_id = str(select_tab_id) if select_tab_id is not None else config.conf["YoutubePlus"].get("lastSubTabId", "all")
        initial_selection = 0
        for i, tab_info in enumerate(self.tab_order):
            if str(tab_info['id']) == tab_to_select_id:
                initial_selection = i
                break
        self.notebook.SetSelection(initial_selection)
        if self.notebook.GetPageCount() > 0:
            self._update_dialog_title()
            self.notebook.GetCurrentPage().SetFocus()
        self.pending_focus_info = None  
        
    def _move_tab(self, direction):
        """
        Moves the current tab and then safely rebuilds the entire notebook UI
        to ensure a single, correct announcement from NVDA.
        """
        current_index = self.notebook.GetSelection()
        new_index = current_index + direction
        if new_index < 0 or new_index >= self.notebook.GetPageCount():
            return
        current_tab_info = self.tab_order.pop(current_index)
        self.tab_order.insert(new_index, current_tab_info)
        try:
            new_order_ids = [str(tab['id']) for tab in self.tab_order]
            config.conf["YoutubePlus"]["subTabOrder"] = ",".join(new_order_ids)
            with sqlite3.connect(self.db_path) as con:
                cur = con.cursor()
                cur.execute("BEGIN TRANSACTION")
                user_cat_pos = 0
                for tab_info in self.tab_order:
                    if isinstance(tab_info['id'], int):
                        cur.execute("UPDATE categories SET position = ? WHERE id = ?", (user_cat_pos, tab_info['id']))
                        user_cat_pos += 1
                con.commit()
            wx.CallAfter(self._build_all_tabs, select_tab_id=current_tab_info['id'])
        except Exception as e:
            log.error("Failed to reorder tabs: %s", e)
            # Translators: Error message when tab reordering fails.
            ui.message(_("Error reordering tabs."))
            
    def on_tab_changed(self, event):
        """
        Called when the user selects a different tab.
        Announces the new tab and updates the dialog title.
        """
        new_tab_index = event.GetSelection()
        new_tab_title = self.notebook.GetPageText(new_tab_index)
        self._update_dialog_title()
        ui.message(new_tab_title)
        currentPage = self.notebook.GetCurrentPage()
        if currentPage:
            self._update_tab_button_states(currentPage)
            wx.CallAfter(currentPage.SetFocus)
        event.Skip()

    def _update_dialog_title(self):
        """Helper method to update the dialog's title based on the current tab."""
        currentPage = self.notebook.GetCurrentPage()
        if not currentPage: return
        tab_title = self.notebook.GetPageText(self.notebook.GetSelection())
        active_profile = config.conf["YoutubePlus"]["activeProfile"]
        # Translators: The title of the subscription feed dialog. 
        # {tab_name} is the name of the current tab. {profile} is the active user profile name.
        full_title = _("Subscription Feed - {tab_name} - YoutubePlus").format(tab_name=tab_title) + " - [{profile}]".format(profile=active_profile)
        self.SetTitle(full_title)

    def _create_tab_panel(self, tab_id, saved_position=0, deleted_video_id=None):
        panel = wx.Panel(self.notebook)
        sizer = wx.BoxSizer(wx.VERTICAL)
        listCtrl = wx.ListCtrl(panel, style=wx.LC_REPORT | wx.LC_SINGLE_SEL)
        # Translators: Column headers for the video list.
        listCtrl.InsertColumn(0, _("Video Title"), width=350)
        # Translators: Header for the content type column (Video, Short, or Live).
        listCtrl.InsertColumn(1, _("Type"), width=80)
        # Translators: Header for the channel name column.
        listCtrl.InsertColumn(2, _("Channel Name"), width=200)
        # Translators: Header for the video duration column.
        listCtrl.InsertColumn(3, _("Duration"), width=120)
        sizer.Add(listCtrl, 1, wx.EXPAND | wx.ALL, 5)
        btnSizer = wx.BoxSizer(wx.HORIZONTAL)
        # Translators: Action button label.
        actionBtn = wx.Button(panel, label=_("&Action..."))
        # Translators: Copy button label.
        copyBtn = wx.Button(panel, label=_("&Copy..."))
        # Translators: Button to mark a video as seen.
        markSeenBtn = wx.Button(panel, label=_("Mark as &Seen"))
        btnSizer.Add(actionBtn, 0, wx.RIGHT, 5)
        btnSizer.Add(copyBtn, 0, wx.RIGHT, 5)
        btnSizer.Add(markSeenBtn, 0)
        sizer.Add(btnSizer, 0, wx.ALL, 5)
        panel.SetSizer(sizer)
        panel.listCtrl, panel.actionBtn, panel.copyBtn, panel.markSeenBtn = listCtrl, actionBtn, copyBtn, markSeenBtn
        panel.tab_id = tab_id
        actionBtn.Bind(wx.EVT_BUTTON, self.on_action_menu)
        copyBtn.Bind(wx.EVT_BUTTON, self.on_copy_menu)
        markSeenBtn.Bind(wx.EVT_BUTTON, self.on_mark_seen)
        listCtrl.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.on_open_video)
        listCtrl.Bind(wx.EVT_KEY_DOWN, self.on_list_key_down)
        listCtrl.Bind(wx.EVT_CONTEXT_MENU, self._on_list_right_click)
        listCtrl.Bind(wx.EVT_LIST_ITEM_SELECTED, lambda e, p=panel: self._update_tab_button_states(p))
        listCtrl.Bind(wx.EVT_LIST_ITEM_DESELECTED, lambda e, p=panel: self._update_tab_button_states(p))
        self._populate_list_for_panel(panel, saved_position=saved_position, deleted_video_id=deleted_video_id)
        return panel

    def _populate_list_for_panel(self, panel, saved_position=0, deleted_video_id=None):
        tab_id = panel.tab_id
        videos_to_show = []
        if tab_id == "all":
            videos_to_show = self.all_videos
        elif tab_id in ["videos", "shorts", "streams"]:
            videos_to_show = [v for v in self.all_videos if v.get('content_type') == tab_id]
        else:
            try:
                con = sqlite3.connect(self.db_path)
                cur = con.cursor()
                cur.execute("SELECT channel_url FROM channel_category_links WHERE category_id = ?", (tab_id,))
                channel_urls = {row[0] for row in cur.fetchall()}
                con.close()
                videos_to_show = [v for v in self.all_videos if v.get('channel_url') in channel_urls]
            except Exception as e:
                log.error("Failed to filter videos for category %s: %s", tab_id, e)
        
        panel.listCtrl.DeleteAllItems()
        panel.videos = videos_to_show
        # Translators: Map for content type display names.
        type_map = {
            "videos": _("Video"),
            "shorts": _("Shorts"),
            "streams": _("Live")
        }
        for index, video in enumerate(videos_to_show):
            # Translators: Default text for missing video information.
            na_text = _("N/A")
            panel.listCtrl.InsertItem(index, video.get('title', na_text))
            content_type = video.get('content_type', 'videos')
            display_type = type_map.get(content_type, _("Video"))
            panel.listCtrl.SetItem(index, 1, display_type)
            panel.listCtrl.SetItem(index, 2, video.get('channel_name', 'N/A'))
            panel.listCtrl.SetItem(index, 3, video.get('duration_str', 'N/A'))
        item_count = panel.listCtrl.GetItemCount()
        if item_count > 0:
            focus_index = 0
            if deleted_video_id:
                remaining_ids = [v.get('id') for v in videos_to_show]
                all_ids = [v.get('id') for v in self.all_videos]
                try:
                    deleted_pos = all_ids.index(deleted_video_id)
                    for next_id in all_ids[deleted_pos + 1:]:
                        if next_id in remaining_ids:
                            focus_index = remaining_ids.index(next_id)
                            break
                    else:
                        for prev_id in reversed(all_ids[:deleted_pos]):
                            if prev_id in remaining_ids:
                                focus_index = remaining_ids.index(prev_id)
                                break
                except ValueError:
                    focus_index = min(saved_position, item_count - 1)
            else:
                focus_index = min(saved_position, item_count - 1)

            panel.listCtrl.SetItemState(
                focus_index,
                wx.LIST_STATE_SELECTED | wx.LIST_STATE_FOCUSED,
                wx.LIST_STATE_SELECTED | wx.LIST_STATE_FOCUSED
            )
            panel.listCtrl.EnsureVisible(focus_index)
        self._update_tab_button_states(panel)

    def _update_tab_button_states(self, panel):
        has_selection = panel.listCtrl.GetFirstSelected() != -1
        panel.actionBtn.Enable(has_selection)
        panel.copyBtn.Enable(has_selection)
        panel.markSeenBtn.Enable(has_selection)
        
    def get_selected_video_info(self):
        currentPage = self.notebook.GetCurrentPage()
        if not currentPage: return None
        listCtrl = currentPage.listCtrl
        selected_index = listCtrl.GetFirstSelected()
        if selected_index == -1: return None
        return currentPage.videos[selected_index]

    def _on_list_right_click(self, event):
        video = self.get_selected_video_info()
        if not video:
            event.Skip()
            return
        menu = self.create_video_action_menu()
        menu.AppendSeparator()
        ID_UNSUB = wx.NewIdRef()
        menu.Append(ID_UNSUB, _("&Unsubscribe from this channel"))
        menu.Bind(wx.EVT_MENU, self.on_unsubscribe, id=ID_UNSUB)
        self.PopupMenu(menu)
        menu.Destroy()
    

    def on_copy_menu(self, event):
        video = self.get_selected_video_info()
        if not video: return
        menu = wx.Menu()
        # Translators: Menu item to copy the video title to clipboard.
        menu.Append(1, _("Copy &Title"))
        # Translators: Menu item to copy the video URL to clipboard.
        menu.Append(2, _("Copy Video &URL"))
        # Translators: Menu item to copy the channel name to clipboard.
        menu.Append(3, _("Copy &Channel Name"))
        # Translators: Menu item to copy the channel URL to clipboard.
        menu.Append(4, _("Copy C&hannel URL"))
        menu.AppendSeparator()
        # Translators: Menu item to copy a formatted summary of the video.
        menu.Append(5, _("Copy &Summary"))

        def on_select(e):
            id_map = {1: 'title', 2: 'url', 3: 'channel_name', 4: 'channel_url', 5: 'summary'}
            copy_type = id_map.get(e.GetId())
            if copy_type:
                self.on_copy(copy_type)
        menu.Bind(wx.EVT_MENU, on_select)
        self.PopupMenu(menu)
        menu.Destroy()

    def on_add_subscription(self, event):
        try:
            url = api.getClipData()
            if not url or not self.core.is_youtube_url(url):
                # Translators: Warning message when the clipboard doesn't contain a valid link.
                ui.message(_("No valid YouTube URL found in clipboard."))
                return
        except:
            # Translators: Error message when system clipboard cannot be accessed.
            ui.message(_("Could not read from clipboard."))
            return
        threading.Thread(target=self.core.subscribe_to_channel_worker, args=(url,), daemon=True).start()

    def on_more_menu(self, event):
            """Shows the 'More...' menu with added category management and pruning options."""
            menu = wx.Menu()
            ID_MARK_ALL, ID_TOGGLE_VIEW, ID_MANAGE_SUBS = wx.NewIdRef(count=3)
            ID_ADD_CAT, ID_RENAME_CAT, ID_REMOVE_CAT = wx.NewIdRef(count=3)
            ID_PRUNE_ALL = wx.NewIdRef()
            # Translators: Menu item to mark all videos in current tab as seen.
            menu.Append(ID_MARK_ALL, _("Mark &all in current tab as seen (control+delete)"))
            # Translators: Toggle menu item for view mode.
            toggle_label = _("Show all &videos (including seen)") if self.view_mode == 'unseen' else _("Show only &unseen videos")
            menu.Append(ID_TOGGLE_VIEW, toggle_label)
            # Translators: Menu item to open subscription management.
            menu.Append(ID_MANAGE_SUBS, _("&Manage subscriptions..."))
            menu.AppendSeparator()
            # Translators: Menu item to add a new custom category tab.
            menu.Append(ID_ADD_CAT, _("Add New &Category...\tCtrl+="))
            # Translators: Menu item to rename the current custom category tab.
            menu.Append(ID_RENAME_CAT, _("&Rename Current Category...\tF2"))
            # Translators: Menu item to delete the current custom category tab.
            menu.Append(ID_REMOVE_CAT, _("Remove Current Category...\tCtrl+-"))
            menu.AppendSeparator()
            # Translators: Menu item to delete all records from the video feed database.
            menu.Append(ID_PRUNE_ALL, _("Clear All Feed Videos..."))
            currentPage = self.notebook.GetCurrentPage()
            is_user_category = isinstance(currentPage.tab_id, int)
            menu.Enable(ID_RENAME_CAT, is_user_category)
            menu.Enable(ID_REMOVE_CAT, is_user_category)

            def on_menu_select(e):
                evt_id = e.GetId()
                if evt_id == ID_MARK_ALL: self.on_mark_all_seen()
                elif evt_id == ID_TOGGLE_VIEW: self.on_toggle_view()
                elif evt_id == ID_MANAGE_SUBS: self.on_manage_subscriptions(None)
                elif evt_id == ID_ADD_CAT: self.on_add_category()
                elif evt_id == ID_RENAME_CAT: self.on_rename_category()
                elif evt_id == ID_REMOVE_CAT: self.on_remove_category()
                elif evt_id == ID_PRUNE_ALL: self.core.prune_all_videos_worker()
            menu.Bind(wx.EVT_MENU, on_menu_select)
            self.PopupMenu(menu)
            menu.Destroy()
            
    def on_toggle_view(self):
        self.view_mode = 'all' if self.view_mode == 'unseen' else 'unseen'
        currentPage = self.notebook.GetCurrentPage()
        last_tab_id = currentPage.tab_id if currentPage else "all"
        self._build_all_tabs(select_tab_id=last_tab_id)

    def on_manage_subscriptions(self, event):
        currentPage = self.notebook.GetCurrentPage()
        if currentPage and hasattr(currentPage, 'listCtrl'):
            self.pending_focus_index = currentPage.listCtrl.GetFirstSelected()
        else:
            self.pending_focus_index = -1
        dlg = ManageSubscriptionsDialog(self, self.core)
        dlg.ShowModal()
        wx.CallAfter(self.notebook.GetCurrentPage().SetFocus)
        
    def on_update_feed(self, event):
        if self.core.is_long_task_running:
            # Translators: Message shown when an update is already happening.
            ui.message(_("An update is already in progress."))
            return
        threading.Thread(target=self._show_progress_and_update_worker, daemon=True).start()
    
    def _show_progress_and_update_worker(self):
        try:
            con = sqlite3.connect(self.db_path)
            cur = con.cursor()
            cur.execute("SELECT content_types FROM subscribed_channels")
            subscribed_channels_types = cur.fetchall()
            channel_count = len(subscribed_channels_types)
            total_tasks = sum(len(c[0].split(',')) for c in subscribed_channels_types if c[0])
            con.close()
        except Exception:
            total_tasks, channel_count = 1, 0

        def create_and_run():
            # Translators: Title of the progress dialog during update. {count} is number of channels.
            title = _("Updating Feed ({count} channels)").format(count=channel_count)
            # Translators: Initial status message in the progress dialog.
            status = _("Starting...")
            self.progress_dialog = wx.ProgressDialog(
                title, status,
                maximum=total_tasks if total_tasks > 0 else 1,
                parent=self,
                style=wx.PD_APP_MODAL | wx.PD_AUTO_HIDE | wx.PD_ELAPSED_TIME | wx.PD_REMAINING_TIME | wx.PD_CAN_ABORT
            )
            self.progress_dialog.Show()
            threading.Thread(target=self.core._update_subscription_feed_worker, args=("sub_feed_progress",), daemon=True).start()
        wx.CallAfter(create_and_run)

    def _on_progress_update(self, data):
        if not self.progress_dialog:
            return
        current = data.get("current", 0)
        message = data.get("message", "")
        keep_going, skip = self.progress_dialog.Update(current, message)
        if not keep_going:
            self.core.stop_subscription_update() # สมมติว่ามีฟังก์ชันนี้ใน Core สำหรับเซต stop flag
            self.progress_dialog.Destroy()
            self.progress_dialog = None
            # Translators: Notification when update is cancelled by user.
            ui.message(_("Update cancelled."))
            
    def on_action_menu(self, event):
        video = self.get_selected_video_info()
        if not video: return
        menu = self.create_video_action_menu()
        menu.AppendSeparator()
        ID_UNSUB = wx.NewIdRef()
        # Translators: Menu item to unsubscribe from a channel while browsing the feed.
        menu.Append(ID_UNSUB, _("&Unsubscribe from this channel"))
        menu.Bind(wx.EVT_MENU, self.on_unsubscribe, id=ID_UNSUB)
        self.PopupMenu(menu)
        menu.Destroy()

    def on_mark_seen(self, event):
        currentPage = self.notebook.GetCurrentPage()
        if not currentPage: return
        listCtrl = currentPage.listCtrl
        selected_index = listCtrl.GetFirstSelected()
        video_to_mark = self.get_selected_video_info()
        if not video_to_mark: return
        self.pending_focus_info = {
            'tab_id': currentPage.tab_id,
            'index': selected_index,
            'deleted_video_id': video_to_mark.get('id')
        }
        video_id = video_to_mark.get('id')
        if self.core.mark_videos_as_seen(video_id):
            # Translators: Brief notification when a video is marked as seen.
            self.core._notify_delete(_("Marked as seen."))
            
    def on_mark_all_seen(self, event=None):
        currentPage = self.notebook.GetCurrentPage()
        if not currentPage or not hasattr(currentPage, 'videos'): return
        videos_in_current_tab = currentPage.videos
        if not videos_in_current_tab:
            # Translators: Message shown when the user tries to mark all as seen in an empty tab.
            ui.message(_("There are no videos in this tab to mark as seen."))
            return
        # Translators: Confirmation prompt. {count} is the number of videos.
        msg = _("Are you sure you want to mark all {count} videos in this tab as seen?").format(count=len(currentPage.videos))
        # Translators: Title of confirmation dialog.
        title = _("Confirm")
        if wx.MessageBox(msg, title, wx.YES_NO | wx.ICON_QUESTION) != wx.YES:
            return
        video_ids = [v.get('id') for v in videos_in_current_tab if v.get('id')]
        if self.core.mark_videos_as_seen(video_ids):
            # Translators: Success message after marking all videos in a tab as seen.
            self.core._notify_delete(_("All videos in the current tab have been marked as seen."))
            
    def on_list_key_down(self, event):
        """Handles key presses on the list, including all shortcuts."""
        control_down = event.ControlDown()
        key_code = event.GetKeyCode()
        if control_down:
            if ord('1') <= key_code <= ord('9'):
                target_tab_index = key_code - ord('1')
                if target_tab_index < self.notebook.GetPageCount():
                    self.notebook.SetSelection(target_tab_index)
                return
            if key_code == ord('='):
                self.on_add_category()
                return
            elif key_code == ord('-'):
                self.on_remove_category()
                return
            elif key_code == wx.WXK_DELETE:
                self.on_mark_all_seen()
                return
            elif key_code in (wx.WXK_UP, wx.WXK_LEFT):
                self._move_tab(-1)
                return
            elif key_code in (wx.WXK_DOWN, wx.WXK_RIGHT):
                self._move_tab(1)
                return
            else:
                event.Skip()
                return
        if key_code == wx.WXK_F2:
            self.on_rename_category()
            return
        elif key_code == wx.WXK_DELETE: # Delete ธรรมดา
            self.on_mark_seen(event)
            return
        elif key_code in (wx.WXK_RETURN, wx.WXK_SPACE):
            self.handle_video_list_keys(event)
            return
        else:
            event.Skip()            
            
    def on_unsubscribe(self, event):
        video = self.get_selected_video_info()
        if not video: return
        channel_name = video.get('channel_name', 'this channel')
        # Translators: Confirmation message for unsubscribing. {channel} is the channel name.
        msg = _("Are you sure you want to unsubscribe from '{channel}'?").format(channel=video['channel_name'])
        # Translators: Title for the confirmation dialog.
        title = _("Confirm Unsubscribe")
        if wx.MessageBox(msg, title, wx.YES_NO | wx.ICON_QUESTION) != wx.YES:
            return
        threading.Thread(target=self.core.unsubscribe_from_channel_worker, args=(video['channel_url'], video['channel_name']), daemon=True).start()
        
    def on_add_category(self):
        """Handles adding a new user-defined category."""
        # Translators: Prompt for category name entry.
        msg = _("Enter new category name:")
        # Translators: Title of the category entry dialog.
        title = _("Add Category")
        with wx.TextEntryDialog(self, msg, title) as dlg:
            if dlg.ShowModal() == wx.ID_OK:
                new_name = dlg.GetValue().strip()
                if new_name:
                    try:
                        con = sqlite3.connect(self.db_path)
                        cur = con.cursor()
                        cur.execute("SELECT MAX(position) FROM categories")
                        max_pos = cur.fetchone()[0]
                        new_pos = (max_pos if max_pos is not None else -1) + 1
                        cur.execute("INSERT INTO categories (name, position) VALUES (?, ?)", (new_name, new_pos))
                        con.commit()
                        con.close()
                        self.core._notify_callbacks("subscriptions_updated")
                    except sqlite3.IntegrityError:
                        # Translators: Message when a user tries to create a category that already exists.
                        ui.message(_("A category with this name already exists."))
                    except Exception as e:
                        log.error("Failed to add category: %s", e)
                        # Translators: Generic error message for category creation failure.
                        ui.message(_("Error adding category."))
        wx.CallAfter(self.notebook.GetCurrentPage().SetFocus)

    def on_rename_category(self):
        """Handles renaming the current user-defined category."""
        currentPage = self.notebook.GetCurrentPage()
        if not currentPage or not isinstance(currentPage.tab_id, int):
            # Translators: Warning when user tries to rename a non-removable system tab (e.g. "All").
            ui.message(_("This is a fixed tab and cannot be renamed."))
            return
        cat_id = currentPage.tab_id
        old_name = self.notebook.GetPageText(self.notebook.GetSelection())
        # Translators: Prompt to rename category. {name} is current name.
        msg = _("Enter new name for '{name}':").format(name=old_name)
        # Translators: Title of the rename dialog.
        title = _("Rename Category")
        with wx.TextEntryDialog(self, msg, title, value=old_name) as dlg:
            if dlg.ShowModal() == wx.ID_OK:
                new_name = dlg.GetValue().strip()
                if new_name and new_name != old_name:
                    try:
                        con = sqlite3.connect(self.db_path)
                        cur = con.cursor()
                        cur.execute("UPDATE categories SET name = ? WHERE id = ?", (new_name, cat_id))
                        con.commit()
                        con.close()
                        self.core._notify_callbacks("subscriptions_updated")
                    except sqlite3.IntegrityError:
                        # Translators: Error message shown when the user tries to create a category with a name that is already in the database.
                        ui.message(_("A category with this name already exists."))
                    except Exception as e:
                        log.error("Failed to rename category: %s", e)
                        # Translators: Generic error for rename failure.
                        ui.message(_("Error renaming category."))
        wx.CallAfter(self.notebook.GetCurrentPage().SetFocus)

    def on_remove_category(self):
        """Handles removing the current user-defined category."""
        currentPage = self.notebook.GetCurrentPage()
        if not currentPage or not isinstance(currentPage.tab_id, int):
            # Translators: Warning when user tries to delete a system tab.
            ui.message(_("This is a fixed tab and cannot be removed."))
            return
        cat_id = currentPage.tab_id
        name = self.notebook.GetPageText(self.notebook.GetSelection())
        # Translators: Confirmation prompt for deletion. {name} is category name.
        msg = _("Are you sure you want to remove the '{name}' category?").format(name=name)
        # Translators: Title of confirm removal dialog.
        title = _("Confirm Removal")
        if wx.MessageBox(msg, title, wx.YES_NO | wx.ICON_QUESTION) != wx.YES:
            return
        try:
            con = sqlite3.connect(self.db_path)
            cur = con.cursor()
            cur.execute("DELETE FROM categories WHERE id = ?", (cat_id,))
            con.commit()
            con.close()
            self.core._notify_callbacks("subscriptions_updated")
            # Translators: Success notification. {name} is the deleted category.
            self.core._notify_delete(_("Category '{name}' removed.").format(name=name))
        except Exception as e:
            log.error("Failed to remove category: %s", e)
            # Translators: Generic error for removal failure.
            self.core._notify_error(_("Error removing category."))
        wx.CallAfter(self.notebook.GetCurrentPage().SetFocus)
        
class ProfileManagementDialog(wx.Dialog):
    
    def __init__(self, parent):
        # Translators: Title of the profile management dialog
        super().__init__(parent, title=_("Manage User Profiles"))
        self.base_data_path = os.path.join(globalVars.appArgs.configPath, "YoutubePlus")
        self.needs_restart = False
        
        mainSizer = wx.BoxSizer(wx.VERTICAL)
        sHelper = gui.guiHelper.BoxSizerHelper(self, orientation=wx.VERTICAL)
        
        # Translators: Label for the profiles list
        self.profilesList = sHelper.addItem(wx.ListBox(self, choices=self._get_profiles(), style=wx.LB_SINGLE))
        
        buttonSizer = wx.BoxSizer(wx.HORIZONTAL)
        # Translators: Button to add a new profile
        self.addButton = wx.Button(self, label=_("&Add"))
        # Translators: Button to rename a profile
        self.renameButton = wx.Button(self, label=_("&Rename"))
        # Translators: Button to delete a profile
        self.deleteButton = wx.Button(self, label=_("&Delete"))
        
        buttonSizer.Add(self.addButton)
        buttonSizer.Add(self.renameButton)
        buttonSizer.Add(self.deleteButton)
        
        mainSizer.Add(sHelper.sizer, proportion=1, flag=wx.ALL | wx.EXPAND, border=10)
        mainSizer.Add(buttonSizer, flag=wx.ALIGN_CENTER | wx.BOTTOM, border=10)
        
        # Translators: Button to close the dialog
        closeBtn = wx.Button(self, id=wx.ID_CANCEL, label=_("C&lose"))
        mainSizer.Add(closeBtn, flag=wx.ALIGN_RIGHT | wx.ALL, border=10)
        
        self.SetSizer(mainSizer)
        mainSizer.Fit(self)

        if self.profilesList.GetCount() > 0:
            self.profilesList.SetSelection(0)
        self.profilesList.SetFocus()

        self.addButton.Bind(wx.EVT_BUTTON, self.on_add)
        self.renameButton.Bind(wx.EVT_BUTTON, self.on_rename)
        self.deleteButton.Bind(wx.EVT_BUTTON, self.on_delete)
        closeBtn.Bind(wx.EVT_BUTTON, self.on_close)
        self.profilesList.Bind(wx.EVT_KEY_DOWN, self.on_list_key_down)

    def on_list_key_down(self, event):
        key_code = event.GetKeyCode()
        if key_code == wx.WXK_F2:
            self.on_rename(None)
        elif key_code == wx.WXK_DELETE:
            self.on_delete(None)
        else:
            event.Skip()

    def _get_profiles(self):
        if not os.path.exists(self.base_data_path):
            return ["default"]
        profiles = [f for f in os.listdir(self.base_data_path) if os.path.isdir(os.path.join(self.base_data_path, f)) and f != "_back_ups_db"]
        return sorted(profiles) if profiles else ["default"]

    def on_add(self, event):
        # Translators: Message asking the user to enter a name for the new profile.
        msg = _("Enter new profile name:")
        # Translators: Title of the dialog for adding a new profile.
        title = _("Add Profile")
        with wx.TextEntryDialog(self, msg, title) as dlg:
            if dlg.ShowModal() == wx.ID_OK:
                name = dlg.GetValue().strip()
                if name:
                    safe_name = "".join([c for c in name if c.isalnum() or c in (' ', '_', '-')]).strip()
                    path = os.path.join(self.base_data_path, safe_name)
                    if not os.path.exists(path):
                        os.makedirs(path)
                        self.profilesList.Set(self._get_profiles())
                        idx = self.profilesList.FindString(safe_name)
                        if idx != wx.NOT_FOUND:
                            self.profilesList.SetSelection(idx)
                        self.profilesList.SetFocus()
                    else:
                        # Translators: Error when profile exists
                        gui.messageBox(_("Profile already exists."), _("Error"), wx.OK | wx.ICON_ERROR)

    def on_rename(self, event):
        old_name = self.profilesList.GetStringSelection()
        if not old_name: return
        # Translators: Message for renaming a profile. {name} is the current name of the profile.
        msg = _("Rename profile '{name}' to:").format(name=old_name)
        # Translators: Title of the profile renaming dialog.
        title = _("Rename Profile")
        with wx.TextEntryDialog(self, msg, title, value=old_name) as dlg:
            if dlg.ShowModal() == wx.ID_OK:
                new_name = dlg.GetValue().strip()
                if not new_name or new_name == old_name: return
                new_name = "".join([c for c in new_name if c.isalnum() or c in (' ', '_', '-')]).strip()
                old_path = os.path.join(self.base_data_path, old_name)
                new_path = os.path.join(self.base_data_path, new_name)
                if os.path.exists(new_path):
                    # Translators: Error message
                    gui.messageBox(_("A profile with this name already exists."), _("Error"), wx.OK | wx.ICON_ERROR)
                    return
                try:
                    os.rename(old_path, new_path)
                    current_active = config.conf["YoutubePlus"].get("activeProfile", "default")
                    if old_name == current_active:
                        config.conf["YoutubePlus"]["activeProfile"] = new_name
                        self.needs_restart = True
                    self.profilesList.Set(self._get_profiles())
                    idx = self.profilesList.FindString(new_name)
                    if idx != wx.NOT_FOUND:
                        self.profilesList.SetSelection(idx)
                    self.profilesList.SetFocus()
                except Exception as e:
                    gui.messageBox(_("Failed to rename profile: {e}").format(e=e), _("Error"), wx.OK | wx.ICON_ERROR)

    def on_delete(self, event):
        name = self.profilesList.GetStringSelection()
        if not name: return
        if name == "default":
            # Translators: Error message for default profile
            gui.messageBox(_("The default profile cannot be deleted."), _("Error"), wx.OK | wx.ICON_ERROR)
            return
        current_active = config.conf["YoutubePlus"].get("activeProfile", "default")
        if name == current_active:
            # Translators: Error when trying to delete active profile
            gui.messageBox(_("Cannot delete the profile currently in use."), _("Error"), wx.OK | wx.ICON_ERROR)
            return
        # Translators: Confirmation message before deleting a profile. {name} is the profile name.
        confirm_msg = _("Delete profile '{name}' and all its data?").format(name=name)
        # Translators: Title of the profile deletion confirmation dialog.
        confirm_title = _("Confirm Delete")
        if gui.messageBox(confirm_msg, confirm_title, wx.YES_NO | wx.ICON_WARNING) == wx.YES:
            try:
                shutil.rmtree(os.path.join(self.base_data_path, name))
                self.profilesList.Set(self._get_profiles())
                if self.profilesList.GetCount() > 0:
                    self.profilesList.SetSelection(0)
                self.profilesList.SetFocus()
            except Exception as e:
                # Translators: Error message when profile deletion fails. {e} is the technical error.
                gui.messageBox(_("Failed to delete profile: {e}").format(e=e), _("Error"), wx.OK | wx.ICON_ERROR)

    def on_close(self, event):
        if self.needs_restart:
            wx.CallAfter(self._do_restart)
        self.Destroy()

    def _do_restart(self):
        # Translators: Message asking to restart NVDA after profile modification
        msg = _("The active profile has been modified. NVDA must be restarted to apply changes. Restart now?")
        # Translators: Restart confirmation title
        title = _("Restart NVDA")
        if gui.messageBox(msg, title, wx.YES_NO | wx.ICON_QUESTION) == wx.YES:
            globalCommands.commands.script_restart(None)
            
class DownloadProgressDialog(wx.Dialog):
    _ROW_FILENAME = 0
    _ROW_PROGRESS = 1
    _ROW_SIZE     = 2
    _ROW_SPEED    = 3
    _ROW_ETA      = 4
    _ROW_STATUS   = 5

    def __init__(self, parent, core):
        super().__init__(
            parent,
            title=_("Downloading..."),
            style=wx.DEFAULT_DIALOG_STYLE | wx.STAY_ON_TOP
        )
        self.core = core
        self._closed = False
        self._is_pulse_mode = False

        main_sizer = wx.BoxSizer(wx.VERTICAL)

        self.listCtrl = wx.ListCtrl(
            self,
            style=wx.LC_REPORT | wx.LC_SINGLE_SEL | wx.BORDER_SUNKEN
        )
        # Translators: Column headers in the download progress dialog.
        self.listCtrl.InsertColumn(0, _("Field"), width=120)
        self.listCtrl.InsertColumn(1, _("Value"), width=280)

        row_labels = [
            _("File"),      # _ROW_FILENAME
            _("Progress"),  # _ROW_PROGRESS
            _("Size"),      # _ROW_SIZE
            _("Speed"),     # _ROW_SPEED
            _("ETA"),       # _ROW_ETA
            _("Status"),    # _ROW_STATUS
        ]
        for label in row_labels:
            idx = self.listCtrl.InsertItem(self.listCtrl.GetItemCount(), label)
            self.listCtrl.SetItem(idx, 1, "-")

        self._set_value(self._ROW_STATUS, _("Preparing..."))

        row_h = self.listCtrl.GetItemRect(0).height if self.listCtrl.GetItemCount() else 22
        self.listCtrl.SetMinSize((-1, row_h * (len(row_labels) + 1)))

        main_sizer.Add(self.listCtrl, 1, wx.ALL | wx.EXPAND, 10)

        self.gauge = wx.Gauge(self, range=100, size=(-1, 14))
        main_sizer.Add(self.gauge, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM | wx.EXPAND, 10)

        # Translators: Cancel button in the download progress dialog.
        self.cancelBtn = wx.Button(self, label=_("&Cancel"))
        main_sizer.Add(self.cancelBtn, 0, wx.ALL | wx.ALIGN_CENTER, 8)

        self.SetSizerAndFit(main_sizer)
        self.SetMinSize((430, -1))
        self.CentreOnScreen()

        self.cancelBtn.Bind(wx.EVT_BUTTON, self._on_cancel)
        self.Bind(wx.EVT_CLOSE, self._on_close)

        self._pulse_timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self._on_pulse_timer, self._pulse_timer)

        self.core.register_callback("download_started", self._on_download_started)
        self.core.register_callback("download_progress", self._on_progress)

    def _set_value(self, row_idx, text):
        self.listCtrl.SetItem(row_idx, 1, text)

    @staticmethod
    def _fmt_speed(bps):
        if not bps:
            return "-"
        if bps >= 1_048_576:
            return f"{bps / 1_048_576:.1f} MB/s"
        if bps >= 1024:
            return f"{bps / 1024:.0f} KB/s"
        return f"{bps:.0f} B/s"

    @staticmethod
    def _fmt_eta(seconds):
        if seconds is None or seconds < 0:
            return "-"
        seconds = int(seconds)
        h, rem = divmod(seconds, 3600)
        m, s = divmod(rem, 60)
        if h:
            return f"{h:02d}:{m:02d}:{s:02d}"
        return f"{m:02d}:{s:02d}"

    @staticmethod
    def _fmt_bytes(b):
        if not b:
            return "-"
        if b >= 1_073_741_824:
            return f"{b / 1_073_741_824:.2f} GB"
        if b >= 1_048_576:
            return f"{b / 1_048_576:.1f} MB"
        if b >= 1024:
            return f"{b / 1024:.0f} KB"
        return f"{b} B"

    def _on_download_started(self, data=None):
        if self._closed:
            return
        title = (data or {}).get('title', '')
        if title:
            self._set_value(self._ROW_FILENAME, title)
            # Translators: Dialog title while a file is downloading. {title} is the file name.
            self.SetTitle(_("Downloading: {title}").format(title=title))

    def _on_progress(self, data=None):
        if self._closed:
            return
        data = data or {}
        status = data.get('status', 'downloading')

        if status == 'downloading':
            percent = data.get('percent', -1)
            speed   = data.get('speed', 0)
            eta     = data.get('eta')
            dl      = data.get('downloaded_bytes', 0)
            total   = data.get('total_bytes', 0)

            if percent >= 0:
                if self._is_pulse_mode:
                    self._pulse_timer.Stop()
                    self._is_pulse_mode = False
                self.gauge.SetValue(min(percent, 100))
                # Translators: Progress percentage. {pct} is 0-100.
                self._set_value(self._ROW_PROGRESS, _("{pct}%").format(pct=percent))
                if dl and total:
                    self._set_value(self._ROW_SIZE,
                        f"{self._fmt_bytes(dl)} / {self._fmt_bytes(total)}")
                self._set_value(self._ROW_SPEED, self._fmt_speed(speed))
                self._set_value(self._ROW_ETA,   self._fmt_eta(eta))
                # Translators: Status while downloading.
                self._set_value(self._ROW_STATUS, _("Downloading"))
            else:
                if not self._is_pulse_mode:
                    self._is_pulse_mode = True
                    self._pulse_timer.Start(150)
                self._set_value(self._ROW_PROGRESS, "-")
                if dl:
                    self._set_value(self._ROW_SIZE, self._fmt_bytes(dl))
                self._set_value(self._ROW_SPEED, self._fmt_speed(speed))
                self._set_value(self._ROW_ETA,   "-")
                # Translators: Status while downloading (size unknown).
                self._set_value(self._ROW_STATUS, _("Downloading"))

        elif status == 'finished':
            self._pulse_timer.Stop()
            self._is_pulse_mode = False
            self.gauge.SetValue(100)
            self._set_value(self._ROW_PROGRESS, "100%")
            # Translators: Status while yt-dlp wraps up the file.
            self._set_value(self._ROW_STATUS, _("Finishing..."))

        elif status in ('complete', 'cancelled', 'error'):
            self._safe_close()

    def _on_pulse_timer(self, event):
        if not self._closed:
            self.gauge.Pulse()

    def _on_close(self, event):
        if not self._closed:
            self.core.cancel_download()
        self._safe_close()
        
    def _on_cancel(self, event):
        self.core.cancel_download()
        self.cancelBtn.Disable()
        self._set_value(self._ROW_STATUS, _("Cancelling..."))
        self._cancel_timeout_timer = wx.CallLater(3000, self._safe_close)
        
    def _safe_close(self):
        if self._closed:
            return
        self._closed = True
        self._pulse_timer.Stop()
        if hasattr(self, '_cancel_timeout_timer') and self._cancel_timeout_timer.IsRunning():
            self._cancel_timeout_timer.Stop()
        self.core.unregister_callback("download_started", self._on_download_started)
        self.core.unregister_callback("download_progress", self._on_progress)
        self.Destroy()

