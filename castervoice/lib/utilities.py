import io
import json
import json
import re
import sys
from locale import getpreferredencoding
from pathlib import Path
from urllib.parse import unquote

import tomlkit
from castervoice.lib.util import guidance

from dragonfly import Key, Window, get_current_engine

try:  # Style C -- may be imported into Caster, or externally
    BASE_PATH = str(Path(__file__).resolve().parent.parent)
    if BASE_PATH not in sys.path:
        sys.path.append(BASE_PATH)
finally:
    from castervoice.lib import printer, settings

DARWIN = sys.platform.startswith('darwin')
LINUX = sys.platform.startswith('linux')
WIN32 = sys.platform.startswith('win')

lasthandle = None


# TODO: Move functions that manipulate or retrieve information from Windows to `window_mgmt_support` in navigation_rules.
# TODO: Implement Optional exact title matching for `get_matching_windows` in Dragonfly
def window_exists(windowname=None, executable=None):
    return Window.get_matching_windows(title=windowname, executable=executable) and True


def get_window_by_title(title=None):
    # returns 0 if nothing found
    Matches = Window.get_matching_windows(title=title)
    if Matches:
        return Matches[0].handle
    else:
        return 0


def get_active_window_title():
    return Window.get_foreground().title


def get_active_window_path():
    return Window.get_foreground().executable


def get_active_window_info():
    '''Returns foreground window executable_file, executable_path, title, handle, classname'''
    FILENAME_PATTERN = re.compile(r"[/\\]([\w_ ]+\.[\w]+)")
    window = Window.get_foreground()
    executable_path = str(Path(get_active_window_path()))
    match_object = FILENAME_PATTERN.findall(window.executable)
    executable_file = None
    if len(match_object) > 0:
        executable_file = match_object[0]
    return [executable_file, executable_path, window.title, window.handle, window.classname]


def maximize_window():
    '''
    Maximize foreground Window
    '''
    Window.get_foreground().maximize()


def minimize_window():
    '''
    Minimize foreground Window
    '''
    global lasthandle
    lasthandle = Window.get_foreground()
    Window.get_foreground().minimize()


def close_window():
    '''
    Close foreground Window
    '''
    Window.get_foreground().close()


def restore_window():
    '''
    Restores last minimized window triggered minimize_window.
    '''
    global lasthandle
    if lasthandle is None:
        printer.out("No previous window minimized by voice")
    else:
        Window.restore(lasthandle)


def save_toml_file(data, path):
    guidance.offer()
    try:
        formatted_data = str(tomlkit.dumps(data))
        with io.open(path, "wt", encoding="utf-8") as f:
            f.write(formatted_data)
    except Exception:
        pass


def load_toml_file(path):
    guidance.offer()
    result = {}
    try:
        with io.open(path, "rt", encoding="utf-8") as f:
            result = tomlkit.loads(f.read()).value
    except IOError as e:
        if e.errno == 2:  # The file doesn't exist.
            save_toml_file(result, path)
        else:
            raise
    except Exception:
        pass
    return result


def save_json_file(data, path):
    guidance.offer()
    try:
        formatted_data = str(json.dumps(data, ensure_ascii=False))
        with io.open(path, "wt", encoding="utf-8") as f:
            f.write(formatted_data)
    except Exception:
        pass


def load_json_file(path):
    guidance.offer()
    result = {}
    try:
        with io.open(path, "rt", encoding="utf-8") as json_file:
            result = json.load(json_file)
    except IOError as e:
        if e.errno == 2:  # The file doesn't exist.
            save_json_file(result, path)
        else:
            raise
    except Exception:
        pass
    return result

