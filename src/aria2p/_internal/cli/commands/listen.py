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

# Command to listen to notifications from the server.

from __future__ import annotations

import sys
from importlib import util as importlib_util
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from aria2p._internal.api import API


def listen(
    api: API,
    callbacks_module: str | Path | None = None,
    event_types: list[str] | None = None,
    timeout: int = 5,
) -> int:
    """Listen subcommand.

    Parameters:
        api: The API instance to use.
        callbacks_module: The path to the module to import, containing the callbacks as functions.
        event_types: The event types to process.
        timeout: The timeout to pass to the WebSocket connection, in seconds.

    Returns:
        int: Always 0.
    """
    if not callbacks_module:
        print("aria2p: listen: Please provide the callback module file path with -c option", file=sys.stderr)
        return 1

    if isinstance(callbacks_module, Path):
        callbacks_module = str(callbacks_module)

    if not event_types:
        event_types = ["start", "pause", "stop", "error", "complete", "btcomplete"]

    spec = importlib_util.spec_from_file_location("aria2p_callbacks", callbacks_module)

    if spec is None:
        print(f"aria2p: Could not import module file {callbacks_module}", file=sys.stderr)
        return 1

    callbacks = importlib_util.module_from_spec(spec)

    if callbacks is None:
        print(f"aria2p: Could not import module file {callbacks_module}", file=sys.stderr)
        return 1

    spec.loader.exec_module(callbacks)  # ty:ignore[unresolved-attribute]

    callbacks_kwargs = {}
    for callback_name in (
        "on_download_start",
        "on_download_pause",
        "on_download_stop",
        "on_download_error",
        "on_download_complete",
        "on_bt_download_complete",
    ):
        if callback_name[3:].replace("download", "").replace("_", "") in event_types:
            callback = getattr(callbacks, callback_name, None)
            if callback:
                callbacks_kwargs[callback_name] = callback

    api.listen_to_notifications(timeout=timeout, handle_signals=True, threaded=False, **callbacks_kwargs)
    return 0
