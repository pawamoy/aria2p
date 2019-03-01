"""
Utils module.

This module contains simple utility functions.
"""


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
