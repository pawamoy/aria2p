"""Command to pause downloads."""

from __future__ import annotations

import sys
from typing import TYPE_CHECKING

from aria2p.client import ClientException

if TYPE_CHECKING:
    from aria2p.api import API


def pause(
    api: API,
    gids: list[str] | None = None,
    do_all: bool = False,  # noqa: FBT001,FBT002
    force: bool = False,  # noqa: FBT001,FBT002
) -> int:
    """Pause subcommand.

    Parameters:
        api: The API instance to use.
        gids: The GIDs of the downloads to pause.
        do_all: Pause all downloads if True.
        force: Force pause or not (see API.pause).

    Returns:
        int: 0 if all success, 1 if one failure.
    """
    if do_all:
        if api.pause_all(force=force):
            return 0
        return 1

    try:
        downloads = api.get_downloads(gids)
    except ClientException as error:
        print(str(error), file=sys.stderr)
        return 1

    result = api.pause(downloads, force=force)

    if all(result):
        return 0

    for item in result:
        if isinstance(item, ClientException):
            print(item, file=sys.stderr)

    return 1
