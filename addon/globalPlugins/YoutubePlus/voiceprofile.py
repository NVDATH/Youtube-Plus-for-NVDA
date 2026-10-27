# -*- coding: utf-8 -*-
# voiceprofile.py for YoutubePlus NVDA add-on
# Copyright (C) 2025
# This file is covered by the GNU General Public License.
# You can read the licence by clicking Help->Licence in the NVDA menu
# or by visiting http://www.gnu.org/licenses/old-licenses/gpl-2.0.html

"""
Reads live chat messages in the voice of a user-chosen NVDA configuration
profile, through a synthesizer instance of its own, like a media player that
runs next to NVDA.

Why a separate synthesizer instead of switching NVDA's profile per message:
switching the profile's synthesizer for every message of a fast chat made NVDA
crash, and NVDA cancels the main synthesizer on (almost) every key press, which
cut the chat off. Here the main synthesizer is never touched:

* the chosen profile's synthesizer is created once, when reading starts, and
  terminated when it stops;
* messages are queued here and spoken one at a time;
* chat reading is independent of NVDA's own speech: NVDA's key presses and
  announcements never pause, cancel or wait for it. If the user wants to hear
  both at once, that is their choice; turning automatic reading off (R in the
  YoutubePlus layer) stops it immediately.
"""

import collections
import time

import wx
import characterProcessing
import config
import speech
import synthDriverHandler
from logHandler import log
from synthDriverHandler import synthDoneSpeaking

# Private key an earlier build used in config.conf.triggersToProfiles.
_LEGACY_TRIGGER_SPEC = "youtubePlusLiveChat"

# Messages waiting to be spoken. When chat is faster than it can be read, the
# oldest ones are dropped from speech (they all stay in the message list).
MAX_QUEUE = 20
# Alerts (Super Chat, Super Sticker, new member) are read before ordinary
# messages and are not dropped to make room for them.
MAX_PRIORITY_QUEUE = 50
# Safety net for a synthesizer that never reports that a message finished.
TICK_MS = 1000
MESSAGE_TIMEOUT_BASE_S = 15
MESSAGE_TIMEOUT_PER_CHAR_S = 0.2
# A synthesizer that stops answering is replaced by a fresh instance, but only
# once per this many seconds; failing again sooner gives the voice profile up.
RECOVERY_INTERVAL_S = 60


def available_profile_names():
    """
    Names of the user's NVDA configuration profiles, sorted. The base
    configuration (empty name) is not included.
    """
    try:
        return sorted((n for n in config.conf.listProfiles() if n), key=str.casefold)
    except Exception:
        log.exception("YoutubePlus: could not list NVDA configuration profiles.")
        return []


def scrub_stale_mapping():
    """
    Drops the private trigger mapping an earlier build of this add-on used, in
    case NVDA persisted it to profileTriggers.ini. Harmless when absent.
    """
    try:
        config.conf.triggersToProfiles.pop(_LEGACY_TRIGGER_SPEC, None)
    except Exception:
        log.exception("YoutubePlus: could not remove a stale voice profile mapping.")


class VoiceProfile:
    """
    Speaks live chat messages with the voice settings of a named NVDA profile.
    Every method must be called on the main thread.
    """

    def __init__(self):
        self._synth = None
        self._name = None
        self._queue = collections.deque()
        self._priorityQueue = collections.deque()
        self._speaking = False
        self._speakStart = 0.0
        self._speakLimit = 0.0
        self._tickCall = None
        self._registered = False
        self._lastRecovery = float("-inf")

    @property
    def name(self):
        """Name of the profile currently in use, or None."""
        return self._name if self._synth is not None else None

    # ---------------------------------------------------------------- lifecycle

    def arm(self, name):
        """Call when reading starts. Returns True if the profile's voice is now in use."""
        self.release()
        if not name:
            return False
        try:
            if name not in available_profile_names():
                return False  # deleted since it was chosen
            synth = self._createSynth(name)
        except Exception:
            log.exception(f"YoutubePlus: could not start the voice profile '{name}'.")
            return False
        self._synth = synth
        self._name = name
        self._register()
        return True

    def release(self):
        """Call when reading stops and from terminate(). Cancels anything still being read."""
        self._unregister()
        self._cancelLater("_tickCall")
        self._queue.clear()
        self._priorityQueue.clear()
        wasSpeaking, self._speaking = self._speaking, False
        synth, self._synth, self._name = self._synth, None, None
        if synth is None:
            return
        # Only cancel what is really being read: some drivers share audio state between instances.
        actions = ([synth.cancel] if wasSpeaking else []) + [synth.terminate]
        for action in actions:
            try:
                action()
            except Exception as e:
                log.warning(f"YoutubePlus: closing the voice profile's synthesizer failed: {e!r}")

    @staticmethod
    def _createSynth(profileName):
        """
        Creates a synthesizer instance configured like the named profile.

        The instance is built directly rather than with getSynthInstance(): that
        function also rebinds NVDA's global synth settings ring and voice
        dictionary to the new instance and may write a config section for it,
        none of which is wanted for a second voice.
        """
        profile = config.conf._getProfile(profileName)
        speechSection = profile.get("speech") or {}
        synthName = speechSection.get("synth")
        if not synthName or synthName == "auto":
            synthName = synthDriverHandler.getSynth().name
        synth = synthDriverHandler._getSynthDriver(synthName)()
        try:
            VoiceProfile._applySettings(synth, synthName, speechSection)
        except Exception:
            try:
                synth.terminate()
            except Exception:
                pass
            raise
        return synth

    @staticmethod
    def _applySettings(synth, synthName, speechSection):
        """
        Settings the profile sets for this synthesizer win; for anything the
        profile leaves alone, the current configuration's value is used.
        """
        try:
            own = speechSection.get(synthName)
        except Exception:
            own = None
        try:
            base = config.conf["speech"][synthName]
        except Exception:
            base = None
        settings = sorted(synth.supportedSettings, key=lambda s: s.id != "voice")  # voice first
        for setting in settings:
            if not getattr(setting, "useConfig", True):
                continue
            value = None
            for section in (own, base):
                if section is None:
                    continue
                try:
                    value = section.get(setting.id)
                except Exception:
                    value = None
                if value is not None:
                    break
            if value is None:
                continue
            try:
                current = getattr(synth, setting.id, None)
                if isinstance(current, bool):
                    value = value if isinstance(value, bool) else str(value).lower() in ("true", "1", "yes")
                elif isinstance(current, int):
                    value = int(value)
                setattr(synth, setting.id, value)
            except Exception as e:
                log.warning(f"YoutubePlus: could not apply the voice profile setting '{setting.id}': {e}")

    # ----------------------------------------------------------------- speaking

    def speak(self, text, priority=False):
        """
        Queues a message. Returns True if the voice profile took care of it
        (spoken, or deliberately silent because NVDA's speech mode isn't "talk"),
        False if the caller should speak it in the normal voice instead.
        `priority` messages are read before ordinary ones.
        """
        if self._synth is None:
            return False
        try:
            if speech.getState().speechMode != speech.SpeechMode.talk:
                return True
        except Exception:
            pass
        text = self._process(text)
        if not text:
            return True
        if priority:
            self._priorityQueue.append(text)
            while len(self._priorityQueue) > MAX_PRIORITY_QUEUE:
                self._priorityQueue.popleft()
        else:
            self._queue.append(text)
            while len(self._queue) > MAX_QUEUE:
                self._queue.popleft()
        self._pump()
        return True

    @staticmethod
    def _process(text):
        """The symbol pronunciation and speech dictionary processing speech.speak applies."""
        try:
            level = characterProcessing.SymbolLevel(config.conf["speech"]["symbolLevel"])
            return speech.processText(speech.getCurrentLanguage(), text, level)
        except Exception:
            return text.strip()

    def _pump(self):
        """Starts the next queued message when nothing is being read."""
        if self._synth is None or self._speaking:
            return
        if self._priorityQueue:
            text = self._priorityQueue.popleft()
        elif self._queue:
            text = self._queue.popleft()
        else:
            return
        self._speaking = True
        self._speakStart = time.monotonic()
        self._speakLimit = MESSAGE_TIMEOUT_BASE_S + MESSAGE_TIMEOUT_PER_CHAR_S * len(text)
        try:
            self._synth.speak([text])
        except Exception:
            log.exception("YoutubePlus: the voice profile's synthesizer failed to speak.")
            self._speaking = False
            wx.CallAfter(self._pump)
            return
        self._later("_tickCall", TICK_MS, self._tick)

    def _tick(self):
        """Watchdog: moves on if the synthesizer never reports that a message finished."""
        self._tickCall = None
        if self._synth is None or not self._speaking:
            return
        if time.monotonic() - self._speakStart > self._speakLimit:
            log.warning("YoutubePlus: the voice profile's synthesizer did not report the end of a message.")
            self._recoverSynth()
            return
        self._later("_tickCall", TICK_MS, self._tick)

    def _recoverSynth(self):
        """
        The synthesizer stopped answering. Some drivers lose their engine
        (for example after another instance of the same driver was closed) and
        then silently drop everything they are given; a fresh instance fixes
        that, which is what turning automatic reading off and on again does.
        If it happens again within RECOVERY_INTERVAL_S, or a new instance can't
        be created, the voice profile is given up and chat messages are read in
        NVDA's normal voice instead of going silent.
        """
        name = self._name
        old, self._synth = self._synth, None
        self._speaking = False
        now = time.monotonic()
        failedAgain = now - self._lastRecovery < RECOVERY_INTERVAL_S
        self._lastRecovery = now
        if old is not None:
            for action in (old.cancel, old.terminate):
                try:
                    action()
                except Exception as e:
                    log.warning(f"YoutubePlus: closing the unresponsive synthesizer failed: {e!r}")
        if failedAgain or not name:
            log.warning("YoutubePlus: the voice profile's synthesizer keeps failing; using the normal voice.")
            self.release()
            return
        try:
            self._synth = self._createSynth(name)
        except Exception:
            log.exception("YoutubePlus: could not restart the voice profile's synthesizer; using the normal voice.")
            self.release()
            return
        log.info("YoutubePlus: restarted the voice profile's synthesizer.")
        self._pump()

    def _register(self):
        if not self._registered:
            synthDoneSpeaking.register(self._onSynthDone)
            self._registered = True

    def _unregister(self):
        if self._registered:
            self._registered = False
            try:
                synthDoneSpeaking.unregister(self._onSynthDone)
            except Exception:
                pass

    def _onSynthDone(self, synth=None, **kwargs):
        """A synthesizer finished everything it was given (may be called from any thread)."""
        if synth is not None and synth is self._synth:
            wx.CallAfter(self._ownMessageDone)

    def _ownMessageDone(self):
        if self._synth is None or not self._speaking:
            return  # stale notification
        self._speaking = False
        self._pump()

    # ------------------------------------------------------------------ helpers

    def _later(self, attribute, milliseconds, callback):
        """(Re)starts the named single-shot timer."""
        self._cancelLater(attribute)
        setattr(self, attribute, wx.CallLater(milliseconds, callback))

    def _cancelLater(self, attribute):
        call = getattr(self, attribute, None)
        if call is not None:
            try:
                if call.IsRunning():
                    call.Stop()
            except Exception:
                pass
            setattr(self, attribute, None)
