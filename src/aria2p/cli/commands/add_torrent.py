"""Command to add torrents."""

import sys
from typing import List

from aria2p.api import API
from aria2p.utils import read_lines


def add_torrents(
    api: API,
    torrent_files: List[str] = None,
    from_file: str = None,
    options: dict = None,
    position: int = None,
) -> int:
    """
    Add torrent subcommand.

    Arguments:
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
