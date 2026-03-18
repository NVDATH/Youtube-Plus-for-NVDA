# -*- coding: utf-8 -*-
# errors.py for Youtube Plus NVDA Addon
# Copyright (C) 2025
# This file is covered by the GNU General Public License.
# You can read the licence by clicking Help->Licence in the NVDA menu
# or by visiting http://www.gnu.org/licenses/old-licenses/gpl-2.0.html
# Shortcut: Windows+y

class HandledError(Exception):
    """
    Base exception for errors that are handled and reported to the user,
    and shouldn't be logged as unexpected critical failures.
    """
    pass

class NetworkRetryError(HandledError):
    """Exception raised when a network operation fails after all retries."""
    pass