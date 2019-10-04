"""
Utils module.

This module contains simple utility classes and functions.
"""
import signal

from loguru import logger


class SignalHandler:
    """A helper class to handle signals."""

    def __init__(self, signals):
        """
        Initialization method.

        Args:
            signals (list of str): List of signals names as found in the ``signal`` module (example: SIGTERM).
        """
        logger.debug("Signal handler: handling signals " + ", ".join(signals))
        self.triggered = False
        for sig in signals:
            signal.signal(signal.Signals[sig], self.trigger)

    def __bool__(self):
        """Return True when one of the given signal was received, False otherwise."""
        return self.triggered

    def trigger(self, signum, frame):
        """Mark this instance as 'triggered' (a specified signal was received)."""
        logger.debug(f"Signal handler: caught signal {signal.Signals(signum).name} ({signum})")
        self.triggered = True


class Queue:
    def __init__(self, items):
        self._mapping = {}
        self._items = []
        for i, d in enumerate(items):
            self._mapping[d] = i
            self._items.append(d)

    def __bool__(self):
        return bool(self._items)

    def __len__(self):
        return len(self._items)

    def __getitem__(self, item):
        return self._items[item]

    def __delitem__(self, key):
        self.remove(self._items[key])

    def __iter__(self):
        return iter(self._items)

    def as_list(self):
        return list(self._items)

    def index(self, item):
        return self._mapping[item]

    def move(self, item, new_index):
        current_index = self.index(item)

        # didn't move (should not be triggered by API)
        if current_index == new_index:
            return False

        # shift up or down depending on movement
        if new_index < current_index:
            self._shift_down(new_index, current_index - 1)
        else:
            self._shift_up(current_index + 1, new_index)

        # assign new index to download
        self._mapping[item] = new_index

        # update mapping and de-fragment
        self._sync()

        return True

    def remove(self, item):
        del self._mapping[item]
        self._sync()

    def _shift(self, start, stop, step):
        for i in range(start, stop + 1):
            self._mapping[self._items[i]] += step

    def _shift_up(self, start, stop, step=1):
        self._shift(start, stop, -step)

    def _shift_down(self, start, stop, step=1):
        self._shift(start, stop, step)

    def _sync(self):
        self._items = [item for item, index in sorted(self._mapping.items(), key=lambda x: x[1])]
        for index, item in enumerate(self._items):
            self._mapping[item] = index


def human_readable_timedelta(value):
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

    return "".join(pieces)


def human_readable_bytes(value, digits=2, delim="", postfix=""):
    """
    Return a human-readable bytes value as a string.

    Args:
        value (int): the bytes value.
        digits (int): how many decimal digits to use.
        delim (str): string to add between value and unit.
        postfix (str): string to add at the end.

    Returns:
        str: the human-readable version of the bytes.
    """
    unit = "B"
    for u in ("KiB", "MiB", "GiB", "TiB"):
        if value > 1000:
            value /= 1024
            unit = u
        else:
            break
    return f"{value:.{digits}f}" + delim + unit + postfix


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
