"""
Utils module.

This module contains simple utility functions.
"""


def human_readable_timedelta(value):
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
    unit = "B"
    for u in ("KiB", "MiB", "GiB", "TiB"):
        if value > 1000:
            value /= 1024
            unit = u
        else:
            break
    return f"{value:.{digits}f}" + delim + unit + postfix


def bool_or_value(value):
    if value == "true":
        return True
    elif value == "false":
        return False
    else:
        return value


def bool_to_str(value):
    if value is True:
        return "true"
    elif value is False:
        return "false"
    else:
        return value
