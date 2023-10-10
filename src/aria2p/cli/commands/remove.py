"""Command to remove downloads."""

from __future__ import annotations

import sys
from typing import TYPE_CHECKING

from aria2p.client import ClientException

if TYPE_CHECKING:
    from aria2p.api import API


def remove(
    api: API,
    gids: list[str] | None = None,
    do_all: bool = False,  # noqa: FBT001,FBT002
    force: bool = False,  # noqa: FBT001,FBT002
) -> int:
    """Remove subcommand.

    Parameters:
        api: The API instance to use.
        gids: The GIDs of the downloads to remove.
        do_all: Pause all downloads if True.
        force: Force pause or not (see API.remove).

    Returns:
        int: 0 if all success, 1 if one failure.
    """
    if do_all:
        if api.remove_all():
            return 0
        return 1

    try:
        downloads = api.get_downloads(gids)
    except ClientException as error:
        print(str(error), file=sys.stderr)
        return 1

    ok = True
    result = api.remove(downloads, force=force)

    if all(result):
        return 0 if ok else 1

    for item in result:
        if isinstance(item, ClientException):
            print(item, file=sys.stderr)

    return 1
