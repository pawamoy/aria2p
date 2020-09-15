"""
Utils module.

This module contains simple utility classes and functions.
"""
import signal
import textwrap
from datetime import timedelta
from pathlib import Path
from typing import List

import pkg_resources
import toml
from loguru import logger
from xdg import XDG_CONFIG_HOME


class SignalHandler:
    """A helper class to handle signals."""

    def __init__(self, signals: List[str]) -> None:
        """
        Initialization method.

        Args:
            signals: List of signals names as found in the ``signal`` module (example: SIGTERM).
        """
        logger.debug("Signal handler: handling signals " + ", ".join(signals))
        self.triggered = False
        for sig in signals:
            try:
                signal.signal(signal.Signals[sig], self.trigger)
            except ValueError as error:
                logger.error(f"Failed to setup signal handler for {sig}: {error}")

    def __bool__(self):
        """Return True when one of the given signal was received, False otherwise."""
        return self.triggered

    # pylint: disable=unused-argument
    def trigger(self, signum, frame) -> None:
        """Mark this instance as 'triggered' (a specified signal was received)."""
        logger.debug(f"Signal handler: caught signal {signal.Signals(signum).name} ({signum})")
        self.triggered = True


class Version:
    """Helper class to manipulate version numbers."""

    def __init__(self, version_string):
        self.version_string = version_string
        self.major, self.minor, self.patch = (int(v) for v in version_string.split("."))

    def __str__(self):
        return self.version_string


def human_readable_timedelta(value: timedelta, precision: int = 0) -> str:
    """Return a human-readable time delta as a string."""
    pieces = []

    if value.days:
        pieces.append(f"{value.days}d")

    seconds = value.seconds

    if seconds >= 3600:
        hours = int(seconds / 3600)
        pieces.append(f"{hours}h")
        seconds -= hours * 3600

    if seconds >= 60:
        minutes = int(seconds / 60)
        pieces.append(f"{minutes}m")
        seconds -= minutes * 60

    if seconds > 0 or not pieces:
        pieces.append(f"{seconds}s")

    if not precision:
        return "".join(pieces)

    return "".join(pieces[:precision])


def human_readable_bytes(value: int, digits: int = 2, delim: str = "", postfix: str = "") -> str:
    """
    Return a human-readable bytes value as a string.

    Parameters:
        value: the bytes value.
        digits: how many decimal digits to use.
        delim: string to add between value and unit.
        postfix: string to add at the end.

    Returns:
        The human-readable version of the bytes.
    """
    chosen_unit = "B"
    for unit in ("KiB", "MiB", "GiB", "TiB"):
        if value > 1000:
            value /= 1024
            chosen_unit = unit
        else:
            break
    return f"{value:.{digits}f}" + delim + chosen_unit + postfix


def bool_or_value(value):
    """Return True for 'true', False for 'false', original value otherwise."""
    if value == "true":
        return True
    if value == "false":
        return False
    return value


def bool_to_str(value):
    """Return 'true' for True, 'false' for False, original value otherwise."""
    if value is True:
        return "true"
    if value is False:
        return "false"
    return value


def get_version():
    try:
        distribution = pkg_resources.get_distribution("aria2p")
    except pkg_resources.DistributionNotFound:
        return Version("0.0.0")
    else:
        return Version(distribution.version)


def load_configuration():
    """Return dict from toml formatted string or file."""

    default_config = """
        [key_bindings]
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
            PREVIOUS_SORT = "<"
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

        [colors]
            BRIGHT_HELP = "CYAN BOLD BLACK"
            FOCUSED_HEADER = "BLACK NORMAL CYAN"
            FOCUSED_ROW = "BLACK NORMAL CYAN"
            HEADER = "BLACK NORMAL GREEN"
            METADATA = "WHITE UNDERLINE BLACK"
            SIDE_COLUMN_FOCUSED_ROW = "BLACK NORMAL CYAN"
            SIDE_COLUMN_HEADER = "BLACK NORMAL GREEN"
            SIDE_COLUMN_ROW = "WHITE NORMAL BLACK"
            STATUS_ACTIVE = "CYAN NORMAL BLACK"
            STATUS_COMPLETE = "GREEN NORMAL BLACK"
            STATUS_ERROR = "RED BOLD BLACK"
            STATUS_PAUSED = "YELLOW NORMAL BLACK"
            STATUS_WAITING = "WHITE BOLD BLACK"
    """

    config_dict = {}
    config_dict["DEFAULT"] = toml.loads(default_config)

    # Check for configuration file
    config_file_path = Path(XDG_CONFIG_HOME) / "aria2p" / "config.toml"

    if config_file_path.exists():
        try:
            config_dict["USER"] = toml.load(config_file_path)
            return config_dict

        except Exception as error:
            logger.error(f"Failed to load configuration file: {error}")
            return config_dict
    else:
        # Write initial configuration file if it does not exist
        config_file_path.parent.mkdir(parents=True, exist_ok=True)
        with config_file_path.open("w") as fd:
            fd.write(textwrap.dedent(default_config).lstrip("\n"))
    return config_dict
