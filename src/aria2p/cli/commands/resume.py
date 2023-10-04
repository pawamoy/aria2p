"""Command to resume downloads."""

from __future__ import annotations

import sys
from typing import TYPE_CHECKING

from aria2p.client import ClientException

if TYPE_CHECKING:
    from aria2p.api import API


def resume(api: API, gids: list[str] | None = None, do_all: bool = False) -> int:  # noqa: FBT001,FBT002
    """Resume subcommand.

    Parameters:
        api: The API instance to use.
        gids: The GIDs of the downloads to resume.
        do_all: Pause all downloads if True.

    Returns:
        int: 0 if all success, 1 if one failure.
    """
    if do_all:
        if api.resume_all():
            return 0
        return 1

    try:
        downloads = api.get_downloads(gids)
    except ClientException as error:
        print(str(error), file=sys.stderr)
        return 1

    result = api.resume(downloads)

    if all(result):
        return 0

    for item in result:
        if isinstance(item, ClientException):
            print(item, file=sys.stderr)

    return 1
