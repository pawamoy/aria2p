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

# Command to show downloads.

# YORE: Bump 2: Remove file.

from __future__ import annotations

import warnings
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from aria2p._internal.api import API


def show(api: API) -> int:
    """Show subcommand.

    Deprecated. Use [`list_downloads`][aria2p.list_downloads] with `output_format="long"` and `human_readable=True` instead.

    Parameters:
        api: The API instance to use.

    Returns:
        int: Always 0.
    """
    warnings.warn(
        "The 'show' command is deprecated and will be removed in version 2. Use 'list -l -H' instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    downloads = api.get_downloads()

    def print_line(*args: Any) -> None:
        print("{:<17} {:<9} {:>8} {:>12} {:>12} {:>8}  {}".format(*args))

    print_line("GID", "STATUS", "PROGRESS", "DOWN_SPEED", "UP_SPEED", "ETA", "NAME")

    for download in downloads:
        print_line(
            download.gid,
            download.status,
            download.progress_string(),
            download.download_speed_string(),
            download.upload_speed_string(),
            download.eta_string(),
            download.name,
        )

    return 0
