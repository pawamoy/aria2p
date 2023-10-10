"""Generic command to add downloads."""

from __future__ import annotations

import sys
from typing import TYPE_CHECKING

from loguru import logger

if TYPE_CHECKING:
    from aria2p.api import API


def add(
    api: API,
    uris: list[str] | None = None,
    from_file: str | None = None,
    options: dict | None = None,
    position: int | None = None,
) -> int:
    """Add magnet subcommand.

    Parameters:
        api: The API instance to use.
        uris: The URIs or file-paths to add.
        from_file: Path to the file to read uris from.
            Deprecated: Every URI that is a valid file-path
            and is not a torrent or a metalink is now read as an input file.
        options: String of aria2c options to add to download.
        position: Position to add new download in the queue.

    Returns:
        int: 0 if OK else 1.
    """
    uris = uris or []

    if from_file:
        logger.warning(
            "Deprecation warning: every URI that is a valid file-path "
            "and is not a torrent or a metalink is now read as an input file.",
        )

    new_downloads = []

    for uri in uris:
        created_downloads = api.add(uri, options=options, position=position)
        new_downloads.extend(created_downloads)
        if position is not None:
            position += len(created_downloads)

    if new_downloads:
        for new_download in new_downloads:
            print(f"Created download {new_download.gid}")
        return 0

    print("No new download was created", file=sys.stderr)
    return 1
