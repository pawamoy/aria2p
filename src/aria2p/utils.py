"""Utils module.

This module contains simple utility classes and functions.
"""

from __future__ import annotations

import signal
import textwrap
from pathlib import Path
from typing import TYPE_CHECKING, Any

import pkg_resources
import toml
from appdirs import user_config_dir
from loguru import logger

if TYPE_CHECKING:
    from datetime import timedelta
    from types import FrameType


class SignalHandler:
    """A helper class to handle signals."""

    def __init__(self, signals: list[str]) -> None:
        """Initialize the object.

        Parameters:
            signals: List of signals names as found in the `signal` module (example: SIGTERM).
        """
        logger.debug("Signal handler: handling signals " + ", ".join(signals))
        self.triggered = False
        for sig in signals:
            try:
                signal.signal(signal.Signals[sig], self.trigger)
            except ValueError as error:
                logger.error(f"Failed to setup signal handler for {sig}: {error}")

    def __bool__(self) -> bool:
        """Return True when one of the given signal was received, False otherwise.

        Returns:
            True when signal received, False otherwise.
        """
        return self.triggered

    def trigger(self, signum: int, frame: FrameType | None) -> None:  # noqa: ARG002
        """Mark this instance as 'triggered' (a specified signal was received).

        Parameters:
            signum: The signal code.
            frame: The signal frame (unused).
        """
        logger.debug(
            f"Signal handler: caught signal {signal.Signals(signum).name} ({signum})",
        )
        self.triggered = True


def human_readable_timedelta(value: timedelta, precision: int = 0) -> str:
    """Return a human-readable time delta as a string.

    Parameters:
        value: The timedelta.
        precision: The precision to use:

            - `0` to display all units
            - `1` to display the biggest unit only
            - `2` to display the first two biggest units only
            - `n` for the first N biggest units, etc.

    Returns:
        A string representing the time delta.
    """
    pieces = []

    if value.days:
        pieces.append(f"{value.days}d")

    seconds = value.seconds

    if seconds >= 3600:  # noqa: PLR2004
        hours = int(seconds / 3600)
        pieces.append(f"{hours}h")
        seconds -= hours * 3600

    if seconds >= 60:  # noqa: PLR2004
        minutes = int(seconds / 60)
        pieces.append(f"{minutes}m")
        seconds -= minutes * 60

    if seconds > 0 or not pieces:
        pieces.append(f"{seconds}s")

    if precision == 0:
        return "".join(pieces)

    return "".join(pieces[:precision])


def human_readable_bytes(value: int, digits: int = 2, delim: str = "", postfix: str = "") -> str:
    """Return a human-readable bytes value as a string.

    Parameters:
        value: The bytes value.
        digits: How many decimal digits to use.
        delim: String to add between value and unit.
        postfix: String to add at the end.

    Returns:
        The human-readable version of the bytes.
    """
    hr_value: float = value
    chosen_unit = "B"
    for unit in ("KiB", "MiB", "GiB", "TiB"):
        if hr_value > 1000:  # noqa: PLR2004
            hr_value /= 1024
            chosen_unit = unit
        else:
            break
    return f"{hr_value:.{digits}f}" + delim + chosen_unit + postfix


def bool_or_value(value: Any) -> Any:
    """Return `True` for `"true"`, `False` for `"false"`, original value otherwise.

    Parameters:
        value: Any kind of value.

    Returns:
        One of these values:

            - `True` for `"true"`
            - `False` for `"false"`
            - Original value otherwise
    """
    if value == "true":
        return True
    if value == "false":
        return False
    return value


def bool_to_str(value: Any) -> Any:
    """Return `"true"` for `True`, `"false"` for `False`, original value otherwise.

    Parameters:
        value: Any kind of value.

    Returns:
        - `"true"` for `True`
        - `"false"` for `False`
        - Original value otherwise
    """
    if value is True:
        return "true"
    if value is False:
        return "false"
    return value


def get_version() -> str:
    """Return the current `aria2p` version.

    Returns:
        The current `aria2p` version.
    """
    try:
        distribution = pkg_resources.get_distribution("aria2p")
    except pkg_resources.DistributionNotFound:
        return "0.0.0"
    return distribution.version


def load_configuration() -> dict[str, Any]:
    """Return dict from TOML formatted string or file.

    Returns:
        The dict configuration.
    """
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
        UI = "WHITE BOLD DEFAULT"
        BRIGHT_HELP = "CYAN BOLD DEFAULT"
        FOCUSED_HEADER = "BLACK NORMAL CYAN"
        FOCUSED_ROW = "BLACK NORMAL CYAN"
        HEADER = "BLACK NORMAL GREEN"
        METADATA = "WHITE UNDERLINE DEFAULT"
        SIDE_COLUMN_FOCUSED_ROW = "DEFAULT NORMAL CYAN"
        SIDE_COLUMN_HEADER = "BLACK NORMAL GREEN"
        SIDE_COLUMN_ROW = "DEFAULT NORMAL DEFAULT"
        STATUS_ACTIVE = "CYAN NORMAL DEFAULT"
        STATUS_COMPLETE = "GREEN NORMAL DEFAULT"
        STATUS_ERROR = "RED BOLD DEFAULT"
        STATUS_PAUSED = "YELLOW NORMAL DEFAULT"
        STATUS_WAITING = "WHITE BOLD DEFAULT"
    """

    config_dict = {}
    config_dict["DEFAULT"] = toml.loads(default_config)

    # Check for configuration file
    config_file_path = Path(user_config_dir("aria2p")) / "config.toml"

    if config_file_path.exists():
        try:
            config_dict["USER"] = toml.load(config_file_path)
        except Exception as error:  # noqa: BLE001
            logger.error(f"Failed to load configuration file: {error}")
    else:
        # Write initial configuration file if it does not exist
        config_file_path.parent.mkdir(parents=True, exist_ok=True)
        with config_file_path.open("w") as fd:
            fd.write(textwrap.dedent(default_config).lstrip("\n"))
    return config_dict


def read_lines(path: str | Path) -> list[str]:
    """Read lines in a file.

    Parameters:
        path: The file path.

    Returns:
        The list of lines.
    """
    return Path(path).read_text().splitlines()
