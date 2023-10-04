"""Command to purge downloads."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from aria2p.api import API


def purge(api: API) -> int:
    """Purge subcommand.

    Parameters:
        api: The API instance to use.

    Returns:
        int: 0 if all success, 1 if one failure.
    """
    if api.autopurge():
        return 0
    return 1
