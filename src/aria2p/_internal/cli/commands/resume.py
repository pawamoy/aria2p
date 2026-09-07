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

# Command to resume downloads.

from __future__ import annotations

import sys
from typing import TYPE_CHECKING

from aria2p._internal.client import ClientException

if TYPE_CHECKING:
    from aria2p._internal.api import API


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
