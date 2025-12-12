# -*- coding: utf-8 -*-
# Youtube plus for NVDA
# Copyright (C) 2025
# This file is covered by the GNU General Public License.
# You can read the licence by clicking Help->Licence in the NVDA menu
# or by visiting http://www.gnu.org/licenses/old-licenses/gpl-2.0.html
# Shortcut: Windows+y

import os
import sys
import addonHandler

# Initialize translations for the addon package
addonHandler.initTranslation()

# Set up the library path first so all other modules can find third-party libraries.
lib_path = os.path.join(os.path.dirname(__file__), "lib")
if lib_path not in sys.path:
    sys.path.insert(0, lib_path)

# Import the main plugin class from its new file for NVDA to load.
from .core import GlobalPlugin
from .settings import SettingsPanel