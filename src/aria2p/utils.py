"""
Utils module.

This module contains simple utility classes and functions.
"""

import signal
from datetime import timedelta
from pathlib import Path
from typing import Any, List

import pkg_resources
from loguru import logger

from aria2p.types import PathOrStr


class SignalHandler:
    """A helper class to handle signals."""

    def __init__(self, signals: List[str]) -> None:
        """
        Initialize the object.

        Arguments:
            signals: List of signals names as found in the `signal` module (example: SIGTERM).
        """
        logger.debug("Signal handler: handling signals " + ", ".join(signals))
        self.triggered = False
        for sig in signals:
            try:
                signal.signal(signal.Signals[sig], self.trigger)  # noqa: E1101 (signal.Signals)
            except ValueError as error:
                logger.error(f"Failed to setup signal handler for {sig}: {error}")

    def __bool__(self) -> bool:
        """
        Return True when one of the given signal was received, False otherwise.

        Returns:
            True when signal received, False otherwise.
        """
        return self.triggered

    def trigger(self, signum, frame) -> None:  # noqa: W0613 (unused frame)
        """
        Mark this instance as 'triggered' (a specified signal was received).

        Arguments:
            signum: The signal code.
            frame: The signal frame (unused).
        """
        logger.debug(
            f"Signal handler: caught signal {signal.Signals(signum).name} ({signum})",  # noqa: E1101 (signal.Signals)
        )
        self.triggered = True


def human_readable_timedelta(value: timedelta, precision: int = 0) -> str:
    """
    Return a human-readable time delta as a string.

    Arguments:
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

    if seconds >= 3600:  # noqa: WPS432 (magic number)
        hours = int(seconds / 3600)  # noqa: WPS432
        pieces.append(f"{hours}h")
        seconds -= hours * 3600  # noqa: WPS432

    if seconds >= 60:
        minutes = int(seconds / 60)
        pieces.append(f"{minutes}m")
        seconds -= minutes * 60

    if seconds > 0 or not pieces:
        pieces.append(f"{seconds}s")

    if precision == 0:
        return "".join(pieces)

    return "".join(pieces[:precision])


def human_readable_bytes(value: int, digits: int = 2, delim: str = "", postfix: str = "") -> str:
    """
    Return a human-readable bytes value as a string.

    Arguments:
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
        if hr_value > 1000:
            hr_value /= 1024
            chosen_unit = unit
        else:
            break
    return f"{hr_value:.{digits}f}" + delim + chosen_unit + postfix  # noqa: WPS221 (not complex)


def bool_or_value(value) -> Any:
    """
    Return `True` for `"true"`, `False` for `"false"`, original value otherwise.

    Arguments:
        value: Any kind of value.

    Returns:
        - `True` for `"true"`
        - `False` for `"false"`
        - Original value otherwise
    """
    if value == "true":
        return True
    if value == "false":
        return False
    return value


def bool_to_str(value) -> Any:
    """
    Return `"true"` for `True`, `"false"` for `False`, original value otherwise.

    Arguments:
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
    """
    Return the current `aria2p` version.

    Returns:
        The current `aria2p` version.
    """
    try:
        distribution = pkg_resources.get_distribution("aria2p")
    except pkg_resources.DistributionNotFound:
        return "0.0.0"
    return distribution.version


def read_lines(path: PathOrStr) -> List[str]:
    """
    Read lines in a file.

    Arguments:
        path: The file path.

    Returns:
        The list of lines.
    """
    return Path(path).read_text().splitlines()
