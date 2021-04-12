"""Command to pause downloads."""

import sys
from typing import List

from aria2p.api import API
from aria2p.client import ClientException


def pause(api: API, gids: List[str] = None, do_all: bool = False, force: bool = False) -> int:
    """
    Pause subcommand.

    Arguments:
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
