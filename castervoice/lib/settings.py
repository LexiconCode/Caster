import sys, os
from collections.abc import Mapping
import io
from pathlib import Path

import tomlkit
from appdirs import *
from castervoice.lib import printer, version
from castervoice.lib.util import guidance
from past.builtins import xrange

SOFTWARE_VERSION_NUMBER = version.__version__
SOFTWARE_NAME = "Caster v " + SOFTWARE_VERSION_NUMBER
QTYPE_DEFAULT = "0"
QTYPE_INSTRUCTIONS = "3"
QTYPE_RECORDING = "4"
QTYPE_DIRECTORY = "5"
QTYPE_CONFIRM = "6"
QTTYPE_SETTINGS = "7"

# calculated fields
SETTINGS = None
SYSTEM_INFORMATION = None
WSR = False
_BASE_PATH = None
_USER_DIR = None
_SETTINGS_PATH = None


def get_filename():
    return _SETTINGS_PATH


def _save(data, path):
    """
    Only to be used for settings file.
    :param data:
    :param path:
    :return:
    """
    guidance.offer()
    try:
        formatted_data = str(tomlkit.dumps(data))
        with io.open(path, "wt", encoding="utf-8") as f:
            f.write(formatted_data)
    except Exception as e:
        printer.out("Error saving toml file: {} {}".format(e, _SETTINGS_PATH))


def _init(path):
    guidance.offer()
    result = {}
    try:
        with io.open(path, "rt", encoding="utf-8") as f:
            result = tomlkit.loads(f.read()).value
    except ValueError as e:
        printer.out("\n\n {} while loading settings file: {} \n\n".format(repr(e), path))
        printer.out(sys.exc_info())
    except IOError as e:
        printer.out("\n\n {} while loading settings file: {} \nAttempting to recover...\n\n".format(repr(e), path))
    default_settings = _get_defaults()
    result, num_default_added = _deep_merge_defaults(result, default_settings)
    if num_default_added > 0:
        printer.out("Default settings values added: {} ".format(num_default_added))
        _save(result, _SETTINGS_PATH)
    return result


def _deep_merge_defaults(data, defaults):
    """
    Recursivly merge data and defaults, preferring data.
    Only handles nested dicts and scalar values.
    Modifies `data` in place.
    """
    changes = 0
    for key, default_value in defaults.items():
        # If the key is in the data, use that, but call recursivly if it's a dict.
        if key in data:
            if isinstance(data[key], Mapping):
                child_data, child_changes = _deep_merge_defaults(data[key], default_value)
                data[key] = child_data
                changes += child_changes
        else:
            data[key] = default_value
            changes += 1
    return data, changes


def _get_defaults():
    return {
        "paths": {
            "BASE_PATH":
                _BASE_PATH,
            "USER_DIR":
                _USER_DIR,
            # pathlib string conversion can be removed once pathlib is utilized throughout Caster.
            # DATA
            "RULES_CONFIG_PATH":
                str(Path(_USER_DIR).joinpath("settings/rules.toml")),
            "TRANSFORMERS_CONFIG_PATH":
                str(Path(_USER_DIR).joinpath("settings/transformers.toml")),
            "HOOKS_CONFIG_PATH":
                str(Path(_USER_DIR).joinpath("settings/hooks.toml")),
            "COMPANION_CONFIG_PATH":
                str(Path(_USER_DIR).joinpath("settings/companion_config.toml")),

            # EXECUTABLES
            "REBOOT_PATH":
                str(Path(_BASE_PATH).joinpath("bin/reboot.bat")),
            "REBOOT_PATH_WSR":
                str(Path(_BASE_PATH).joinpath("bin/reboot_wsr.bat")),
            "WSR_PATH":
                str(Path("C:/Windows/Speech/Common/sapisvr.exe")),
            # PYTHON
        },

        # node rules path
        "Tree_Node_Path": {
            "SM_CSS_TREE_PATH": str(Path(_USER_DIR).joinpath("data/sm_css_tree.toml")),
        },

        "online": {
            "online_mode": True,  # False disables updates
            "last_update_date": "None",
            "update_interval": 7  # Days
        },

        # Default enabled hooks: Use hook class name
        "hooks": {
            "default_hooks": ['PrinterHook', 'RulesLoadedHook'],
        },

        # miscellaneous section
        "miscellaneous": {
            "ccr_on": True,
        },
    
        # Grammar reloading section
        "grammar_reloading": {
            "reload_trigger": "timer",  # manual or timer
            "reload_timer_seconds": 5,  # seconds
        },

    }

def settings(key_path, default_value=None):
    """
    This should be the preferred way to use settings.SETTINGS,
    a KeyError-safe function call to access the settings dict.
    """
    dv = False if default_value is None else default_value
    if SETTINGS is None:
        return dv
    value = SETTINGS
    for k in key_path:
        if k in value:
            value = value[k]
        else:
            return dv
    return value


def save_config():
    """
    Save the current in-memory settings to disk
    """
    _save(SETTINGS, _SETTINGS_PATH)


def initialize():
    global SETTINGS
    global _BASE_PATH, _USER_DIR, _SETTINGS_PATH

    if SETTINGS is not None:
        return

    # calculate prerequisites
    _BASE_PATH = str(Path(__file__).resolve().parent.parent)
    if os.getenv("CASTER_USER_DIR") is not None:
        _USER_DIR = os.getenv("CASTER_USER_DIR")
    else:
        _USER_DIR = user_data_dir(appname="caster", appauthor=False)
    _SETTINGS_PATH = str(Path(_USER_DIR).joinpath("settings/settings.toml"))

    # Kick everything off.
    SETTINGS = _init(_SETTINGS_PATH)

    printer.out("Caster User Directory: {}".format(_USER_DIR))
