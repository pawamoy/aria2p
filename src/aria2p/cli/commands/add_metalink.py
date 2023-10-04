"""Command to add metalinks."""

from __future__ import annotations

import sys
from typing import TYPE_CHECKING

from aria2p.utils import read_lines

if TYPE_CHECKING:
    from aria2p.api import API


def add_metalinks(
    api: API,
    metalink_files: list[str] | None = None,
    from_file: str | None = None,
    options: dict | None = None,
    position: int | None = None,
) -> int:
    """Add metalink subcommand.

    Parameters:
        api: The API instance to use.
        metalink_files: The paths to the metalink files.
        from_file: Path to the file to metalink files paths from.
        options: String of aria2c options to add to download.
        position: Position to add new download in the queue.

    Returns:
        int: 0 if OK else 1.
    """
    ok = True

    if not metalink_files:
        metalink_files = []

    if from_file:
        try:
            metalink_files.extend(read_lines(from_file))
        except OSError:
            print(f"Cannot open file: {from_file}", file=sys.stderr)
            ok = False

    for metalink_file in metalink_files:
        new_downloads = api.add_metalink(metalink_file, options=options, position=position)
        for download in new_downloads:
            print(f"Created download {download.gid}")

    return 0 if ok else 1
