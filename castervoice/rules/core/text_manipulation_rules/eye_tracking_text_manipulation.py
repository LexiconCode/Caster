# Credit goes to wolfmanstout
# https://handsfreecoding.org/2020/07/25/say-what-you-see-efficient-ui-interaction-with-ocr-and-gaze-tracking/
# https://github.com/wolfmanstout/gaze-ocr

import sys
import six
import tempfile
import requests
import zipfile
import threading
import time
import gaze_ocr
import screen_ocr  # dependency of gaze-ocr

from dragonfly import (
    Dictation,
    Grammar,
    MappingRule,
    get_engine,
)

from castervoice.lib.actions import Key, Text, Mouse
from castervoice.lib.ctrl.mgr.rule_details import RuleDetails
from castervoice.lib.merge.state.short import R
from castervoice.lib import settings

import six
if six.PY2:
    from castervoice.lib.util.pathlib import Path
else:
    from pathlib import Path # pylint: disable=import-error

tobii = Path.joinpath(Path(settings.SETTINGS["paths"]["USER_DIR"]), "third_party_integration\\tobii\\dll")

def set_up_tobii_dlls():
    """Downloads and Unzips dll `Tobii Interaction` in to Caster user directory from nuget"""
    temp = tempfile.TemporaryDirectory()
    temp_zip = Path.joinpath(Path(temp.name, 'Tobii.zip'))
    try:
        response = r"https://www.nuget.org/api/v2/package/Tobii.Interaction"
        zip = requests.get(response, allow_redirects=True)
        open(temp_zip, 'wb').write(zip.content)

        dlls = ("AnyCPU/Tobii.EyeX.Client.dll", "Tobii.Interaction.Model.dll", "Tobii.Interaction.Net.dll")
        with zipfile.ZipFile(temp_zip) as z:
            for file in z.namelist():
                if file.endswith(dlls):
                    tobii.mkdir(parents=True, exist_ok=True)
                    with open(Path.joinpath(tobii, Path(file).name), 'w+b') as f:
                        f.write(z.read(file))
    except Exception as e:
        print(e)

if not Path(tobii).is_dir():
    print("\n Caster: Setting up Tobii DLL files in {}\n".format(tobii))
    set_up_tobii_dlls()


# Initialize eye tracking and OCR.
tracker = gaze_ocr.eye_tracking.EyeTracker.get_connected_instance(str(tobii))
ocr_reader = screen_ocr.Reader.create_fast_reader()
gaze_ocr_controller = gaze_ocr.Controller(ocr_reader, tracker) 

if not tracker.is_connected:
    if sys.platform == "win32":
        print("\n Caster: is tobii software installed and `screen-ocr[winrt]`? \n See: https://gaming.tobii.com/getstarted/ and `pip install screen-ocr[winrt]`")
    else:
        print("\n Caster: is tobii software installed and `screen-ocr[tesseract]`? \n See: https://gaming.tobii.com/getstarted/ and `pip install screen-ocr[tesseract]`")
    print("\n Caster: Restart Caster when dependencies are installed. \n")

class TobiiRule(MappingRule):
    mapping = {
        # Click on text.
        "<text> click": gaze_ocr_controller.move_cursor_to_word_action("%(text)s") + Mouse("left"),
 
        # Move the cursor for text editing.
        "go before <text>": gaze_ocr_controller.move_cursor_to_word_action("%(text)s", "before") + Mouse("left"),
        "go after <text>": gaze_ocr_controller.move_cursor_to_word_action("%(text)s", "after") + Mouse("left"),
 
        # Select text starting from the current position.
        "words before <text>": gaze_ocr_controller.move_cursor_to_word_action("%(text)s", "before") + Key("shift:down") + Mouse("left") + Key("shift:up"),
        "words after <text>": gaze_ocr_controller.move_cursor_to_word_action("%(text)s", "after") + Key("shift:down") + Mouse("left") + Key("shift:up"),
 
        # Select a phrase or range of text.
        "words <text> [through <text2>]": gaze_ocr_controller.select_text_action("%(text)s", "%(text2)s"),
 
        # Select and replace text.
        "replace <text> with <replacement>": gaze_ocr_controller.select_text_action("%(text)s") + Text("%(replacement)s"),
    }
 
    extras = [
        Dictation("text"),
        Dictation("text2"),
        Dictation("replacement"),
    ]
 
    def _process_begin(self):
        # Start OCR now so that results are ready when the command completes.
        gaze_ocr_controller.start_reading_nearby()
 
def get_rule():
    return TobiiRule, RuleDetails(name="tobii rule")
