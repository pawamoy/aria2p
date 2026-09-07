# SPDX-License-Identifier: ISC
#
# ISC License
#
# Copyright (c) 2020, Timothée Mazzucotelli and contributors
#
# Permission to use, copy, modify, and/or distribute this software for any
# purpose with or without fee is hereby granted, provided that the above
# copyright notice and this permission notice appear in all copies.
#
# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
# WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
# ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
# WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
# ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
# OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.

# Generic command to add downloads.

from __future__ import annotations

import sys
from typing import TYPE_CHECKING

from loguru import logger

if TYPE_CHECKING:
    from aria2p._internal.api import API


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
