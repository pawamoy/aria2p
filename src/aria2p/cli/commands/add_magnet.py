"""Command to add magnets."""

from __future__ import annotations

import sys
from typing import TYPE_CHECKING

from aria2p.utils import read_lines

if TYPE_CHECKING:
    from aria2p.api import API


def add_magnets(
    api: API,
    uris: list[str] | None = None,
    from_file: str | None = None,
    options: dict | None = None,
    position: int | None = None,
) -> int:
    """Add magnet subcommand.

    Parameters:
        api: The API instance to use.
        uris: The URIs of the magnets.
        from_file: Path to the file to read uris from.
        options: String of aria2c options to add to download.
        position: Position to add new download in the queue.

    Returns:
        int: Always 0.
    """
    ok = True

    if not uris:
        uris = []

    if from_file:
        try:
            uris.extend(read_lines(from_file))
        except OSError:
            print(f"Cannot open file: {from_file}", file=sys.stderr)
            ok = False

    for uri in uris:
        new_download = api.add_magnet(uri, options=options, position=position)
        print(f"Created download {new_download.gid}")

    return 0 if ok else 1
