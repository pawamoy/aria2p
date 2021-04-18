"""Configuration module."""

import textwrap
from pathlib import Path
from typing import Any, Dict, List, Tuple, Union

import toml
from appdirs import user_config_dir
from asciimatics.screen import Screen
from loguru import logger

color_map = {
    "BLACK": Screen.COLOUR_BLACK,
    "WHITE": Screen.COLOUR_WHITE,
    "RED": Screen.COLOUR_RED,
    "CYAN": Screen.COLOUR_CYAN,
    "YELLOW": Screen.COLOUR_YELLOW,
    "BLUE": Screen.COLOUR_BLUE,
    "GREEN": Screen.COLOUR_GREEN,
    "DEFAULT": Screen.COLOUR_DEFAULT,
}

mode_map = {
    "NORMAL": Screen.A_NORMAL,
    "BOLD": Screen.A_BOLD,
    "UNDERLINE": Screen.A_UNDERLINE,
    "REVERSE": Screen.A_REVERSE,
}

special_keys = {
    "F1": Screen.KEY_F1,
    "F2": Screen.KEY_F2,
    "F3": Screen.KEY_F3,
    "F4": Screen.KEY_F4,
    "F5": Screen.KEY_F5,
    "F6": Screen.KEY_F6,
    "F7": Screen.KEY_F7,
    "F8": Screen.KEY_F8,
    "F9": Screen.KEY_F9,
    "F10": Screen.KEY_F10,
    "F11": Screen.KEY_F11,
    "F12": Screen.KEY_F12,
    "ESC": Screen.KEY_ESCAPE,
    "DEL": Screen.KEY_DELETE,
    "PAGE_UP": Screen.KEY_PAGE_UP,
    "PAGE_DOWN": Screen.KEY_PAGE_DOWN,
    "HOME": Screen.KEY_HOME,
    "END": Screen.KEY_END,
    "LEFT": Screen.KEY_LEFT,
    "UP": Screen.KEY_UP,
    "RIGHT": Screen.KEY_RIGHT,
    "DOWN": Screen.KEY_DOWN,
    "BACK": Screen.KEY_BACK,
    "TAB": Screen.KEY_TAB,
    "SPACE": ord(" "),
    "ENTER": ord("\n"),
}


class Config(dict):  # noqa: WPS600
    """A special class to hold configuration items."""

    def __getattr__(self, name):
        return self[name]


class Key:
    """A class to represent an input key."""

    def __init__(self, name: str, value=None) -> None:
        """
        Initialize the object.

        Arguments:
            name: The key name.
            value: The key value.
        """
        self.name = name
        if value is None:
            try:
                value = ord(name)
            except TypeError:
                value = special_keys[name.upper()]
        self.value = value

    def __eq__(self, value):
        return self.value == value


def parse_style(style: str) -> Tuple[int, int, int]:
    """
    Return a color tuple (foreground color, mode, background color).

    Arguments:
        style: The style value.

    Returns:
        Foreground color, mode, background color.
    """
    foreground, mode, background = style.split(" ")
    return color_map[foreground], mode_map[mode], color_map[background]


def parse_keybinds(keybinds: Union[str, List[str]]) -> List["Key"]:
    """
    Return a list of Key instances.

    Arguments:
        keybinds: A key or list of keys to bind.

    Returns:
        A list of keys.
    """
    if isinstance(keybinds, list):
        return [Key(key) for key in keybinds]
    return [Key(keybinds)]


def merge(default_config, user_config):
    """
    Merge the user configuration into the default configuration.

    Arguments:
        default_config: The default configuration.
        user_config: The user configuration.

    Returns:
        The modified default configuration.
    """
    for key, user_value in user_config.items():
        if key in default_config and isinstance(default_config[key], dict) and isinstance(user_value, dict):
            merge(default_config[key], user_value)
        else:
            default_config[key] = user_value
    return default_config


def load_configuration() -> Dict[str, Any]:
    """
    Return dict from TOML formatted string or file.

    Returns:
        The dict configuration.
    """
    default_config = """
        [keybinds]
        AUTOCLEAR = "c"
        CANCEL = "esc"
        ENTER = "enter"
        FILTER = ["F4", "\\\\"]
        FOLLOW_ROW = "F"
        HELP = ["F1", "?"]
        MOVE_DOWN = ["down", "j"]
        MOVE_DOWN_STEP = "J"
        MOVE_END = "end"
        MOVE_HOME = "home"
        MOVE_LEFT = ["left", "h"]
        MOVE_RIGHT = ["right", "l"]
        MOVE_UP = ["up", "k"]
        MOVE_UP_STEP = "K"
        NEXT_SORT = ["p", ">"]
        PREVIOUS_SORT = ["n", "<"]
        PRIORITY_DOWN = ["F8", "d", "]"]
        PRIORITY_UP = ["F7", "u", "["]
        QUIT = ["F10", "q"]
        REMOVE_ASK = ["del", "F9"]
        RETRY = "r"
        RETRY_ALL = "R"
        REVERSE_SORT = "I"
        SEARCH = ["F3", "/"]
        SELECT_SORT = "F6"
        SETUP = "F2"
        TOGGLE_EXPAND_COLLAPSE = "x"
        TOGGLE_EXPAND_COLLAPSE_ALL = "X"
        TOGGLE_RESUME_PAUSE = "space"
        TOGGLE_RESUME_PAUSE_ALL = "P"
        TOGGLE_SELECT = "s"
        UN_SELECT_ALL = "U"
        ADD_DOWNLOADS = "a"

        [style]
        DEFAULT = "DEFAULT BOLD DEFAULT"
        BRIGHT_HELP = "CYAN BOLD DEFAULT"
        FOCUSED_HEADER = "DEFAULT NORMAL CYAN"
        FOCUSED_ROW = "DEFAULT NORMAL CYAN"
        HEADER = "DEFAULT NORMAL GREEN"
        METADATA = "DEFAULT UNDERLINE DEFAULT"
        SIDE_COLUMN_FOCUSED_ROW = "DEFAULT NORMAL CYAN"
        SIDE_COLUMN_HEADER = "DEFAULT NORMAL GREEN"
        SIDE_COLUMN_ROW = "DEFAULT NORMAL DEFAULT"
        STATUS_ACTIVE = "CYAN NORMAL DEFAULT"
        STATUS_COMPLETE = "GREEN NORMAL DEFAULT"
        STATUS_ERROR = "RED BOLD DEFAULT"
        STATUS_PAUSED = "YELLOW NORMAL DEFAULT"
        STATUS_WAITING = "DEFAULT BOLD DEFAULT"
    """

    config = Config(toml.loads(default_config))

    # Check for configuration file
    config_file_path = Path(user_config_dir("aria2p")) / "config.toml"

    if config_file_path.exists():
        try:
            user_config = toml.load(config_file_path)
        except Exception as error:  # noqa: W0703 (too broad exception)
            logger.error(f"Failed to load configuration file: {error}")
        else:
            merge(config, user_config)
    else:
        # Write initial configuration file if it does not exist
        config_file_path.parent.mkdir(parents=True, exist_ok=True)
        with config_file_path.open("w") as fd:
            fd.write(textwrap.dedent(default_config).lstrip("\n"))

    config["style"] = Config(config["style"])
    for style_name, style in config["style"].items():
        config["style"][style_name] = parse_style(style)

    config["keybinds"] = Config(config["keybinds"])
    for keybinds_name, keybinds in config["keybinds"].items():
        config["keybinds"][keybinds_name] = parse_keybinds(keybinds)

    return config
