"""Command to add torrents."""

from __future__ import annotations

import sys
from typing import TYPE_CHECKING

from aria2p.utils import read_lines

if TYPE_CHECKING:
    from aria2p.api import API


def add_torrents(
    api: API,
    torrent_files: list[str] | None = None,
    from_file: str | None = None,
    options: dict | None = None,
    position: int | None = None,
) -> int:
    """Add torrent subcommand.

    Parameters:
        api: The API instance to use.
        torrent_files: The paths to the torrent files.
        from_file: Path to the file to read torrent files paths from.
        options: String of aria2c options to add to download.
        position: Position to add new download in the queue.

    Returns:
        int: Always 0.
    """
    ok = True

    if not torrent_files:
        torrent_files = []

    if from_file:
        try:
            torrent_files.extend(read_lines(from_file))
        except OSError:
            print(f"Cannot open file: {from_file}", file=sys.stderr)
            ok = False

    for torrent_file in torrent_files:
        new_download = api.add_torrent(torrent_file, options=options, position=position)
        print(f"Created download {new_download.gid}")

    return 0 if ok else 1
