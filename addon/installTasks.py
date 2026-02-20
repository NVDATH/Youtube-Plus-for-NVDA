import os
import shutil
import addonHandler
import globalVars
import gui
import wx
from logHandler import log

addonHandler.initTranslation()

def onInstall():
    addon_name = "YoutubePlus"
    destination_dir = os.path.join(globalVars.appArgs.configPath, "youtubePlus")
    
    old_addon = None
    for addon in addonHandler.getAvailableAddons():
        if addon.name == addon_name and addon.isInstalled:
            old_addon = addon
            break
    
    if not old_addon or old_addon.version > "2026.2.4":
        return

    source_dir = os.path.join(old_addon.path, "globalPlugins", "YoutubePlus")
    if not os.path.exists(source_dir):
        return

    try:
        if not os.path.exists(destination_dir):
            os.makedirs(destination_dir)

        copied_count = 0
        target_files = ["subscription.db"]
        
        for f in os.listdir(source_dir):
            if f.lower().endswith(".json") or f.lower() in target_files:
                src = os.path.join(source_dir, f)
                dst = os.path.join(destination_dir, f)
                
                if not os.path.exists(dst):
                    shutil.copy2(src, dst)
                    copied_count += 1
        
        if copied_count > 0:
            # Translators: Success message for data migration.
            msg = _("Successfully migrated {count} data files to the user directory.").format(count=copied_count)
            # Translators: Title for the migration dialog.
            title = _("YouTube Plus Migration")
            wx.CallAfter(gui.messageBox, msg, title, wx.OK | wx.ICON_INFORMATION)

    except Exception as e:
        log.error(f"YoutubePlus migration failed: {e}")