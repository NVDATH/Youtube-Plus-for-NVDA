# -*- coding: utf-8 -*-
# dialogs.py for YoutubePlus NVDA Addon

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
    #"cookieMode": "string(default='none')",
    "exportPath": "string()",
    "subDialogViewMode": "string(default='unseen')",
    "searchResultCount": "integer(default=20, min=5, max=100)"
}
config.conf.spec["YoutubePlus"] = confspec

def sanitize_filename(filename):
    filename = unicodedata.normalize('NFC', filename)
    allowed_pattern = r'[^a-zA-Z0-9\u0E00-\u0E7F \-\.]'
    sanitized = re.sub(allowed_pattern, ' ', filename)
    sanitized = re.sub(r'\s+', ' ', sanitized).strip()
    return sanitized

class BaseDialogMixin:
    """A mixin to provide common dialog functionality, like closing on Escape."""
    def on_char_hook(self, event):
        if event.GetKeyCode() == wx.WXK_ESCAPE:
            self.Close()
        else:
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

--- Help ---
- H: Show this help dialog
""")

class InfoDialog(BaseInfoDialog):
    """Dialog to show video info, inherits from BaseInfoDialog."""
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
            else: event.Skip()
        else: event.Skip()

    def processKey(self, event):
        if event.ControlDown() and event.GetKeyCode() == ord('C'):
            self.onCopy(event)
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
        if key == wx.WXK_ESCAPE: self.Close()
        elif altDown:
            if key == ord("C"): self.onCopy(event)
            elif key == ord("E"): self.onExport(event)
            elif key == ord("L"): self.Close()
            elif key == ord("S"): self.searchTextCtrl.SetFocus()
            else: event.Skip()
        else: event.Skip()

    def processKey(self, event):
        if event.ControlDown() and event.GetKeyCode() == ord('C'):
            self.onCopy(event)
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
        ui.message(_("Getting data for '{title}'...").format(title=video.get('title')))
        threading.Thread(target=self.core.get_data_for_url, args=(url,), daemon=True).start()

    def on_download_video(self, event):
        video = self.get_selected_video_info()
        if not video: return
        video_id = video.get('id') or video.get('video_id')
        if not video_id:
            # Translators: Error message.
            return ui.message(_("Video ID not found."))
        url = f"https://youtube.com/watch?v={video_id}"
        threading.Thread(target=self.core._direct_download_worker, args=(url, 'video'), daemon=True).start()

    def on_download_audio(self, event):
        video = self.get_selected_video_info()
        if not video: return
        video_id = video.get('id') or video.get('video_id')
        if not video_id: 
            # Translators: Error message.
            return ui.message(_("Video ID not found."))
        url = f"https://youtube.com/watch?v={video_id}"
        threading.Thread(target=self.core._direct_download_worker, args=(url, 'audio'), daemon=True).start()

    def on_open_channel(self, event):
        video = self.get_selected_video_info()
        if not video or not video.get('channel_url'): return
        webbrowser.open(video['channel_url'])

    def on_copy(self, copy_type):
            """Handles copying a specific piece of video data to the clipboard."""
            video = self.get_selected_video_info()
            if not video: return
            video_id = video.get('id') or video.get('video_id')
            if not video_id: return
            text_to_copy = ""
            if copy_type == 'title':
                text_to_copy = video.get('title', '')
            elif copy_type == 'url':
                text_to_copy = f"https://youtu.be/{video_id}"
            elif copy_type == 'channel_name':
                text_to_copy = video.get('channel_name', '')
            elif copy_type == 'channel_url':
                text_to_copy = video.get('channel_url', '')
            elif copy_type == 'summary':
                # Translators: Labels used when copying video summary to clipboard.
                text_to_copy = (
                    _("Title: {title}\n").format(title=video.get('title', '')) +
                    _("Channel: {channel}\n").format(channel=video.get('channel_name', '')) +
                    _("URL: ") + "https://youtu.be/{id}".format(id=video_id)
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
        suffix_map = {"videos": "/videos", "shorts": "/shorts", "streams": "/streams"}
        label_map = {"videos": _("Videos"), "shorts": _("Shorts"), "streams": _("Live")}
        suffix = suffix_map.get(content_type, "/videos")
        label = label_map.get(content_type, _("Content"))
        full_url = channel_url.rstrip('/') + suffix
        # Translators: Status message when fetching specific content from a channel.
        # {type} will be Videos, Shorts, or Live.
        title_template = _("Fetching {type} from {channel}...").format(channel=channel_name, type=label)
        thread_kwargs = {
            'url': full_url, 'dialog_title_template': title_template, 'content_type_label': label,
            'base_channel_url': channel_url, 'base_channel_name': channel_name
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
        elif action == "add__to_watchlist":
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

class BaseVideoListPanel(wx.Panel, VideoActionMixin):
    # Class-level clipboard shared across all instances (enables cross-list paste)
    _clipboard = []        # list of item dicts
    _clipboard_is_cut = False
    _clipboard_source = None  # reference to the panel that did the cut/copy

    def __init__(self, parent, core_instance):
        super().__init__(parent)
        self.core = core_instance
        self.items = []
        self.filtered_items = []
        self._is_first_load = True
        self.last_selected_item_before_search = None
        self.file_path = self._get_file_path()
        self.callback_topic = self._get_callback_topic()
        mainSizer = wx.BoxSizer(wx.VERTICAL)
        # Multi-select: removed wx.LC_SINGLE_SEL
        self.listCtrl = wx.ListCtrl(self, style=wx.LC_REPORT)
        self._create_list_columns(self.listCtrl)
        mainSizer.Add(self.listCtrl, 1, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 10)
        btnSizer = wx.BoxSizer(wx.HORIZONTAL)
        self._create_extra_buttons(self, btnSizer)
        btnSizer.AddStretchSpacer()
        self.addBtn = wx.Button(self, label=self._get_add_button_label())
        # Translators: Button to remove the selected item(s) from the list.
        self.removeBtn = wx.Button(self, label=_("&Remove"))
        btnSizer.Add(self.addBtn, 0, wx.RIGHT, 5)
        btnSizer.Add(self.removeBtn, 0, wx.RIGHT, 5)
        mainSizer.Add(btnSizer, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 10)
        self.SetSizer(mainSizer)
        if self.callback_topic:
            self.core.register_callback(self.callback_topic, self.refresh_data)
        self._load_data()
        self._populate_list()
        self._update_button_states()
        self.addBtn.Bind(wx.EVT_BUTTON, self.on_add)
        self.removeBtn.Bind(wx.EVT_BUTTON, self.on_remove)
        self.listCtrl.Bind(wx.EVT_KEY_DOWN, self.on_list_key_down)
        self.listCtrl.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.on_open_video)
        self.listCtrl.Bind(wx.EVT_LIST_ITEM_SELECTED, self.on_list_item_selected)
        self.listCtrl.Bind(wx.EVT_LIST_ITEM_DESELECTED, self.on_list_item_selected)

    def _get_file_path(self):
        raise NotImplementedError

    def _get_callback_topic(self):
        raise NotImplementedError

    def _get_add_button_label(self):
        raise NotImplementedError

    def _get_search_fields(self, item):
        return [item.get('title', ''), item.get('channel_name', '')]

    def _get_item_title_for_messages(self, item):
        return item.get('title', 'N/A')

    def _create_list_columns(self, list_ctrl):
        # Translators: Column header for video title.
        list_ctrl.InsertColumn(0, _("Title"), width=350)
        # Translators: Column header for channel name.
        list_ctrl.InsertColumn(1, _("Channel"), width=200)
        # Translators: Column header for video duration.
        list_ctrl.InsertColumn(2, _("Duration"), width=120)

    def _create_extra_buttons(self, panel, sizer):
        # Translators: Button to open action menu.
        self.actionBtn = wx.Button(panel, label=_("&Action..."))
        # Translators: Button to open copy menu.
        self.copyBtn = wx.Button(panel, label=_("&Copy..."))
        sizer.Add(self.actionBtn, 0, wx.RIGHT, 5)
        sizer.Add(self.copyBtn, 0, wx.RIGHT, 5)
        self.actionBtn.Bind(wx.EVT_BUTTON, self.on_action_menu)
        self.copyBtn.Bind(wx.EVT_BUTTON, self.on_copy_menu)

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
        self.filtered_items = self.items[:]

    def _save_data(self):
        with self.core._fav_file_lock:
            try:
                with open(self.file_path, 'w', encoding='utf-8') as f:
                    json.dump(self.items, f, indent=2, ensure_ascii=False)
            except (IOError, OSError):
                # Translators: Error message when data cannot be saved to disk.
                ui.message(_("Error: Could not save data."))

    def _populate_list(self):
        self.listCtrl.Freeze()
        try:
            self.listCtrl.DeleteAllItems()
            for index, item in enumerate(self.filtered_items):
                self.listCtrl.InsertItem(index, item.get('title', 'N/A'))
                self.listCtrl.SetItem(index, 1, item.get('channel_name', 'N/A'))
                self.listCtrl.SetItem(index, 2, item.get('duration_str', ''))
                if self._is_first_load and self.listCtrl.GetItemCount() > 0:
                    self.listCtrl.SetItemState(0, wx.LIST_STATE_SELECTED | wx.LIST_STATE_FOCUSED,
                                                wx.LIST_STATE_SELECTED | wx.LIST_STATE_FOCUSED)
                    self._is_first_load = False
        finally:
            self.listCtrl.Thaw()
            
    def _get_selected_items(self):
        """Return list of selected items in current view order."""
        selected = []
        idx = self.listCtrl.GetFirstSelected()
        while idx != -1:
            selected.append(self.filtered_items[idx])
            idx = self.listCtrl.GetNextSelected(idx)
        return selected

    def _get_item_unique_key(self, item):
        """Return a value that uniquely identifies an item (URL preferred)."""
        return item.get('url') or item.get('title', '')

    def refresh_data(self, data=None):
        if not self.listCtrl:
            return
        self._load_data()
        current_search = getattr(self, '_saved_search_text', "")  # ← ดึงค่าที่จำไว้
        self.on_search(current_search)
        if data and data.get("action") == "add":
            count = self.listCtrl.GetItemCount()
            if count > 0:
                last_index = count - 1
                self.listCtrl.SetItemState(last_index, wx.LIST_STATE_SELECTED | wx.LIST_STATE_FOCUSED,
                                           wx.LIST_STATE_SELECTED | wx.LIST_STATE_FOCUSED)
                self.listCtrl.EnsureVisible(last_index)
        self._update_button_states()
        
    def _update_button_states(self):
        is_not_empty = bool(self.items)
        is_selected = self.listCtrl.GetFirstSelected() != -1
        self.removeBtn.Enable(is_not_empty and is_selected)
        self.actionBtn.Enable(is_not_empty and is_selected)
        self.copyBtn.Enable(is_not_empty and is_selected)

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
        # Translators: Menu items for copying specific video information.
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

    def on_remove(self, event):
        selected_items = self._get_selected_items()
        if not selected_items:
            return
        first_index = self.listCtrl.GetFirstSelected()
        count = len(selected_items)
        if count == 1:
            title = self._get_item_title_for_messages(selected_items[0])
            # Translators: Confirmation dialog message before deleting a single item.
            confirm_msg = _("Are you sure you want to remove '{title}'?").format(title=title)
        else:
            # Translators: Confirmation dialog message before deleting multiple items. {count} is the number of items.
            confirm_msg = _("Are you sure you want to remove {count} selected items?").format(count=count)
        # Translators: Title of the confirmation dialog for removal.
        confirm_title = _("Confirm Removal")
        if wx.MessageBox(confirm_msg, confirm_title, wx.YES_NO | wx.ICON_QUESTION, self) != wx.YES:
            return
        for item in selected_items:
            self.items.remove(item)
        self._save_data()
        self.on_search("")
        item_count = self.listCtrl.GetItemCount()
        if item_count > 0:
            new_selection = min(first_index, item_count - 1)
            self.listCtrl.SetItemState(new_selection, wx.LIST_STATE_SELECTED | wx.LIST_STATE_FOCUSED,
                                       wx.LIST_STATE_SELECTED | wx.LIST_STATE_FOCUSED)
            self.listCtrl.EnsureVisible(new_selection)
        self._update_button_states()
        wx.CallAfter(self.listCtrl.SetFocus)
        # Translators: Notification spoken by NVDA after item(s) are removed.
        self.core._notify_delete(_("Item removed.") if count == 1 else
                                 _("{count} items removed.").format(count=count))

    def on_add(self, event):
        try:
            url = api.getClipData()
            if not url or not self.core.is_youtube_url(url):
                # Translators: Message when the clipboard does not contain a YouTube link.
                ui.message(_("No valid YouTube URL found in clipboard."))
                return
        except Exception:
            # Translators: Error message when clipboard access fails.
            ui.message(_("Could not read from clipboard."))
            return
        threading.Thread(target=self._add_worker(), args=(url,), daemon=True).start()
        
    def _add_worker(self):
        raise NotImplementedError

    # ---------- Cut / Copy / Paste ----------

    def on_list_copy(self):
        """Ctrl+C — copy selected items to class-level clipboard."""
        selected = self._get_selected_items()
        if not selected:
            return
        BaseVideoListPanel._clipboard = [dict(item) for item in selected]
        BaseVideoListPanel._clipboard_is_cut = False
        BaseVideoListPanel._clipboard_source = self
        # Translators: Notification spoken by NVDA after copying item(s) to clipboard.
        ui.message(_("{count} item(s) copied.").format(count=len(selected)))

    def on_list_cut(self):
        """Ctrl+X — mark selected items for cut (removed on paste)."""
        selected = self._get_selected_items()
        if not selected:
            return
        BaseVideoListPanel._clipboard = [dict(item) for item in selected]
        BaseVideoListPanel._clipboard_is_cut = True
        BaseVideoListPanel._clipboard_source = self
        # Translators: Notification spoken by NVDA after cutting item(s) to clipboard.
        ui.message(_("{count} item(s) cut.").format(count=len(selected)))

    def on_list_paste(self):
        if not BaseVideoListPanel._clipboard:
            # Translators: Notification when the clipboard is empty and paste is attempted.
            ui.message(_("Clipboard is empty."))
            return

        is_same_list = BaseVideoListPanel._clipboard_source is self
        is_cut = BaseVideoListPanel._clipboard_is_cut
        clipboard_keys = [self._get_item_unique_key(i) for i in BaseVideoListPanel._clipboard]

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
                self.items.insert(adjusted_pos + offset, item)
            self._save_data()
            added_count = len(items_to_move)
            skipped = 0
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
                    # Translators: Confirmation dialog when pasting a single duplicate item across lists. {op} is Cut or Copy, {title} is the item title, {src} and {dst} are list names.
                    title = self._get_item_title_for_messages(duplicate_items[0])
                    confirm_msg = _(
                        "{op} '{title}' from {src} to {dst} — this item already exists. Replace it?"
                    ).format(op=op, title=title, src=source_name, dst=dest_name)
                else:
                    # Translators: Confirmation dialog when pasting multiple duplicate items across lists. {op} is Cut or Copy, {count} is number of duplicates, {src} and {dst} are list names.
                    confirm_msg = _(
                        "{op} from {src} to {dst} — {count} item(s) already exist. Replace all?"
                    ).format(op=op, count=dup_count, src=source_name, dst=dest_name)
                replace_duplicates = (
                # Translators: Title of the confirmation dialog when replacing duplicate items on paste.
                    wx.MessageBox(confirm_msg, _("Confirm Replace"),
                                  wx.YES_NO | wx.ICON_QUESTION, self) == wx.YES
                )

            added_count = 0
            replaced_count = 0
            skipped = 0
            for item in BaseVideoListPanel._clipboard:
                key = self._get_item_unique_key(item)
                if key in existing_keys:
                    if replace_duplicates:
                        for i, existing in enumerate(self.items):
                            if self._get_item_unique_key(existing) == key:
                                self.items[i] = dict(item)
                                break
                        replaced_count += 1
                    else:
                        skipped += 1
                else:
                    self.items.insert(insert_pos + added_count, dict(item))
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
            # Translators: Notification after successfully pasting one or more items with no duplicates skipped.
            msg = _("{count} item(s) pasted.").format(count=total_done)
        elif total_done > 0 and skipped > 0:
            # Translators: Notification after pasting where some duplicate items were skipped.
            msg = _("{done} item(s) pasted, {skipped} skipped.").format(
                done=total_done, skipped=skipped)
        else:
            # Translators: Notification when all items to be pasted already exist in the destination list.
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
        """Return a human-readable name for the given panel (used in dialogs).
        Subclasses can override this to return a translated tab name."""
        return getattr(panel, '_list_display_name', panel.__class__.__name__)

    def _get_focused_item(self, panel):
        """Return (item, view_index) of the currently focused item, or (None, -1)."""
        idx = panel.listCtrl.GetFirstSelected()
        if idx != -1 and idx < len(panel.filtered_items):
            return panel.filtered_items[idx], idx
        return None, -1

    def on_search(self, search_text):
        self._saved_search_text = search_text  
        search_text = search_text.lower()
        if search_text and self.last_selected_item_before_search is None:
            selected_index = self.listCtrl.GetFirstSelected()
            if selected_index != -1:
                self.last_selected_item_before_search = self.filtered_items[selected_index]
        if search_text:
            self.filtered_items = [
                item for item in self.items
                if any(search_text in field.lower() for field in self._get_search_fields(item))
            ]
        else:
            self.filtered_items = self.items[:]
        self._populate_list()
        if not search_text and self.last_selected_item_before_search:
            try:
                new_index = self.filtered_items.index(self.last_selected_item_before_search)
            except ValueError:
                new_index = 0
            self.last_selected_item_before_search = None
            self._focus_item(new_index)
        elif search_text and self.listCtrl.GetItemCount() > 0:
            self._focus_item(0)
        else:
            if self.listCtrl.GetItemCount() > 0:
                self._focus_item(0)

    def _focus_item(self, index):
        if self.listCtrl.GetItemCount() == 0:
            return
        index = min(index, self.listCtrl.GetItemCount() - 1)
        self._is_programmatic_focus = True
        self.listCtrl.SetItemState(-1, 0, wx.LIST_STATE_SELECTED | wx.LIST_STATE_FOCUSED)
        self.listCtrl.SetItemState(index,
            wx.LIST_STATE_SELECTED | wx.LIST_STATE_FOCUSED,
            wx.LIST_STATE_SELECTED | wx.LIST_STATE_FOCUSED)
        self.listCtrl.EnsureVisible(index)
        if index < len(self.filtered_items):
            self._last_selected_key = self._get_item_unique_key(self.filtered_items[index])
        self._is_programmatic_focus = False
        
    def on_list_item_selected(self, event):
        if getattr(self, '_is_programmatic_focus', False):
            event.Skip()
            return
        idx = self.listCtrl.GetFirstSelected()
        if idx != -1 and idx < len(self.filtered_items):
            self._last_selected_key = self._get_item_unique_key(self.filtered_items[idx])
        self._update_button_states()
        event.Skip()
    
    def get_selected_video_info(self):
        selected_index = self.listCtrl.GetFirstSelected()
        if selected_index == -1:
            return None
        return self.filtered_items[selected_index]

    def on_list_key_down(self, event):
        key_code = event.GetKeyCode()
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
        self.handle_video_list_keys(event)

    def on_close(self, event):
        if self.callback_topic:
            self.core.unregister_callback(self.callback_topic, self.refresh_data)
        self._save_data()
        
class FavVideoPanel(BaseVideoListPanel):
    def _get_file_path(self):
        return self.core.get_profile_path("fav_video.json")

    def _get_callback_topic(self):
        return "fav_video_updated"

    def _get_add_button_label(self):
        return _("Add &new favorite video from clipboard")

    def _add_worker(self):
        return self.core.add_item_to_favorites_worker
    
class WatchListPanel(BaseVideoListPanel):
    def _get_file_path(self):
        return self.core.get_profile_path("watch_list.json")

    def _get_callback_topic(self):
        return "watch_list_updated"

    def _get_add_button_label(self):
        return _("Add &new watch list from clipboard")

    def _add_worker(self):
        return self.core.add_to_watchlist_worker
    
class FavChannelPanel(wx.Panel):
    def __init__(self, parent, core_instance):
        wx.Panel.__init__(self, parent)
        self.core = core_instance
        self.channel = []
        self.filtered_channel = []
        self._is_first_load = True
        self.last_selected_item_before_search = None
        self._is_programmatic_selection = False
        self.fav_file_path = self.core.get_profile_path("fav_channel.json")

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
        self.openBtn = wx.Button(self, label=_("&Open"))
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
        self.on_search("")
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
            # Translators: Error message when the channel URL is missing.
            return ui.message(_("Error: Channel URL not found."))
        menu = wx.Menu()
        # Translators: Menu items for different types of channel content.
        menu_choices = {
        wx.ID_HIGHEST + 1: (_("Videos"), "/videos"),
        wx.ID_HIGHEST + 2: (_("Shorts"), "/shorts"),
        wx.ID_HIGHEST + 3: (_("Live"), "/streams"),
        }
        for menu_id, (label, suffix) in menu_choices.items(): menu.Append(menu_id, label)
        def on_menu_select(e):
            label, suffix = menu_choices.get(e.GetId())
            full_url = channel_url.rstrip('/') + suffix
                        # Translators: Status message when starting to fetch channel content. 
            # {type} is the content type (Videos, Shorts, Live) and {channel} is the channel name.
            title_template = _("Fetching {type} from {channel}...").format(channel=channel_name, type=label)
            #threading.Thread(target=self.core._view_channel_worker, args=(full_url, title_template, label), daemon=True).start()
            thread_kwargs = {
                'url': full_url, 'dialog_title_template': title_template, 'content_type_label': label,
                'base_channel_url': channel_url, 'base_channel_name': channel_name
            }
            threading.Thread(target=self.core._view_channel_worker, kwargs=thread_kwargs, daemon=True).start()
        menu.Bind(wx.EVT_MENU, on_menu_select)
        self.PopupMenu(menu)
        menu.Destroy()
        
    def on_list_key_down(self, event):
        if event.ControlDown():
            key_code = event.GetKeyCode()
            if key_code == ord('X'):
                self.on_list_cut()
                return
            elif key_code == ord('V'):
                self.on_list_paste()
                return
        key_code = event.GetKeyCode()
        if key_code == wx.WXK_RETURN or key_code == wx.WXK_SPACE:
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

class FavPlaylistPanel(wx.Panel):
    def __init__(self, parent, core_instance):
        wx.Panel.__init__(self, parent)
        self.core = core_instance
        self.playlists = []
        self.filtered_playlists = []
        self._is_first_load = True
        self.last_selected_item_before_search = None
        self.fav_file_path = self.core.get_profile_path("fav_playlist.json")

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
        self.openWebBtn = wx.Button(self, label=_("Open on &Web"))
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
        if event.ControlDown():
            key_code = event.GetKeyCode()
            if key_code == ord('X'):
                self.on_list_cut()
                return
            elif key_code == ord('V'):
                self.on_list_paste()
                return
        key_code = event.GetKeyCode()
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
        self.on_search("")
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
        searchLabel = wx.StaticText(panel, label=_("&Search:"))
        self.searchCtrl = wx.TextCtrl(panel, style=wx.TE_PROCESS_ENTER)
        searchSizer.Add(searchLabel, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 5)
        searchSizer.Add(self.searchCtrl, 1, wx.EXPAND)
        sizer.Add(searchSizer, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 10)

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
        wx.CallAfter(self.on_tab_changed, None)

    def on_search(self, event):
        search_text = self.searchCtrl.GetValue()
        current_page = self.notebook.GetCurrentPage()
        if not current_page:
            return
        current_page._saved_search_text = search_text
        if hasattr(current_page, 'on_search'):
            current_page.on_search(search_text)
        
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
        #if saved_search and hasattr(current_page, 'on_search'):
            #current_page.on_search(saved_search)
        if hasattr(current_page, 'listCtrl'):
            wx.CallAfter(current_page.listCtrl.SetFocus)
        if event:
            event.Skip()
        
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

class SearchDialog(BaseDialogMixin, wx.Dialog):
    """
    A simplified and robust search dialog.
    """
    def __init__(self, parent, core_instance):
        # Translators: Title of the dialog for searching YouTube.
        super().__init__(parent, title=_("Search YouTube"))
        self.core = core_instance

        panel = wx.Panel(self)
        mainSizer = wx.BoxSizer(wx.VERTICAL)
        sHelper = gui.guiHelper.BoxSizerHelper(self, sizer=mainSizer)
        # Translators: Label for the search query input field.
        sHelper.addItem(wx.StaticText(panel, label=_("&Search for:")))
        self.queryText = sHelper.addItem(wx.TextCtrl(panel, style=wx.TE_PROCESS_ENTER))
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
    def __init__(self, parent, title, video_list, core_instance, playlist_id_to_update=None, new_count_to_update=None):
        super().__init__(parent, title=title)
        self.videos = video_list
        self.core = core_instance
        self.playlist_id_to_update = playlist_id_to_update
        self.new_count_to_update = new_count_to_update
        panel = wx.Panel(self)
        mainSizer = wx.BoxSizer(wx.VERTICAL)
        self.listCtrl = wx.ListCtrl(panel, style=wx.LC_REPORT | wx.LC_SINGLE_SEL)
        # Translators: Column header for video title.
        self.listCtrl.InsertColumn(0, _("Title"), width=450)
        # Translators: Column header for video duration.
        self.listCtrl.InsertColumn(1, _("Duration"), width=120)
        mainSizer.Add(self.listCtrl, 1, wx.EXPAND | wx.ALL, 10)
        btnSizer = wx.BoxSizer(wx.HORIZONTAL)
        # Translators: Button to open the action menu for the selected video.
        self.actionBtn = wx.Button(panel, label=_("&Action..."))
        # Translators: Button to open the copy menu for the selected video info.
        self.copyBtn = wx.Button(panel, label=_("&Copy..."))
        # Translators: Button to close the dialog.
        self.closeBtn = wx.Button(panel, label=_("C&lose"))
        btnSizer.Add(self.actionBtn, 0, wx.RIGHT, 5)
        btnSizer.Add(self.copyBtn, 0, wx.RIGHT, 5)
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
        self.Bind(wx.EVT_CLOSE, self.on_close)
        self.Bind(wx.EVT_CHAR_HOOK, self.on_char_hook)
        self.actionBtn.Bind(wx.EVT_BUTTON, self.on_action_menu)
        self.copyBtn.Bind(wx.EVT_BUTTON, self.on_copy_menu)
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
            self.listCtrl.InsertItem(index, video.get('title', default_val))
            self.listCtrl.SetItem(index, 1, video.get('duration_str', ''))

    def on_list_key_down(self, event):
        key_code = event.GetKeyCode()
        if key_code in (wx.WXK_RETURN, wx.WXK_NUMPAD_ENTER, wx.WXK_SPACE):
            self.handle_video_list_keys(event)
            return
        event.Skip()
        
class ManageSubscriptionsDialog(BaseDialogMixin, wx.Dialog):
    """
    A comprehensive dialog to manage subscribed channels, their categories,
    and content types to fetch, with all fixes applied.
    """
    _instance = None 

    def __new__(cls, *args, **kwargs):  # <--- ✅ เพิ่มเมธอดนี้ทั้งหมด
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
        # Translators: Button to save subscription changes.
        self.saveBtn = wx.Button(panel, wx.ID_OK, label=_("&Save Changes"))
        # Translators: Button to close the dialog.
        self.closeBtn = wx.Button(panel, wx.ID_CANCEL, label=_("C&lose"))
        btnSizer.AddStretchSpacer()
        btnSizer.Add(self.saveBtn, 0, wx.RIGHT, 5)
        btnSizer.Add(self.closeBtn, 0)
        topSizer.Add(btnSizer, 0, wx.ALIGN_RIGHT | wx.ALL, 10)

        panel.SetSizer(topSizer)
        self.SetSize((800, 500))
        self.CentreOnScreen()
        self.core.register_callback("subscriptions_updated", self._on_subscriptions_updated)
        self.core.register_callback("subscription_added", self._on_subscription_added)
        self.core.register_callback("subscription_removed", self._on_subscription_removed)
        self._load_all_data()
        self._populate_category_filter()
        self._populate_channel_list()
        self.Bind(wx.EVT_CLOSE, self.on_close)
        self.Bind(wx.EVT_CHAR_HOOK, self.on_char_hook)
        self.saveBtn.Bind(wx.EVT_BUTTON, self.on_save)
        self.closeBtn.Bind(wx.EVT_BUTTON, lambda e: self.Close())
        self.categoryFilterCombo.Bind(wx.EVT_COMBOBOX, lambda e: self._populate_channel_list())
        self.channelListCtrl.Bind(wx.EVT_LIST_ITEM_SELECTED, self._update_right_panel)
        self.channelListCtrl.Bind(wx.EVT_LIST_ITEM_DESELECTED, self._update_right_panel)
        self.unsubBtn.Bind(wx.EVT_BUTTON, self.on_unsubscribe)
        self.viewContentBtn.Bind(wx.EVT_BUTTON, self.on_view_channel_content)
        self.addBtn.Bind(wx.EVT_BUTTON, self.on_add_subscription)

    def on_close(self, event):
        """Called when the dialog is closed."""
        self.core.unregister_callback("subscriptions_updated", self._on_subscriptions_updated)
        self.core.unregister_callback("subscription_added", self._on_subscription_added)
        self.core.unregister_callback("subscription_removed", self._on_subscription_removed)
        self.__class__._instance = None
        self.Destroy()

    def _on_subscription_added(self, new_channel_data):
        """Handles the targeted addition of a new channel to the list."""
        self.all_channels.append(new_channel_data)
        self.all_channels.sort(key=lambda x: x[1].lower())
        self._populate_channel_list()

    def _on_subscription_removed(self, data):
        """Handles the targeted removal of a channel from the list."""
        channel_url_to_remove = data.get("channel_url")
        if not channel_url_to_remove: return
        self.all_channels = [ch for ch in self.all_channels if ch[0] != channel_url_to_remove]
        self._populate_channel_list()
        
    def _on_subscriptions_updated(self):
        """Callback handler to refresh the dialog when data changes."""
        if not self.IsShown():
            return
        wx.CallAfter(self._load_all_data)
        wx.CallAfter(self._populate_category_filter)
        wx.CallAfter(self._populate_channel_list)
        
    def _load_all_data(self):
        """Loads all channels and categories from the database."""
        try:
            con = sqlite3.connect(self.db_path)
            cur = con.cursor()
            cur.execute("SELECT channel_url, channel_name FROM subscribed_channels ORDER BY channel_name COLLATE NOCASE")
            self.all_channels = cur.fetchall()
            cur.execute("SELECT id, name FROM categories ORDER BY position")
            self.categories = cur.fetchall()
            con.close()
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
        selected_channel_url = None
        selected_index = self.channelListCtrl.GetFirstSelected()
        if selected_index != -1:
            original_index = self.channelListCtrl.GetItemData(selected_index)
            if original_index < len(self.all_channels):
                selected_channel_url, __ = self.all_channels[original_index]
        self.channelListCtrl.DeleteAllItems()
        filter_selection = self.categoryFilterCombo.GetSelection()
        channels_to_show = []
        if filter_selection <= 0:
            channels_to_show = self.all_channels
        else:
            cat_id = self.categoryFilterCombo.GetClientData(filter_selection)
            try:
                con = sqlite3.connect(self.db_path)
                cur = con.cursor()
                cur.execute("""
                    SELECT sc.channel_url, sc.channel_name FROM subscribed_channels sc
                    JOIN channel_category_links ccl ON sc.channel_url = ccl.channel_url
                    WHERE ccl.category_id = ? ORDER BY sc.channel_name COLLATE NOCASE
                """, (cat_id,))
                channels_to_show = cur.fetchall()
                con.close()
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
            self.channelListCtrl.SetItemState(new_selection_index, wx.LIST_STATE_SELECTED | wx.LIST_STATE_FOCUSED, wx.LIST_STATE_SELECTED | wx.LIST_STATE_FOCUSED)
        if self.channelListCtrl.GetItemCount() > 0 and self.channelListCtrl.GetFirstSelected() == -1:
            self.channelListCtrl.SetItemState(0, wx.LIST_STATE_SELECTED | wx.LIST_STATE_FOCUSED, wx.LIST_STATE_SELECTED | wx.LIST_STATE_FOCUSED)
            self.channelListCtrl.EnsureVisible(0)
            event = wx.ListEvent(wx.wxEVT_LIST_ITEM_SELECTED, self.channelListCtrl.GetId())
            event.SetIndex(0)
            wx.PostEvent(self.channelListCtrl.GetEventHandler(), event)
        self._update_ui_state()
    
    def _update_ui_state(self):
        """Enable/disable controls based on whether any channels are subscribed."""
        has_any_channels = bool(self.all_channels)
        is_channel_selected = self.channelListCtrl.GetFirstSelected() != -1
        self.categoryFilterCombo.Enable(has_any_channels)
        self.channelListCtrl.Enable(has_any_channels)
        self.rightPanel.Show(has_any_channels)
        for ctrl in [self.categoryCheckList, self.contentTypesList, self.unsubBtn, self.saveBtn]:
            ctrl.Enable(is_channel_selected and has_any_channels)
        self.Layout()

    def _update_right_panel(self, event=None):
        self._update_ui_state()
        selected_index = self.channelListCtrl.GetFirstSelected()
        self.categoryCheckList.Clear()
        self.contentTypesList.CheckedItems = []
        if selected_index == -1: return
        original_index = self.channelListCtrl.GetItemData(selected_index)
        channel_url, __ = self.all_channels[original_index]
        try:
            con = sqlite3.connect(self.db_path)
            cur = con.cursor()
            cur.execute("SELECT category_id FROM channel_category_links WHERE channel_url = ?", (channel_url,))
            assigned_cat_ids = {row[0] for row in cur.fetchall()}
            cur.execute("SELECT content_types FROM subscribed_channels WHERE channel_url = ?", (channel_url,))
            content_types_str = cur.fetchone()[0]
            con.close()
            checked_cats = []
            self.categoryCheckList.Set([cat[1] for cat in self.categories])
            for index, (cat_id, name) in enumerate(self.categories):
                if cat_id in assigned_cat_ids:
                    checked_cats.append(index)
            self.categoryCheckList.CheckedItems = checked_cats
            internal_types = ["videos", "shorts", "streams"]
            saved_types = content_types_str.split(',')
            self.contentTypesList.CheckedItems = [i for i, t in enumerate(internal_types) if t in saved_types]
        except Exception as e:
            log.error("Failed to update channel details panel: %s", e)
            
    def on_save(self, event):
        selected_index = self.channelListCtrl.GetFirstSelected()
        if selected_index == -1:
            # Translators: Error message when no channel is selected to save.
            ui.message(_("No channel selected to save."))
            return
        original_index = self.channelListCtrl.GetItemData(selected_index)
        channel_url, __ = self.all_channels[original_index]
        try:
            con = sqlite3.connect(self.db_path)
            cur = con.cursor()
            cur.execute("DELETE FROM channel_category_links WHERE channel_url = ?", (channel_url,))
            assigned_cat_indices = self.categoryCheckList.CheckedItems
            for index in assigned_cat_indices:
                cat_id, __ = self.categories[index]
                cur.execute("INSERT INTO channel_category_links (channel_url, category_id) VALUES (?, ?)", (channel_url, cat_id))
            internal_types = ["videos", "shorts", "streams"]
            checked_types_indices = self.contentTypesList.CheckedItems
            types_to_save = [internal_types[i] for i in checked_types_indices]
            cur.execute("UPDATE subscribed_channels SET content_types = ? WHERE channel_url = ?", (",".join(types_to_save), channel_url))
            con.commit()
            con.close()
            self.core._notify_callbacks("subscriptions_updated")
            # Translators: Success message after saving changes.
            ui.message(_("Changes saved for the selected channel."))
        except Exception as e:
            log.error("Failed to save subscription changes: %s", e)
            # Translators: Error message shown when save fails.
            ui.message(_("Error saving changes."))

    def on_view_channel_content(self, event):
            """Shows a submenu to view different content types for the selected channel."""
            selected_index = self.channelListCtrl.GetFirstSelected()
            if selected_index == -1: return
            original_index = self.channelListCtrl.GetItemData(selected_index)
            channel_url, channel_name = self.all_channels[original_index]
            if not channel_url:
                # Translators: Error message when channel URL is missing.
                ui.message(_("Error: Channel URL not found."))
                return
            menu = wx.Menu()
            # Translators: Submenu items to fetch specific content types.
            menu_choices = {
                wx.ID_HIGHEST + 1: (_("Videos"), "/videos"),
                wx.ID_HIGHEST + 2: (_("Shorts"), "/shorts"),
                wx.ID_HIGHEST + 3: (_("Live"), "/streams"),
            }
            for menu_id, (label, suffix) in menu_choices.items():
                menu.Append(menu_id, label)
            
            def on_menu_select(e):
                label, suffix = menu_choices.get(e.GetId())
                full_url = channel_url.rstrip('/') + suffix
                # Translators: Progress template for fetching channel content. {type} is "Videos"/"Live", {channel} is the name.
                template = _("Fetching {type} from {channel}...")   
                title_text = template.format(channel=channel_name, type=label)
                thread_kwargs = {
                    'url': full_url,
                    'dialog_title_template': title_text,
                    'content_type_label': label,
                    'base_channel_url': channel_url,
                    'base_channel_name': channel_name
                }
                threading.Thread(target=self.core._view_channel_worker, kwargs=thread_kwargs, daemon=True).start()
            menu.Bind(wx.EVT_MENU, on_menu_select)
            self.PopupMenu(menu)
            menu.Destroy()
            
    def on_add_subscription(self, event):
        """Handles adding a new subscription from a URL in the clipboard."""
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
        if selected_index == -1: return
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

    def _on_subscriptions_updated(self):
        """Handles the callback when subscription data changes."""
        if self.progress_dialog:
            self.progress_dialog.Update(self.progress_dialog.GetRange())
            self.progress_dialog = None
        currentPage = self.notebook.GetCurrentPage()
        last_tab_id = currentPage.tab_id if currentPage else "all"
        self._build_all_tabs(select_tab_id=last_tab_id)

    def _build_all_tabs(self, select_tab_id=None):
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
            page = self._create_tab_panel(tab_info['id'])
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

    def _create_tab_panel(self, tab_id):
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
        self._populate_list_for_panel(panel)
        return panel

    def _populate_list_for_panel(self, panel):
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
            if self.pending_focus_info and self.pending_focus_info['tab_id'] == panel.tab_id:
                saved_index = self.pending_focus_info['index']
                focus_index = min(saved_index, item_count - 1)
                self.pending_focus_info = None
            panel.listCtrl.SetItemState(focus_index, wx.LIST_STATE_SELECTED | wx.LIST_STATE_FOCUSED, wx.LIST_STATE_SELECTED | wx.LIST_STATE_FOCUSED)
            panel.listCtrl.EnsureVisible(focus_index)
        self._update_tab_button_states(panel)

    def _update_tab_button_states(self, panel):
        has_items = panel.listCtrl.GetItemCount() > 0
        panel.actionBtn.Enable(has_items)
        panel.copyBtn.Enable(has_items)
        panel.markSeenBtn.Enable(has_items)

    def get_selected_video_info(self):
        currentPage = self.notebook.GetCurrentPage()
        if not currentPage: return None
        listCtrl = currentPage.listCtrl
        selected_index = listCtrl.GetFirstSelected()
        if selected_index == -1: return None
        return currentPage.videos[selected_index]

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
        self.pending_focus_info = {'tab_id': currentPage.tab_id, 'index': selected_index}
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
        self.base_data_path = os.path.join(globalVars.appArgs.configPath, "youtubePlus")
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