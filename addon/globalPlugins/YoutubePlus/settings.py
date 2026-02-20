# settings.py for Youtube Plus NVDA Addon

import wx
import gui
import config
import os
import logging
import addonHandler
from .core import GlobalPlugin

# Initialize translations for this file
addonHandler.initTranslation()

class SettingsPanel(gui.settingsDialogs.SettingsPanel):
    # Translators: The title of the category in the NVDA Settings dialog.
    title = _("Youtube Plus")

    def makeSettings(self, sizer):
        sHelper = gui.guiHelper.BoxSizerHelper(self, orientation=wx.VERTICAL)

        # Translators: Label for a setting to choose how the add-on notifies progress.
        sHelper.addItem(wx.StaticText(self, label=_("&Notification mode:")))
        # Translators: Options for notification mode. 
        # Beep: use system beeps; Sound: use audio files; Silent: no notification.
        indicator_choices = [_("Beep"), _("Sound"), _("Silent")]
        self.indicatorModeCombo = sHelper.addItem(wx.ComboBox(self, choices=indicator_choices, style=wx.CB_READONLY))
        mode_map = {'beep': 0, 'sound': 1, 'silent': 2}
        current_mode = config.conf["YoutubePlus"].get("progressIndicatorMode", "beep")
        self.indicatorModeCombo.SetSelection(mode_map.get(current_mode, 0))

        # Translators: Label for a setting to choose the default sort order of videos.
        sHelper.addItem(wx.StaticText(self, label=_("Default &sort order:")))
        # Translators: Options for video sorting order.
        sort_choices = [_("Newest First"), _("Oldest First")]
        self.sortOrderCombo = sHelper.addItem(wx.ComboBox(self, choices=sort_choices, style=wx.CB_READONLY))
        current_sort = config.conf["YoutubePlus"].get("sortOrder", "newest")
        self.sortOrderCombo.SetSelection(0 if current_sort == 'newest' else 1)


        # Translators: Label for a setting to set how many items (videos/shorts) to fetch per channel.
        sHelper.addItem(wx.StaticText(self, label=_("&Items to fetch for each content type:")))
        self.playlistFetchCountSpin = sHelper.addItem(wx.SpinCtrl(self, min=5, max=100, initial=config.conf["YoutubePlus"].get("playlist_fetch_count", 20)))

        # Translators: Label for a setting to choose which content types to fetch when adding a new subscription.
        contentTypesLabel = _("Default content &types for new subscriptions:")
        # Translators: Options for content types to fetch.
        contentChoices = [_("Videos"), _("Shorts"), _("Live")]
        self.contentTypesList = sHelper.addLabeledControl(
            contentTypesLabel, gui.nvdaControls.CustomCheckListBox, choices=contentChoices)
        checkedItems = []
        internalValues = ["videos", "shorts", "streams"]
        savedValues = config.conf["YoutubePlus"].get("contentTypesToFetch", internalValues)
        for value in savedValues:
            if value in internalValues:
                checkedItems.append(internalValues.index(value))
        self.contentTypesList.CheckedItems = checkedItems

        # Translators: Options for the background update interval.
        self.interval_choices = [
            _("Disabled"), _("15 minutes"), _("30 minutes"), _("1 hour"), _("2 hours"),
            _("4 hours"), _("6 hours"), _("12 hours"), _("24 hours")
        ]
        self.interval_values = [0, 15, 30, 60, 120, 240, 360, 720, 1440]
        # Translators: Label for a setting to choose how often the add-on checks for new videos in the background.
        sHelper.addItem(wx.StaticText(self, label=_("Background &update interval:")))
        self.intervalCombo = sHelper.addItem(wx.ComboBox(self, choices=self.interval_choices, style=wx.CB_READONLY))
        current_interval = config.conf["YoutubePlus"].get("autoUpdateIntervalMinutes", 0)
        try:
            self.intervalCombo.SetSelection(self.interval_values.index(current_interval))
        except ValueError:
            self.intervalCombo.SetSelection(0)

        sHelper.addItem(wx.StaticLine(self, style=wx.LI_HORIZONTAL), flag=wx.EXPAND | wx.TOP | wx.BOTTOM, border=5)

        # Translators: Label for a checkbox to toggle automatic reading of new live chat messages.
        self.autoSpeak = sHelper.addItem(wx.CheckBox(self, label=_("&Automatically speak incoming live chat")))
        self.autoSpeak.SetValue(config.conf["YoutubePlus"].get("autoSpeak", True))

        # Translators: Label for a setting to set the live chat refresh rate in seconds.
        sHelper.addItem(wx.StaticText(self, label=_("&Live chat refresh interval (seconds):")))
        self.refreshIntevalSpin = sHelper.addItem(wx.SpinCtrl(self, min=1, max=60, initial=config.conf["YoutubePlus"].get("refreshInteval", 5)))

        # Translators: Label for a setting to set the maximum number of messages stored in the chat history.
        sHelper.addItem(wx.StaticText(self, label=_("Message &history limit (live chat):")))
        self.messageLimitSpin = sHelper.addItem(wx.SpinCtrl(self, min=100, max=20000, initial=config.conf["YoutubePlus"].get("messageLimit", 5000)))
        
        sHelper.addItem(wx.StaticLine(self, style=wx.LI_HORIZONTAL), flag=wx.EXPAND | wx.TOP | wx.BOTTOM, border=5)
        
        # === COOKIE SETTINGS ===
        # Cookie file picker (recommended method)
        """
        sHelper.addItem(wx.StaticText(self, label=_("&Cookie file (cookies.txt):")))
        cookiePathSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.cookieFileTextCtrl = wx.TextCtrl(self, value=config.conf["YoutubePlus"].get("cookieFilePath", ""))
        cookiePathSizer.Add(self.cookieFileTextCtrl, 1, wx.EXPAND | wx.RIGHT, 5)
        self.browseCookieBtn = wx.Button(self, label=_("B&rowse..."))
        cookiePathSizer.Add(self.browseCookieBtn, 0)
        sHelper.addItem(cookiePathSizer, flag=wx.EXPAND)
        self.browseCookieBtn.Bind(wx.EVT_BUTTON, self.onBrowseCookie)
        
        # Help text
        cookieHelpText = wx.StaticText(
            self,
            label=_("Recommended: Use browser extension 'Get cookies.txt LOCALLY' to export cookies.\n"
                   "Leave empty to proceed without cookies.")
        )
        sHelper.addItem(cookieHelpText)
        """
        
        # Browser cookie method (experimental - commented out)
        """
        sHelper.addItem(wx.StaticText(self, label=_("&Cookie method (Experimental - may not work):")))
        cookie_choices = [
            _("Do not use cookies (Default)"),
            _("Chrome"),
            _("Firefox"),
            _("Edge"),
            _("Opera"),
            _("Brave"),
            _("Vivaldi")
        ]
        self.cookieModeCombo = sHelper.addItem(wx.ComboBox(self, choices=cookie_choices, style=wx.CB_READONLY))
        cookie_map = {
            'none': 0,
            'chrome': 1,
            'firefox': 2,
            'edge': 3,
            'opera': 4,
            'brave': 5,
            'vivaldi': 6
        }
        current_cookie_mode = config.conf["YoutubePlus"].get("cookieMode", "none")
        self.cookieModeCombo.SetSelection(cookie_map.get(current_cookie_mode, 0))
        """
        
        sHelper.addItem(wx.StaticLine(self, style=wx.LI_HORIZONTAL), flag=wx.EXPAND | wx.TOP | wx.BOTTOM, border=5)

        # Translators: Label for the setting to choose the default folder for downloads and exported files.
        sHelper.addItem(wx.StaticText(self, label=_("Default download and &export folder path:")))
        pathSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.exportPathTextCtrl = wx.TextCtrl(self, value=config.conf["YoutubePlus"].get("exportPath", ""))
        pathSizer.Add(self.exportPathTextCtrl, 1, wx.EXPAND | wx.RIGHT, 5)
        # Translators: Button to browse for a folder.
        self.browseBtn = wx.Button(self, label=_("&Browse..."))
        pathSizer.Add(self.browseBtn, 0)
        sHelper.addItem(pathSizer, flag=wx.EXPAND)
        self.browseBtn.Bind(wx.EVT_BUTTON, self.onBrowse)

        sHelper.addItem(wx.StaticLine(self, style=wx.LI_HORIZONTAL), flag=wx.EXPAND | wx.TOP | wx.BOTTOM, border=10)

        # Translators: A button in the settings dialog that allows the user to delete all saved data.
        self.clearDataBtn = wx.Button(self, label=_("Clear All Favorite and Subscription Data..."))
        sHelper.addItem(self.clearDataBtn, flag=wx.ALIGN_CENTER)
        self.clearDataBtn.Bind(wx.EVT_BUTTON, self.on_clear_data)

    def onSave(self):
        selection_map_indicator = {0: 'beep', 1: 'sound', 2: 'silent'}
        config.conf["YoutubePlus"]["progressIndicatorMode"] = selection_map_indicator.get(self.indicatorModeCombo.GetSelection(), 'beep')
        config.conf["YoutubePlus"]["sortOrder"] = 'newest' if self.sortOrderCombo.GetSelection() == 0 else 'oldest'

        config.conf["YoutubePlus"]["playlist_fetch_count"] = self.playlistFetchCountSpin.GetValue()
        selected_index = self.intervalCombo.GetSelection()
        if selected_index != wx.NOT_FOUND:
            config.conf["YoutubePlus"]["autoUpdateIntervalMinutes"] = self.interval_values[selected_index]
        content_types = []
        internalValues = ["videos", "shorts", "streams"]
        for index in self.contentTypesList.CheckedItems:
            content_types.append(internalValues[index])
        config.conf["YoutubePlus"]["contentTypesToFetch"] = content_types

        config.conf["YoutubePlus"]["autoSpeak"] = self.autoSpeak.GetValue()
        config.conf["YoutubePlus"]["refreshInteval"] = self.refreshIntevalSpin.GetValue()
        config.conf["YoutubePlus"]["messageLimit"] = self.messageLimitSpin.GetValue()
        
        # Save cookie file path
        #config.conf["YoutubePlus"]["cookieFilePath"] = self.cookieFileTextCtrl.GetValue()
        
        # Browser cookie mode (commented out)
        """
        selection_map_cookie = {
            0: 'none',
            1: 'chrome',
            2: 'firefox',
            3: 'edge',
            4: 'opera',
            5: 'brave',
            6: 'vivaldi'
        }
        config.conf["YoutubePlus"]["cookieMode"] = selection_map_cookie.get(self.cookieModeCombo.GetSelection(), 'none')
        """
        
        config.conf["YoutubePlus"]["exportPath"] = self.exportPathTextCtrl.GetValue()
        
        if GlobalPlugin.instance:
            GlobalPlugin.instance._notify_callbacks("settings_saved")
        logging.info("YoutubePlus settings saved.")
    
    def onBrowseCookie(self, event):
        """Browse for cookies.txt file."""
        logging.debug("Opening file dialog for cookie file.")
        with wx.FileDialog(
            self,
            message=_("Select cookies.txt file"),
            wildcard="Text files (*.txt)|*.txt|All files (*.*)|*.*",
            style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST
        ) as dlg:
            if dlg.ShowModal() == wx.ID_OK:
                path = dlg.GetPath()
                logging.info("User selected cookie file: %s", path)
                self.cookieFileTextCtrl.SetValue(path)
        
    def onBrowse(self, event):
        logging.debug("Opening directory dialog for export path.")
        with wx.DirDialog(self, message=_("Select default folder to export files"), style=wx.DD_DEFAULT_STYLE) as dlg:
            if dlg.ShowModal() == wx.ID_OK:
                path = dlg.GetPath()
                logging.info("User selected new export path: %s", path)
                self.exportPathTextCtrl.SetValue(path)

    def on_clear_data(self, event):
        """Shows a confirmation dialog and calls the plugin to clear all data."""
        confirm = wx.MessageBox(
            _("This will permanently delete all your saved favorite videos, favorite channels, and subscription data. This action cannot be undone.\n\nAre you sure you want to continue?"),
            _("Confirm Data Deletion"),
            wx.YES_NO | wx.ICON_EXCLAMATION, self
        )
        if confirm != wx.YES:
            return
        
        if GlobalPlugin.instance:
            GlobalPlugin.instance.clear_all_user_data()
            
gui.settingsDialogs.NVDASettingsDialog.categoryClasses.append(SettingsPanel)