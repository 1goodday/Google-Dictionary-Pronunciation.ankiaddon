# Google Pronunciation Anki Add-on
# Anki Addon to add Google pronunciations (American and/or
# British English accents) to vocabulary entries
#
# Copyright (c) 2021  Roozbeh Sarraf   roozbeh_sarraf@outlook.com
# https://github.com/1goodday/anki_addon_google_pronunciation
# Licensed under MIT License

from . import anki_funcs, settings
from anki.hooks import addHook
from aqt import gui_hooks
from aqt import mw
import warnings

# Turns [currently] unnecessary warnings off.
# This line can be commented/de-commented in case that Future Warning
# messages disappear/appear during the use.
warnings.simplefilter(action='ignore', category=FutureWarning)

# Adds a new button to the editor, and hooks "add_pronunciation_button"
# function to that.
addHook('setupEditorButtons', anki_funcs.add_pronunciation_button)

# Refer to notes in anki webview.py for this line of code.
mw.addonManager.setWebExports(__name__, r"web/.*(css|js)")

# Adds labels to play buttons if selected in the user config file (config.json).
if settings.add_play_button_labels:
    gui_hooks.webview_will_set_content.append(anki_funcs.new_play_button_css)
    gui_hooks.card_will_show.append(anki_funcs.add_button_labels)
