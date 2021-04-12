"""Command to resume downloads."""

import sys
from typing import List

from aria2p.api import API
from aria2p.client import ClientException


def resume(api: API, gids: List[str] = None, do_all: bool = False) -> int:
    """
    Resume subcommand.

    Arguments:
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
