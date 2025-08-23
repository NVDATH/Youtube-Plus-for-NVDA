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

# Initialize translations for this file
addonHandler.initTranslation()

def copy_to_clipboard(text):
    api.copyToClip(text)

confspec = {
    "autoSpeak": "boolean(default=True)",
    "sortOrder": "string(default='newest')",
    "playlist_fetch_count": "integer(default=20, min=5, max=100)",
    "contentTypesToFetch": "string_list(default=list('videos', 'shorts', 'streams'))",
    "autoUpdateIntervalMinutes": "integer(default=0)",
    "refreshInteval": "integer(default=5, min=1, max=60)",
    "messageLimit": "integer(default=5000, min=100, max=20000)",
    "exportPath": "string()",
    "cookieMode": "string(default='auto')",
    "subDialogViewMode": "string(default='unseen')",
    "progressIndicatorMode": "string(default='beep')",
    "searchResultCount": "integer(default=20, min=5, max=50)"
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
    
class BaseInfoDialog(BaseDialogMixin, wx.Dialog): # << CHANGE HERE
    """A base dialog for showing read-only text content."""
    def __init__(self, parent, title, text_content):
        super().__init__(parent, title=title)
        panel = wx.Panel(self)
        mainSizer = wx.BoxSizer(wx.VERTICAL)
        textCtrl = wx.TextCtrl(panel, value=text_content, style=wx.TE_MULTILINE | wx.TE_READONLY)
        mainSizer.Add(textCtrl, 1, wx.EXPAND | wx.ALL, 10)
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
    def __init__(self, parent, title, help_text):
        super(HelpDialog, self).__init__(parent, title, help_text)

class InfoDialog(BaseInfoDialog):
    """Dialog to show video info, inherits from BaseInfoDialog."""
    def __init__(self, parent, title, info_text):
        super(InfoDialog, self).__init__(parent, title, info_text)

class MessagesListCtrl(wx.ListCtrl, listmix.ListCtrlAutoWidthMixin):
    def __init__(self, parent):
        wx.ListCtrl.__init__(self, parent, style=wx.LC_REPORT | wx.LC_SINGLE_SEL | wx.BORDER_SUNKEN)
        listmix.ListCtrlAutoWidthMixin.__init__(self)
        self.InsertColumn(0, _("Author"), width=200)
        self.InsertColumn(1, _("Message"), width=350)
        self.InsertColumn(2, _("Time"), width=150)

class CommentsListCtrl(wx.ListCtrl, listmix.ListCtrlAutoWidthMixin):
    def __init__(self, parent):
        wx.ListCtrl.__init__(self, parent, style=wx.LC_REPORT | wx.LC_SINGLE_SEL | wx.BORDER_SUNKEN)
        listmix.ListCtrlAutoWidthMixin.__init__(self)
        self.InsertColumn(0, _("Author"), width=200)
        self.InsertColumn(1, _("Message"), width=350)
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
        searchLabel = wx.StaticText(panel, label=_("&Search:"))
        self.searchTextCtrl = wx.TextCtrl(panel, style=wx.TE_PROCESS_ENTER)
        searchSizer.Add(searchLabel, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 5)
        searchSizer.Add(self.searchTextCtrl, 1, wx.EXPAND)
        mainSizer.Add(searchSizer, 0, wx.EXPAND | wx.ALL, 5)

        self.listCtrl = wx.ListCtrl(panel, style=wx.LC_REPORT | wx.LC_SINGLE_SEL)
        self.listCtrl.InsertColumn(0, _("Title"), width=500)
        self.listCtrl.InsertColumn(1, _("Time"), width=100)
        mainSizer.Add(self.listCtrl, 1, wx.EXPAND | wx.ALL, 10)
        
        self.currentTextElement = wx.TextCtrl(panel, style=wx.TE_MULTILINE | wx.TE_READONLY)
        mainSizer.Add(self.currentTextElement, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 10)

        btnSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.openBtn = wx.Button(panel, label=_("&Open Chapter"))
        self.copyTitleBtn = wx.Button(panel, label=_("&Copy Title"))
        self.copyUrlBtn = wx.Button(panel, label=_("Copy &URL"))
        self.exportBtn = wx.Button(panel, label=_("&Export"))
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
            self.currentTextElement.SetValue(f"{time_str} - {title_str}")
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
                ui.message(_("Opening in browser..."))
                webbrowser.open(timestamp_url)
            except Exception as e:
                # Topic 2: Add logging for better debugging
                log.warning("Failed to open URL in browser.", exc_info=True)
                ui.message(f"Error opening browser: {e}")

    def on_copy_text(self, event):
        selected_index = self.listCtrl.GetFirstSelected()
        if selected_index != -1:
            title_str = self.listCtrl.GetItemText(selected_index, 0)
            time_str = self.listCtrl.GetItemText(selected_index, 1)
            full_text = f"{time_str} - {title_str}"
            copy_to_clipboard(full_text)
            ui.message(_("Copied timestamp: ") + full_text)

    def on_copy_url(self, event):
        selected_index = self.listCtrl.GetFirstSelected()
        if selected_index != -1:
            seconds = self.listCtrl.GetItemData(selected_index)
            timestamp_url = f"{self.base_video_url}&t={seconds}s"
            copy_to_clipboard(timestamp_url)
            ui.message(_("Copied URL: ") + timestamp_url)
    
    def on_export(self, event):
        default_path = config.conf["YoutubePlus"].get("exportPath", "") or os.path.expanduser("~/Desktop")
        safeTitle = sanitize_filename(f"Chapters for {self.GetTitle()}")
        filename = f"{safeTitle}.txt"
        filepath = os.path.join(default_path, filename)
        log.info("Exporting chapters for '%s' to %s", self.GetTitle(), filepath)
        try:
            with open(filepath, "w", encoding="utf-8") as f:
                for chapter in self.chapters:
                    start_seconds = int(chapter.get('start_time', 0))
                    minutes, seconds = divmod(start_seconds, 60)
                    hours, minutes = divmod(minutes, 60)
                    time_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
                    title_str = chapter.get('title', '')
                    f.write(f"{time_str} - {title_str}\n")
            ui.message(_("Export complete"))
        except (IOError, OSError) as e:
            # Topic 2: More specific exception handling and logging
            log.error("Failed to export chapters due to an OS/IO error.", exc_info=True)
            ui.message(_("Error exporting file: ") + str(e))
        except Exception as e:
            log.exception("An unexpected error occurred during chapter export.")
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
        self.copyBtn = wx.Button(panel, label="&Copy")
        self.exportBtn = wx.Button(panel, label="&Export")
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
        if selected_index != -1:
            self.last_selected_obj = self.filteredMessages[selected_index]
        
        item_count_before = self.messagesListBox.GetItemCount()
        is_at_bottom = (selected_index == item_count_before - 1)

        self.messagesListBox.Freeze()
        try:
            # This logic is complex but efficient for updating the list view.
            # It works on the local copy `self.filteredMessages`.
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
        
        if searchText:
            self.filteredMessages = [
                m for m in self.messages
                if searchText in m.get('author', '').lower() or searchText in m.get('message', '').lower()
            ]
        else:
            self.filteredMessages = self.messages[:]
        
        self.updateList()

    def onCopy(self, event):
        selected = self.messagesListBox.GetFirstSelected()
        if selected != -1:
            msg_obj = self.filteredMessages[selected]
            full_text = f"{msg_obj.get('author')}: {msg_obj.get('message')}"
            copy_to_clipboard(full_text)
            ui.message(_("message copied"))
        else:
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
                    time_str = msg_obj.get('datetime', '')
                    author = msg_obj.get('author', '')
                    message = msg_obj.get('message', '')
                    f.write(f"[{time_str}] {author}: {message}\n")
            ui.message(_("Export message complete"))
        except (IOError, OSError) as e:
            log.error("Failed to export chat messages due to an OS/IO error.", exc_info=True)
            ui.message(_("Error exporting file: ") + str(e))
        except Exception:
            log.exception("An unexpected error occurred during chat export.")
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
        searchLabel = wx.StaticText(self.panel, label=_("&Search:"))
        self.searchTextCtrl = wx.TextCtrl(self.panel, style=wx.TE_PROCESS_ENTER)
        searchSizer.Add(searchLabel, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 5)
        searchSizer.Add(self.searchTextCtrl, 1, wx.EXPAND)
        mainSizer.Add(searchSizer, 0, wx.EXPAND | wx.ALL, 5)

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
        self.copyBtn = wx.Button(self.panel, label=_("&Copy"))
        self.exportBtn = wx.Button(self.panel, label="&Export")
        self.totalAmountTextCtrl = wx.TextCtrl(self.panel, style=wx.TE_READONLY | wx.TE_MULTILINE | wx.TE_LEFT) 
        self.totalAmountTextCtrl.SetMinSize((150, -1)) 
        bottomBtnSizer.Add(self.totalAmountTextCtrl, 1, wx.EXPAND | wx.RIGHT, 5)

        bottomBtnSizer.Add(self.copyBtn, 0, wx.RIGHT, 5)
        bottomBtnSizer.Add(self.exportBtn, 0, wx.RIGHT, 5)
        
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
            ui.message(_("Copied"))
        else: ui.message(_("Nothing selected"))

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
            ui.message(_("Export complete"))
        except (IOError, OSError) as e:
            # Topic 2: Better exception handling
            log.error("Failed to export comments due to an OS/IO error.", exc_info=True)
            ui.message(_("Error exporting file: ") + str(e))
        except Exception:
            log.exception("An unexpected error occurred during comments export.")
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

    def onClose(self, event): self.Destroy()

class VideoActionMixin:
    """A mixin to provide a standardized 'Action' menu for any video list dialog."""
    
    def on_open_video(self, event):
        """Handles opening the selected video in a web browser."""
        video = self.get_selected_video_info()
        video_id = video.get('id') or video.get('video_id')
        if not video_id: 
            ui.message(_("Video ID not found."))
            return
        
        url = f"https://www.youtube.com/watch?v={video_id}"
        ui.message(_("Opening in browser..."))
        try:
            webbrowser.open(url)
        except Exception as e:
            log.warning("Failed to open URL in browser.", exc_info=True)
            ui.message(f"Error opening browser: {e}")

    def create_video_action_menu(self):
        """Creates and returns a wx.Menu with common video actions."""
        menu = wx.Menu()
        
        ID_VIEW_INFO = wx.NewIdRef()
        ID_VIEW_COMMENTS = wx.NewIdRef()
        ID_SHOW_CHAPTERS = wx.NewIdRef() 
        ID_DOWNLOAD_VID = wx.NewIdRef()
        ID_DOWNLOAD_AUD = wx.NewIdRef()
        ID_OPEN_VID_WEB = wx.NewIdRef()
        ID_ADD_FAV_VID = wx.NewIdRef()
        ID_ADD_FAV_CHAN = wx.NewIdRef()
        ID_OPEN_CHAN_WEB = wx.NewIdRef()
        ID_SHOW_VIDS = wx.NewIdRef()
        ID_SHOW_SHORTS = wx.NewIdRef()
        ID_SHOW_LIVE = wx.NewIdRef()
        
        menu.Append(ID_VIEW_INFO, _("View Video &Info..."))
        menu.Append(ID_VIEW_COMMENTS, _("View &Comments / Replay..."))
        menu.Append(ID_SHOW_CHAPTERS, _("View Chap&ters/Timestamps...")) 
        menu.AppendSeparator()
        menu.Append(ID_DOWNLOAD_VID, _("&Download Video"))
        menu.Append(ID_DOWNLOAD_AUD, _("Download &Audio"))
        menu.AppendSeparator()
        menu.Append(ID_ADD_FAV_VID, _("Add to &Favorite Videos"))
        menu.Append(ID_ADD_FAV_CHAN, _("Add to &Favorite Channels"))
        menu.AppendSeparator()
        menu.Append(ID_OPEN_VID_WEB, _("Open video in &browser"))
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
        menu.Bind(wx.EVT_MENU, self.on_open_video, id=ID_OPEN_VID_WEB)
        menu.Bind(wx.EVT_MENU, self.on_add_to_fav_video, id=ID_ADD_FAV_VID)
        menu.Bind(wx.EVT_MENU, self.on_add_to_fav_channel, id=ID_ADD_FAV_CHAN)
        
        menu.Bind(wx.EVT_MENU, self.on_open_channel, id=ID_OPEN_CHAN_WEB)
        menu.Bind(wx.EVT_MENU, lambda e: self._view_channel_content('videos'), id=ID_SHOW_VIDS)
        menu.Bind(wx.EVT_MENU, lambda e: self._view_channel_content('shorts'), id=ID_SHOW_SHORTS)
        menu.Bind(wx.EVT_MENU, lambda e: self._view_channel_content('streams'), id=ID_SHOW_LIVE)
        
        return menu
        
    def on_show_chapters(self, event):
        """Handles showing the chapters/timestamps dialog for the selected video."""
        video = self.get_selected_video_info()
        if not video: return
        video_id = video.get('id') or video.get('video_id')
        if not video_id: return ui.message(_("Video ID not found."))
        
        url = f"https://youtube.com/watch?v={video_id}"
        ui.message(_("Getting chapters..."))
        threading.Thread(target=self.core._show_chapters_worker, args=(url, ), daemon=True).start()
        
    def on_add_to_fav_video(self, event):
        video = self.get_selected_video_info()
        video_id = video.get('id') or video.get('video_id')
        if not video_id:
            ui.message(_("Could not get video ID to add to favorites."))
            return
        url = f"https://www.youtube.com/watch?v={video_id}"
        threading.Thread(target=self.core.add_item_to_favorites_worker, args=(url,), daemon=True).start()

    def on_add_to_fav_channel(self, event):
        video = self.get_selected_video_info()
        video_id = video.get('id') or video.get('video_id')
        if not video_id:
            ui.message(_("Could not get video ID to find the channel."))
            return
        url = f"https://www.youtube.com/watch?v={video_id}"
        threading.Thread(target=self.core.add_channel_to_favorites_worker, args=(url,), daemon=True).start()
    
    def on_view_info(self, event):
        video = self.get_selected_video_info()
        if not video: return
        video_id = video.get('id') or video.get('video_id')
        if not video_id: return ui.message(_("Video ID not found."))
        url = f"https://youtube.com/watch?v={video_id}"
        threading.Thread(target=self.core._get_info_worker, args=(url,), daemon=True).start()

    def on_view_comments(self, event):
        video = self.get_selected_video_info()
        if not video: return
        video_id = video.get('id') or video.get('video_id')
        if not video_id: return ui.message(_("Video ID not found."))
        url = f"https://youtube.com/watch?v={video_id}"
        ui.message(_("Getting data for '{title}'...").format(title=video.get('title')))
        self.core.get_data_for_url(url)

    def on_download_video(self, event):
        video = self.get_selected_video_info()
        if not video: return
        video_id = video.get('id') or video.get('video_id')
        if not video_id: return ui.message(_("Video ID not found."))
        url = f"https://youtube.com/watch?v={video_id}"
        threading.Thread(target=self.core._direct_download_worker, args=(url, 'video'), daemon=True).start()

    def on_download_audio(self, event):
        video = self.get_selected_video_info()
        if not video: return
        video_id = video.get('id') or video.get('video_id')
        if not video_id: return ui.message(_("Video ID not found."))
        
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
                text_to_copy = (
                    f"Title: {video.get('title', '')}\n"
                    f"Channel: {video.get('channel_name', '')}\n"
                    f"URL: https://youtu.be/{video_id}"
                )
            
            if text_to_copy:
                api.copyToClip(text_to_copy)
                ui.message(_("Copied"))
                
    def _view_channel_content(self, content_type):
        pass

class FavVideoPanel(wx.Panel, VideoActionMixin):
    def __init__(self, parent, core_instance):
        wx.Panel.__init__(self, parent)
        self.core = core_instance
        self.favorites = []
        self.filtered_favorites = []
        self._is_first_load = True
        self.last_selected_item_before_search = None
        self.fav_file_path = self._get_fav_file_path()

        mainSizer = wx.BoxSizer(wx.VERTICAL)

        self.listCtrl = wx.ListCtrl(self, style=wx.LC_REPORT | wx.LC_SINGLE_SEL)
        self._create_list_columns(self.listCtrl)
        mainSizer.Add(self.listCtrl, 1, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 10)

        btnSizer = wx.BoxSizer(wx.HORIZONTAL)
        self._create_extra_buttons(self, btnSizer)
        btnSizer.AddStretchSpacer()
        self.addBtn = wx.Button(self, label=self._get_add_button_label())
        self.removeBtn = wx.Button(self, label=_("&Remove"))
        btnSizer.Add(self.addBtn, 0, wx.RIGHT, 5)
        btnSizer.Add(self.removeBtn, 0, wx.RIGHT, 5)
        mainSizer.Add(btnSizer, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 10)

        self.SetSizer(mainSizer)

        self.core.register_callback("fav_video_updated", self.refresh_favVideo)

        self._load_favorites()
        self._populate_list()  
        self._update_button_states()

        self.addBtn.Bind(wx.EVT_BUTTON, self.on_add)
        self.removeBtn.Bind(wx.EVT_BUTTON, self.on_remove)
        self.listCtrl.Bind(wx.EVT_KEY_DOWN, self.on_list_key_down)

    def on_close(self, event):
        self.core.unregister_callback("fav_video_updated", self.refresh_favVideo)
        self._save_favorites()

    def _create_extra_buttons(self, panel, sizer):
            self.actionBtn = wx.Button(panel, label=_("&Action..."))
            self.copyBtn = wx.Button(panel, label=_("&Copy..."))
            sizer.Add(self.actionBtn, 0, wx.RIGHT, 5)
            sizer.Add(self.copyBtn, 0, wx.RIGHT, 5)
            
            self.actionBtn.Bind(wx.EVT_BUTTON, self.on_action_menu)
            self.copyBtn.Bind(wx.EVT_BUTTON, self.on_copy_menu)
            
    def on_action_menu(self, event):
        if self.listCtrl.GetFirstSelected() == -1: return
        menu = self.create_video_action_menu()
        self.PopupMenu(menu)
        menu.Destroy()

    def on_copy_menu(self, event):
            if self.listCtrl.GetFirstSelected() == -1: return
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

    def get_selected_video_info(self):
        selected_index = self.listCtrl.GetFirstSelected()
        if selected_index == -1: return None
        return self.filtered_favorites[selected_index]

    def _view_channel_content(self, content_type):
        selected_index = self.listCtrl.GetFirstSelected()
        if selected_index == -1: return
        item = self.filtered_favorites[selected_index]
        channel_url = item.get("channel_url")
        channel_name = item.get("channel_name")
        if not channel_url:
            ui.message(_("Error: Channel URL not found for this item."))
            return
        suffix_map = {"videos": "/videos", "shorts": "/shorts", "streams": "/streams"}
        label_map = {"videos": _("Videos"), "shorts": _("Shorts"), "streams": _("Live")}
        suffix = suffix_map.get(content_type, "/videos")
        label = label_map.get(content_type, _("Content"))
        full_url = channel_url.rstrip('/') + suffix
        title_template = _("Fetching {type} from {channel}...").format(channel=channel_name, type=label)
        thread_kwargs = {
            'url': full_url, 'dialog_title_template': title_template, 'content_type_label': label,
            'base_channel_url': channel_url, 'base_channel_name': channel_name
        }
        threading.Thread(target=self.core._view_channel_worker, kwargs=thread_kwargs, daemon=True).start()
        
    def _get_fav_file_path(self): return os.path.join(os.path.dirname(__file__), 'fav_video.json')
    def _get_add_button_label(self): return _("Add &new favorite video  from clipboard")
    
    def _create_list_columns(self, list_ctrl):
        list_ctrl.InsertColumn(0, _("Title"), width=350)
        list_ctrl.InsertColumn(1, _("Channel"), width=200)
        list_ctrl.InsertColumn(2, _("Duration"), width=120)
        
    def _get_search_fields(self, item): return [item.get('title', ''), item.get('channel_name', '')]
    
    def _get_item_title_for_messages(self, item): return item.get('title', 'N/A')
    
    def _update_button_states(self):
        is_not_empty = bool(self.favorites)
        self.removeBtn.Enable(is_not_empty)
        self.actionBtn.Enable(is_not_empty and self.listCtrl.GetFirstSelected() != -1)
        self.copyBtn.Enable(is_not_empty and self.listCtrl.GetFirstSelected() != -1)

    def _load_favorites(self):
        with self.core._fav_file_lock:
            try:
                with open(self.fav_file_path, 'r', encoding='utf-8') as f:
                    self.favorites = json.load(f)
            except (FileNotFoundError, json.JSONDecodeError, TypeError):
                self.favorites = []
        self.filtered_favorites = self.favorites[:]

    def _save_favorites(self):
        with self.core._fav_file_lock:
            try:
                with open(self.fav_file_path, 'w', encoding='utf-8') as f:
                    json.dump(self.favorites, f, indent=2, ensure_ascii=False)
            except (IOError, OSError):
                ui.message(_("Error: Could not save favorites list."))

    def on_add(self, event):
        """Delegates the add action to the core worker."""
        try:
            url = api.getClipData()
            if not url or not self.core.is_youtube_url(url):
                ui.message(_("No valid YouTube URL found in clipboard."))
                return
        except Exception:
            ui.message(_("Could not read from clipboard."))
            return
        threading.Thread(target=self.core.add_item_to_favorites_worker, args=(url,), daemon=True).start()
        
    def on_remove(self, event):
        selected_index = self.listCtrl.GetFirstSelected()
        if selected_index == -1: return
        item_to_remove = self.filtered_favorites[selected_index]
        title = self._get_item_title_for_messages(item_to_remove)
        if wx.MessageBox(_("Are you sure you want to remove '{title}'?").format(title=title), _("Confirm Removal"), wx.YES_NO | wx.ICON_QUESTION, self) != wx.YES:
            return
        self.favorites.remove(item_to_remove)
        self._save_favorites()
        self.on_search("")
        item_count = self.listCtrl.GetItemCount()
        if item_count > 0:
            new_selection = min(selected_index, item_count - 1)
            self.listCtrl.SetItemState(new_selection, wx.LIST_STATE_SELECTED | wx.LIST_STATE_FOCUSED, wx.LIST_STATE_SELECTED | wx.LIST_STATE_FOCUSED)
            self.listCtrl.EnsureVisible(new_selection)
        self._update_button_states()
        wx.CallAfter(self.listCtrl.SetFocus)
        self.core._notify_delete(_("Item removed."))

    def on_search(self, search_text):
        search_text = search_text.lower()

        if search_text and self.last_selected_item_before_search is None:
            selected_index = self.listCtrl.GetFirstSelected()
            if selected_index != -1:
                self.last_selected_item_before_search = self.filtered_favorites[selected_index]

        if search_text:
            self.filtered_favorites = [
                item for item in self.favorites
                if any(search_text in field.lower() for field in self._get_search_fields(item))
            ]
        else:
            self.filtered_favorites = self.favorites[:]

        self._populate_list()

        if not search_text and self.last_selected_item_before_search:
            try:
                new_index = self.filtered_favorites.index(self.last_selected_item_before_search)
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
            for index, item in enumerate(self.filtered_favorites):
                self.listCtrl.InsertItem(index, item.get('title', 'N/A'))
                self.listCtrl.SetItem(index, 1, item.get('channel_name', 'N/A'))
                self.listCtrl.SetItem(index, 2, item.get('duration_str', ''))
            
            if self._is_first_load and self.listCtrl.GetItemCount() > 0:
                self.listCtrl.SetItemState(0, wx.LIST_STATE_SELECTED | wx.LIST_STATE_FOCUSED, wx.LIST_STATE_SELECTED | wx.LIST_STATE_FOCUSED)
                self._is_first_load = False
        finally:
            self.listCtrl.Thaw()
            
    def on_list_key_down(self, event):
        if event.ShiftDown():
            key_code = event.GetKeyCode()
            if key_code == wx.WXK_UP:
                self.move_item(-1)
            elif key_code == wx.WXK_DOWN:
                self.move_item(1)
            else:
                event.Skip()
            return

        key_code = event.GetKeyCode()
        if key_code == wx.WXK_RETURN or key_code == wx.WXK_SPACE:
            self.on_open_video(event)
        elif key_code == wx.WXK_DELETE:
            self.on_remove(event)
        else:
            event.Skip()

    def move_item(self, direction):
        selected_index = self.listCtrl.GetFirstSelected()
        if selected_index == -1: return
        if (direction == -1 and selected_index == 0) or \
           (direction == 1 and selected_index == len(self.filtered_favorites) - 1):
            return

        item_to_move = self.filtered_favorites[selected_index]
        original_master_index = self.favorites.index(item_to_move)

        self.favorites.pop(original_master_index)
        new_master_index = original_master_index + direction
        self.favorites.insert(new_master_index, item_to_move)
        self._save_favorites()
        self.on_search("")
        
        try:
            new_view_index = self.filtered_favorites.index(item_to_move)
            self.listCtrl.SetItemState(new_view_index, wx.LIST_STATE_SELECTED | wx.LIST_STATE_FOCUSED, wx.LIST_STATE_SELECTED | wx.LIST_STATE_FOCUSED)
            self.listCtrl.EnsureVisible(new_view_index)
        except ValueError: pass
        self._update_button_states()

    def refresh_favVideo(self, data=None):
        if not self.listCtrl:
            return
        self._load_favorites()
        self.on_search("")

        if data and data.get("action") == "add":
            item_count = self.listCtrl.GetItemCount()
            if item_count > 0:
                last_index = item_count - 1
                self.listCtrl.SetItemState(last_index, wx.LIST_STATE_SELECTED | wx.LIST_STATE_FOCUSED, wx.LIST_STATE_SELECTED | wx.LIST_STATE_FOCUSED)
                self.listCtrl.EnsureVisible(last_index)
        self._update_button_states()

class FavChannelPanel(wx.Panel):
    def __init__(self, parent, core_instance):
        wx.Panel.__init__(self, parent)
        self.core = core_instance
        self.channel = []
        self.filtered_channel = []
        self._is_first_load = True
        self.last_selected_item_before_search = None
        self._is_programmatic_selection = False
        self.fav_file_path = os.path.join(os.path.dirname(__file__), 'fav_channel.json')

        mainSizer = wx.BoxSizer(wx.VERTICAL)

        self.listCtrl = wx.ListCtrl(self, style=wx.LC_REPORT | wx.LC_SINGLE_SEL)
        self.listCtrl.InsertColumn(0, _("Channel"), width=450)
        self.listCtrl.InsertColumn(1, _("Subscribers"), width=150)
        mainSizer.Add(self.listCtrl, 1, wx.EXPAND | wx.ALL, 5)

        self.descriptionBox = wx.StaticBoxSizer(wx.VERTICAL, self, label=_("Channel Description"))
        self.descriptionText = wx.TextCtrl(self, style=wx.TE_MULTILINE | wx.TE_READONLY)
        self.descriptionBox.Add(self.descriptionText, 1, wx.EXPAND | wx.ALL, 5)
        mainSizer.Add(self.descriptionBox, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 5)

        btnSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.openBtn = wx.Button(self, label=_("&Open"))
        self.viewContentBtn = wx.Button(self, label=_("View &channel Content..."))
        self.addBtn = wx.Button(self, label=_("Add &new favorite channel from clipboard"))
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
                ui.message(_("No valid YouTube URL found in clipboard."))
                return
        except:
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
        selected_index = self.listCtrl.GetFirstSelected()
        if selected_index == -1:
            return
            
        item_to_remove = self.filtered_channel[selected_index]
        
        channel_name = item_to_remove.get('channel_name', 'this channel') # ใช้ 'this channel' เป็นค่าสำรอง
        
        confirm_message = _("Are you sure you want to remove '{name}'?").format(name=channel_name)
        if wx.MessageBox(confirm_message, _("Confirm Removal"), wx.YES_NO | wx.ICON_QUESTION) != wx.YES:
            return
            
        self.channel.remove(item_to_remove)
        self._save_channel()
        self.on_search("")

        item_count = self.listCtrl.GetItemCount()
        if item_count > 0:
            new_selection = min(selected_index, item_count - 1)
            self._is_programmatic_selection = True
            self.listCtrl.SetItemState(new_selection, wx.LIST_STATE_SELECTED | wx.LIST_STATE_FOCUSED, wx.LIST_STATE_SELECTED | wx.LIST_STATE_FOCUSED)
            self._is_programmatic_selection = False
            self.listCtrl.EnsureVisible(new_selection)

        self._update_button_states()
        wx.CallAfter(self.listCtrl.SetFocus)
        self.core._notify_delete(_("Channel removed."))
        
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
        if not channel_url: return ui.message(_("Error: Channel URL not found."))
        
        menu = wx.Menu()
        menu_choices = { wx.ID_HIGHEST + 1: (_("Videos"), "/videos"), wx.ID_HIGHEST + 2: (_("Shorts"), "/shorts"), wx.ID_HIGHEST + 3: (_("Live"), "/streams"), }
        for menu_id, (label, suffix) in menu_choices.items(): menu.Append(menu_id, label)
        def on_menu_select(e):
            label, suffix = menu_choices.get(e.GetId())
            full_url = channel_url.rstrip('/') + suffix
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
        if event.ShiftDown():
            key_code = event.GetKeyCode()
            if key_code == wx.WXK_UP:
                self.move_item(-1)
            elif key_code == wx.WXK_DOWN:
                self.move_item(1)
            else:
                event.Skip()
            return

        key_code = event.GetKeyCode()
        if key_code == wx.WXK_RETURN or key_code == wx.WXK_SPACE: self.on_open(event)
        elif key_code == wx.WXK_DELETE: self.on_remove(event)
        else: event.Skip()

    def move_item(self, direction):
        selected_index_view = self.listCtrl.GetFirstSelected()
        if selected_index_view == -1: return
        if direction == -1 and selected_index_view == 0: return
        if direction == 1 and selected_index_view == self.listCtrl.GetItemCount() - 1: return

        item_to_move = self.filtered_channel[selected_index_view]
        original_master_index = self.channel.index(item_to_move)

        self.channel.pop(original_master_index)
        new_master_index = original_master_index + direction
        self.channel.insert(new_master_index, item_to_move)
        
        self._save_channel()
        self.on_search("")
        
        try:
            new_view_index = self.filtered_channel.index(item_to_move)
            self.listCtrl.SetItemState(new_view_index, wx.LIST_STATE_SELECTED | wx.LIST_STATE_FOCUSED, wx.LIST_STATE_SELECTED | wx.LIST_STATE_FOCUSED)
            self.listCtrl.EnsureVisible(new_view_index)
        except ValueError: pass
        self._update_button_states()

class FavPlaylistPanel(wx.Panel):
    def __init__(self, parent, core_instance):
        wx.Panel.__init__(self, parent)
        self.core = core_instance
        self.playlists = []
        self.filtered_playlists = []
        self._is_first_load = True
        self.last_selected_item_before_search = None
        self.fav_file_path = os.path.join(os.path.dirname(__file__), 'fav_playlist.json')

        mainSizer = wx.BoxSizer(wx.VERTICAL)

        self.listCtrl = wx.ListCtrl(self, style=wx.LC_REPORT | wx.LC_SINGLE_SEL)
        self.listCtrl.InsertColumn(0, _("Playlist Title"), width=350)
        self.listCtrl.InsertColumn(1, _("Channel"), width=200)
        self.listCtrl.InsertColumn(2, _("Videos"), width=80)
        mainSizer.Add(self.listCtrl, 1, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 10)

        btnSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.showVideosBtn = wx.Button(self, label=_("Show &Videos..."))
        self.openWebBtn = wx.Button(self, label=_("Open on &Web"))
        self.addBtn = wx.Button(self, label=_("Add &new favorite playlist from clipboard"))
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
        if event.ShiftDown():
            key_code = event.GetKeyCode()
            if key_code == wx.WXK_UP:
                self.move_item(-1)
            elif key_code == wx.WXK_DOWN:
                self.move_item(1)
            else:
                event.Skip()
            return

        key_code = event.GetKeyCode()
        if key_code == wx.WXK_RETURN:
            self.on_show_videos(event)
        elif key_code == wx.WXK_DELETE:
            self.on_remove(event)
        else:
            event.Skip()

    def move_item(self, direction):
        selected_index_view = self.listCtrl.GetFirstSelected()
        if selected_index_view == -1: return
        if direction == -1 and selected_index_view == 0: return
        if direction == 1 and selected_index_view == self.listCtrl.GetItemCount() - 1: return

        item_to_move = self.filtered_playlists[selected_index_view]
        original_master_index = self.playlists.index(item_to_move)

        self.playlists.pop(original_master_index)
        new_master_index = original_master_index + direction
        self.playlists.insert(new_master_index, item_to_move)
        
        self._save_playlists()
        self.on_search("")
        try:
            new_view_index = self.filtered_playlists.index(item_to_move)
            self.listCtrl.SetItemState(new_view_index, wx.LIST_STATE_SELECTED | wx.LIST_STATE_FOCUSED, wx.LIST_STATE_SELECTED | wx.LIST_STATE_FOCUSED)
            self.listCtrl.EnsureVisible(new_view_index)
        except ValueError: pass
        self._update_button_states()

    def _update_button_states(self):
        has_items = self.listCtrl.GetItemCount() > 0
        self.showVideosBtn.Enable(has_items)
        self.openWebBtn.Enable(has_items)
        self.removeBtn.Enable(has_items)
    
    def on_remove(self, event):
        selected_index = self.listCtrl.GetFirstSelected()
        if selected_index == -1: return
        item_to_remove = self.filtered_playlists[selected_index]
        confirm = wx.MessageBox(
            _("Are you sure you want to remove '{title}'?").format(title=item_to_remove.get('playlist_title')),
            _("Confirm Removal"), wx.YES_NO | wx.ICON_QUESTION, self)
        if confirm != wx.YES: return
        self.playlists.remove(item_to_remove)
        self._save_playlists()
        self.on_search("") 
        item_count = self.listCtrl.GetItemCount()
        if item_count > 0:
            new_selection = min(selected_index, item_count - 1)
            self.listCtrl.SetItemState(new_selection, wx.LIST_STATE_SELECTED | wx.LIST_STATE_FOCUSED, wx.LIST_STATE_SELECTED | wx.LIST_STATE_FOCUSED)
            self.listCtrl.EnsureVisible(new_selection)
        self._update_button_states()
        wx.CallAfter(self.listCtrl.SetFocus)
        self.core._notify_delete(_("Playlist removed."))
        
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
                ui.message(_("Error: Could not save playlist list."))

    def on_add(self, event):
        try:
            url = api.getClipData()
            list_match = re.search(r'[?&]list=([^&]+)', url or "")
            if not url or not self.core.is_youtube_url(url) or not list_match:
                ui.message(_("No valid YouTube playlist URL found in clipboard."))
                return
        except Exception:
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
                self.listCtrl.InsertItem(index, item.get('playlist_title', 'N/A'))
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

    def __new__(cls, *args, **kwargs):  # <--- ✅ เพิ่มเมธอดนี้ทั้งหมด
        if cls._instance is None:
            return super(FavsDialog, cls).__new__(cls, *args, **kwargs)
        cls._instance.Raise()
        return cls._instance

    def __init__(self, parent, core_instance, initial_tab_index=0):
        if self.__class__._instance is not None:
            return
        super().__init__(parent, title=_("Favorites - Youtube Plus"))
        self.__class__._instance = self

        self.core = core_instance
        self.panels = {}

        self.tabs_info = [
            {'id': 'videos', 'panel_class': FavVideoPanel, 'name': _("Videos")},
            {'id': 'channels', 'panel_class': FavChannelPanel, 'name': _("Channels")},
            {'id': 'playlists', 'panel_class': FavPlaylistPanel, 'name': _("Playlists")},
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
        if hasattr(current_page, 'on_search'):
            current_page.on_search(search_text)

    def on_tab_changed(self, event):
        self._update_dialog_title()
        tab_title = self.notebook.GetPageText(self.notebook.GetSelection())
        ui.message(tab_title)

        self.searchCtrl.ChangeValue("")

        current_page = self.notebook.GetCurrentPage()
        if not current_page:
            if event: event.Skip()
            return

        if hasattr(current_page, 'on_search') and self.searchCtrl.GetValue():
            current_page.on_search("")

        if hasattr(current_page, 'listCtrl'):
            wx.CallAfter(current_page.SetFocus)
        
        if event:
            event.Skip()
        
    def _update_dialog_title(self):
        """Helper method to update the dialog's title based on the current tab."""
        currentPage = self.notebook.GetCurrentPage()
        if not currentPage: return

        tab_title = self.notebook.GetPageText(self.notebook.GetSelection())
        full_title = _("Favorites - {tab_name} - Youtube Plus").format(tab_name=tab_title)
        self.SetTitle(full_title)

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

        wx.CallAfter(self.on_tab_changed, None)

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
        super().__init__(parent, title=_("Search YouTube"))
        self.core = core_instance

        panel = wx.Panel(self)
        mainSizer = wx.BoxSizer(wx.VERTICAL)
        sHelper = gui.guiHelper.BoxSizerHelper(self, sizer=mainSizer)

        sHelper.addItem(wx.StaticText(panel, label=_("&Search for:")))
        self.queryText = sHelper.addItem(wx.TextCtrl(panel, style=wx.TE_PROCESS_ENTER))

        sHelper.addItem(wx.StaticText(panel, label=_("Number of &results to fetch:")))
        last_count = config.conf["YoutubePlus"].get("searchResultCount", 20)
        self.countSpin = sHelper.addItem(wx.SpinCtrl(panel, min=5, max=50, initial=last_count))

        btnSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.searchBtn = wx.Button(panel, wx.ID_OK, label=_("&Search"))
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
        self.listCtrl.InsertColumn(0, _("Title"), width=450)
        self.listCtrl.InsertColumn(1, _("Duration"), width=120)
        mainSizer.Add(self.listCtrl, 1, wx.EXPAND | wx.ALL, 10)

        btnSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.actionBtn = wx.Button(panel, label=_("&Action..."))
        self.copyBtn = wx.Button(panel, label=_("&Copy..."))
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
        self.listCtrl.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.on_open_video)
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

    def on_open_video(self, event):
        """Handles both Enter key and menu selection."""
        video = self.get_selected_video_info()
        if not video: return
        webbrowser.open(f"https://www.youtube.com/watch?v={video.get('id')}")

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
            self.listCtrl.InsertItem(index, video.get('title', 'N/A'))
            self.listCtrl.SetItem(index, 1, video.get('duration_str', ''))
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
        super().__init__(parent, title=_("Manage Subscriptions"))
        self.__class__._instance = self
 
        self.core = core_instance
        self.db_path = os.path.join(os.path.dirname(__file__), 'subscription.db')

        self.all_channels = []
        self.categories = []
        
        panel = wx.Panel(self)
        topSizer = wx.BoxSizer(wx.VERTICAL)
        mainSplitSizer = wx.BoxSizer(wx.HORIZONTAL)
        
        leftPanel = wx.Panel(panel)
        leftSizer = wx.BoxSizer(wx.VERTICAL)
        
        leftSizer.Add(wx.StaticText(leftPanel, label=_("Subscribed &Channels:")), 0, wx.BOTTOM, 5)
        self.channelListCtrl = wx.ListCtrl(leftPanel, style=wx.LC_REPORT | wx.LC_SINGLE_SEL)
        self.channelListCtrl.InsertColumn(0, _("Channel Name"), width=300)
        leftSizer.Add(self.channelListCtrl, 1, wx.EXPAND)

        filterSizer = wx.BoxSizer(wx.HORIZONTAL)
        filterSizer.Add(wx.StaticText(leftPanel, label=_("Filter by Category:")), 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 5)
        self.categoryFilterCombo = wx.ComboBox(leftPanel, style=wx.CB_READONLY)
        filterSizer.Add(self.categoryFilterCombo, 1, wx.EXPAND)
        leftSizer.Add(filterSizer, 0, wx.EXPAND | wx.TOP, 5)
        leftPanel.SetSizer(leftSizer)

        self.rightPanel = wx.Panel(panel)
        rightSizer = wx.BoxSizer(wx.VERTICAL)

        catBox = wx.StaticBoxSizer(wx.VERTICAL, self.rightPanel, label=_("Assign to Categories"))
        catHelper = gui.guiHelper.BoxSizerHelper(self, sizer=catBox)
        self.categoryCheckList = catHelper.addItem(gui.nvdaControls.CustomCheckListBox(self.rightPanel))
        rightSizer.Add(catBox, 1, wx.EXPAND | wx.ALL, 5)

        typeBox = wx.StaticBoxSizer(wx.VERTICAL, self.rightPanel, label=_("Content Types to Fetch"))
        typeHelper = gui.guiHelper.BoxSizerHelper(self, sizer=typeBox)
        self.contentTypesList = typeHelper.addItem(gui.nvdaControls.CustomCheckListBox(self.rightPanel, choices=[_("Videos"), _("Shorts"), _("Live")]))
        rightSizer.Add(typeBox, 0, wx.EXPAND | wx.ALL, 5)

        actionBox = wx.StaticBoxSizer(wx.VERTICAL, self.rightPanel, label=_("Actions"))
        actionHelper = gui.guiHelper.BoxSizerHelper(self, sizer=actionBox)
        self.viewContentBtn = actionHelper.addItem(wx.Button(self.rightPanel, label=_("View &Content...")))
        self.addBtn = actionHelper.addItem(wx.Button(self.rightPanel, label=_("Add &new subscribe channel from Clipboard...")))
        self.unsubBtn = actionHelper.addItem(wx.Button(self.rightPanel, label=_("&Unsubscribe from this Channel")))
        rightSizer.Add(actionBox, 0, wx.EXPAND | wx.ALL, 5)

        self.rightPanel.SetSizer(rightSizer)
        
        mainSplitSizer.Add(leftPanel, 1, wx.EXPAND | wx.ALL, 5)
        mainSplitSizer.Add(self.rightPanel, 1, wx.EXPAND | wx.ALL, 5)
        topSizer.Add(mainSplitSizer, 1, wx.EXPAND)

        btnSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.saveBtn = wx.Button(panel, wx.ID_OK, label=_("&Save Changes"))
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
            ui.message(_("Changes saved for the selected channel."))
        except Exception as e:
            log.error("Failed to save subscription changes: %s", e)
            ui.message(_("Error saving changes."))

    def on_view_channel_content(self, event):
            """Shows a submenu to view different content types for the selected channel."""
            selected_index = self.channelListCtrl.GetFirstSelected()
            if selected_index == -1: return
            original_index = self.channelListCtrl.GetItemData(selected_index)
            channel_url, channel_name = self.all_channels[original_index]

            if not channel_url:
                ui.message(_("Error: Channel URL not found."))
                return
            
            menu = wx.Menu()
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
                title_template = _("Fetching {type} from {channel}...").format(channel=channel_name, type=label)

                thread_kwargs = {
                    'url': full_url,
                    'dialog_title_template': title_template,
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
            ui.message(_("Could not read from clipboard."))
            return
        
        threading.Thread(target=self.core.subscribe_to_channel_worker, args=(url,), daemon=True).start()
        
    def on_unsubscribe(self, event):
        selected_index = self.channelListCtrl.GetFirstSelected()
        if selected_index == -1: return
        original_index = self.channelListCtrl.GetItemData(selected_index)
        channel_url, channel_name = self.all_channels[original_index]
        if wx.MessageBox(_("Are you sure you want to unsubscribe from '{name}'?").format(name=channel_name), _("Confirm Unsubscribe"), wx.YES_NO | wx.ICON_QUESTION) != wx.YES:
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
        
        super().__init__(parent, title=_("Subscription Feed"))
        self.__class__._instance = self # Register the new instance
        
        self.core = core_instance
        self.db_path = os.path.join(os.path.dirname(__file__), 'subscription.db')

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

        # <<< FIXED: จัดเรียงปุ่มกลับไปตามตำแหน่งเดิม >>>
        btnSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.addBtn = wx.Button(panel, label=_("Add &new Subscription from clipboard URL."))
        self.updateBtn = wx.Button(panel, label=_("&Update Feed"))
        self.moreBtn = wx.Button(panel, label=_("&More..."))
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

        fixed_tabs = [{'id': 'all', 'name': _("All")}, {'id': 'videos', 'name': _("Videos")}, {'id': 'shorts', 'name': _("Shorts")}, {'id': 'streams', 'name': _("Live")}]
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

        # 1. สลับตำแหน่งใน self.tab_order (ลิสต์ข้อมูลในหน่วยความจำ)
        current_tab_info = self.tab_order.pop(current_index)
        self.tab_order.insert(new_index, current_tab_info)
        
        try:
            # 2. บันทึกลำดับใหม่ทั้งหมดลง config และฐานข้อมูล
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
            
            # <<< FINAL: ใช้วิธีที่ปลอดภัยที่สุด คือการสร้าง UI ใหม่ทั้งหมด >>>
            # โดยใช้ wx.CallAfter เพื่อให้แน่ใจว่า Event ปัจจุบันทำงานจบก่อน
            wx.CallAfter(self._build_all_tabs, select_tab_id=current_tab_info['id'])

        except Exception as e:
            log.error("Failed to reorder tabs: %s", e)
            ui.message(_("Error reordering tabs."))
            
    def on_tab_changed(self, event):
        """
        Called when the user selects a different tab.
        Announces the new tab and updates the dialog title.
        """
        new_tab_index = event.GetSelection()
        new_tab_title = self.notebook.GetPageText(new_tab_index)
        
        # <<< FINAL: ใช้ทั้งสองวิธีร่วมกันเพื่อประสบการณ์ที่ดีที่สุด >>>
        # 1. อัปเดต Title ของหน้าต่าง
        self._update_dialog_title()
        # 2. สั่งให้อ่านชื่อแท็บใหม่ทันที (เหมือนเดิม)
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
        full_title = _("Subscription Feed - {tab_name} - Youtube Plus").format(tab_name=tab_title)
        self.SetTitle(full_title)            
        
    def _create_tab_panel(self, tab_id):
        panel = wx.Panel(self.notebook)
        sizer = wx.BoxSizer(wx.VERTICAL)
        listCtrl = wx.ListCtrl(panel, style=wx.LC_REPORT | wx.LC_SINGLE_SEL)
        listCtrl.InsertColumn(0, _("Video Title"), width=350)
        listCtrl.InsertColumn(1, _("Type"), width=80)
        listCtrl.InsertColumn(2, _("Channel Name"), width=200)
        listCtrl.InsertColumn(3, _("Duration"), width=120)
        sizer.Add(listCtrl, 1, wx.EXPAND | wx.ALL, 5)
        btnSizer = wx.BoxSizer(wx.HORIZONTAL)
        actionBtn = wx.Button(panel, label=_("&Action..."))
        copyBtn = wx.Button(panel, label=_("&Copy..."))
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
        type_map = {"videos": _("Video"), "shorts": _("Shorts"), "streams": _("Live")}
        for index, video in enumerate(videos_to_show):
            panel.listCtrl.InsertItem(index, video.get('title', 'N/A'))
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

    def on_add_subscription(self, event):
        try:
            url = api.getClipData()
            if not url or not self.core.is_youtube_url(url):
                ui.message(_("No valid YouTube URL found in clipboard."))
                return
        except:
            ui.message(_("Could not read from clipboard."))
            return
        threading.Thread(target=self.core.subscribe_to_channel_worker, args=(url,), daemon=True).start()

    def on_more_menu(self, event):
            """Shows the 'More...' menu with added category management and pruning options."""
            menu = wx.Menu()
            ID_MARK_ALL, ID_TOGGLE_VIEW, ID_MANAGE_SUBS = wx.NewIdRef(count=3)
            ID_ADD_CAT, ID_RENAME_CAT, ID_REMOVE_CAT = wx.NewIdRef(count=3)
            ID_PRUNE_ALL = wx.NewIdRef() # <--- ✅ เพิ่ม ID สำหรับเมนูใหม่
            
            menu.Append(ID_MARK_ALL, _("Mark &all in current tab as seen (control+delete)"))
            
            toggle_label = _("Show all &videos (including seen)") if self.view_mode == 'unseen' else _("Show only &unseen videos")
            menu.Append(ID_TOGGLE_VIEW, toggle_label)
            
            menu.Append(ID_MANAGE_SUBS, _("&Manage subscriptions..."))
            
            menu.AppendSeparator()
            menu.Append(ID_ADD_CAT, _("Add New &Category...\tCtrl+="))
            menu.Append(ID_RENAME_CAT, _("&Rename Current Category...\tF2"))
            menu.Append(ID_REMOVE_CAT, _("Remove Current Category...\tCtrl+-"))

            menu.AppendSeparator()
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
            dialog_title = _("Updating Feed ({count} channels)").format(count=channel_count)
            self.progress_dialog = wx.ProgressDialog(
                dialog_title, _("Starting..."),
                maximum=total_tasks if total_tasks > 0 else 1,
                parent=self,
                style=wx.PD_APP_MODAL | wx.PD_AUTO_HIDE | wx.PD_ELAPSED_TIME | wx.PD_REMAINING_TIME
            )
            self.progress_dialog.Show()
            threading.Thread(target=self.core._update_subscription_feed_worker, args=("sub_feed_progress",), daemon=True).start()
        wx.CallAfter(create_and_run)

    def _on_progress_update(self, data):
        if not self.progress_dialog: return
        current = data.get("current", 0)
        total = data.get("total", 1)
        message = data.get("message", "")
        
        self.progress_dialog.Update(current, message)
        
        if current >= total:
            self.progress_dialog = None

    def on_action_menu(self, event):
        video = self.get_selected_video_info()
        if not video: return
        menu = self.create_video_action_menu()
        menu.AppendSeparator()
        ID_UNSUB = wx.NewIdRef()
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

        self._mark_videos_as_seen_db([video_to_mark])
        self.core._notify_callbacks("subscriptions_updated")
        self.core._notify_delete(_("Marked as seen."))
        
    def on_mark_all_seen(self, event=None):
        currentPage = self.notebook.GetCurrentPage()
        if not currentPage or not hasattr(currentPage, 'videos'): return
        videos_in_current_tab = currentPage.videos
        if not videos_in_current_tab:
            ui.message(_("There are no videos in this tab to mark as seen."))
            return
        confirm_msg = _("Are you sure you want to mark all {count} videos in this tab as seen?").format(count=len(videos_in_current_tab))
        if wx.MessageBox(confirm_msg, _("Confirm"), wx.YES_NO | wx.ICON_QUESTION) != wx.YES:
            return
        self._mark_videos_as_seen_db(videos_in_current_tab)
        self.core._notify_callbacks("subscriptions_updated")
        self.core._notify_delete(_("All videos in the current tab have been marked as seen."))

    def _mark_videos_as_seen_db(self, video_list):
        if not video_list: return
        try:
            con = sqlite3.connect(self.db_path)
            ids_to_mark = [(v['id'],) for v in video_list]
            con.executemany("INSERT OR IGNORE INTO seen_videos (video_id) VALUES (?)", ids_to_mark)
            con.commit()
        finally:
            if con: con.close()

    def on_open_video(self, event):
        video = self.get_selected_video_info()
        if not video: return
        webbrowser.open(f"https://youtube.com/watch?v={video.get('id')}")

    def on_list_key_down(self, event):
        """Handles key presses on the list, including all shortcuts."""
        control_down = event.ControlDown()
        key_code = event.GetKeyCode()

        if control_down:
            # --- จัดการคีย์ลัดที่มีปุ่ม Control ---

            # Ctrl+Number (1-9) สำหรับกระโดดไปที่แท็บ
            if ord('1') <= key_code <= ord('9'):
                target_tab_index = key_code - ord('1')
                if target_tab_index < self.notebook.GetPageCount():
                    self.notebook.SetSelection(target_tab_index)
                return

            # Ctrl+= (สำหรับเพิ่มหมวดหมู่)
            if key_code == ord('='):
                self.on_add_category()
                return
            # Ctrl+- (สำหรับลบหมวดหมู่)
            elif key_code == ord('-'):
                self.on_remove_category()
                return

            elif key_code == wx.WXK_DELETE:
                self.on_mark_all_seen()
                return

            # Ctrl+Up/Down/Left/Right (สำหรับจัดลำดับแท็บ)
            elif key_code in (wx.WXK_UP, wx.WXK_LEFT):
                self._move_tab(-1)
                return
            elif key_code in (wx.WXK_DOWN, wx.WXK_RIGHT):
                self._move_tab(1)
                return
            else:
                event.Skip()

        # --- จัดการคีย์ลัดที่ไม่มีปุ่ม Control ---
        elif key_code == wx.WXK_F2:
            self.on_rename_category()
        elif key_code in (wx.WXK_RETURN, wx.WXK_SPACE):
            self.on_open_video(event)
        elif key_code == wx.WXK_DELETE: # Delete ธรรมดา
            self.on_mark_seen(event)
        else:
            event.Skip()
            
    def on_unsubscribe(self, event):
        video = self.get_selected_video_info()
        if not video: return
        channel_name = video.get('channel_name', 'this channel')
        confirm_msg = _("Are you sure you want to unsubscribe from '{channel}'?").format(channel=channel_name)
        if wx.MessageBox(confirm_msg, _("Confirm Unsubscribe"), wx.YES_NO | wx.ICON_QUESTION) != wx.YES:
            return
        threading.Thread(target=self.core.unsubscribe_from_channel_worker, args=(video['channel_url'], video['channel_name']), daemon=True).start()

    def _view_channel_content(self, content_type):
        video = self.get_selected_video_info()
        if not video: return
        channel_url = video.get("channel_url")
        channel_name = video.get("channel_name")
        if not channel_url or not channel_name:
            ui.message(_("Error: Channel information not found for this item."))
            return
        suffix_map = {"videos": "/videos", "shorts": "/shorts", "streams": "/streams"}
        label_map = {"videos": _("Videos"), "shorts": _("Shorts"), "streams": _("Live")}
        suffix = suffix_map.get(content_type, "/videos")
        label = label_map.get(content_type, _("Content"))
        full_url = channel_url.rstrip('/') + suffix
        title_template = _("Fetching {type} from {channel}...").format(channel=channel_name, type=label)
        thread_kwargs = {
            'url': full_url, 'dialog_title_template': title_template, 'content_type_label': label,
            'base_channel_url': channel_url, 'base_channel_name': channel_name
        }
        threading.Thread(target=self.core._view_channel_worker, kwargs=thread_kwargs, daemon=True).start()
        
    def on_add_category(self):
        """Handles adding a new user-defined category."""
        with wx.TextEntryDialog(self, _("Enter new category name:"), _("Add Category")) as dlg:
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
                        ui.message(_("A category with this name already exists."))
                    except Exception as e:
                        log.error("Failed to add category: %s", e)
                        ui.message(_("Error adding category."))
        wx.CallAfter(self.notebook.GetCurrentPage().SetFocus)

    def on_rename_category(self):
        """Handles renaming the current user-defined category."""
        currentPage = self.notebook.GetCurrentPage()
        if not currentPage or not isinstance(currentPage.tab_id, int):
            ui.message(_("This is a fixed tab and cannot be renamed."))
            return
        
        cat_id = currentPage.tab_id
        old_name = self.notebook.GetPageText(self.notebook.GetSelection())
        
        with wx.TextEntryDialog(self, _("Enter new name for '{name}':").format(name=old_name), _("Rename Category"), value=old_name) as dlg:
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
                        ui.message(_("A category with this name already exists."))
                    except Exception as e:
                        log.error("Failed to rename category: %s", e)
                        ui.message(_("Error renaming category."))
        wx.CallAfter(self.notebook.GetCurrentPage().SetFocus)

    def on_remove_category(self):
        """Handles removing the current user-defined category."""
        currentPage = self.notebook.GetCurrentPage()
        if not currentPage or not isinstance(currentPage.tab_id, int):
            ui.message(_("This is a fixed tab and cannot be removed."))
            return

        cat_id = currentPage.tab_id
        name = self.notebook.GetPageText(self.notebook.GetSelection())
        
        if wx.MessageBox(_("Are you sure you want to remove the '{name}' category?").format(name=name), _("Confirm Removal"), wx.YES_NO | wx.ICON_QUESTION) != wx.YES:
            return

        try:
            con = sqlite3.connect(self.db_path)
            cur = con.cursor()
            cur.execute("DELETE FROM categories WHERE id = ?", (cat_id,))
            con.commit()
            con.close()
            self.core._notify_callbacks("subscriptions_updated")
            self.core._notify_delete(_("Category '{name}' removed.").format(name=name))
        except Exception as e:
            log.error("Failed to remove category: %s", e)
            self.core._notify_error(_("Error removing category."))
        wx.CallAfter(self.notebook.GetCurrentPage().SetFocus)
        