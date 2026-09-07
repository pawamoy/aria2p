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

# This module defines the Stats class.
#
# It holds information retrieved with the `get_global_stat` method of the client.

from __future__ import annotations

from aria2p._internal.utils import human_readable_bytes


class Stats:
    """This class holds information retrieved with the `get_global_stat` method of the client."""

    def __init__(self, struct: dict) -> None:
        """Initialize the object.

        Parameters:
            struct: A dictionary Python object returned by the JSON-RPC client.
        """
        self._struct = struct or {}

    @property
    def download_speed(self) -> int:
        """Overall download speed (byte/sec).

        Returns:
            The overall download speed in bytes per second.
        """
        return int(self._struct["downloadSpeed"])

    def download_speed_string(self, human_readable: bool = True) -> str:  # noqa: FBT001,FBT002
        """Return the download speed as string.

        Parameters:
            human_readable: Return in human readable format or not.

        Returns:
            The download speed string.
        """
        if human_readable:
            return human_readable_bytes(self.download_speed, delim=" ", postfix="/s")
        return str(self.download_speed) + " B/s"

    @property
    def upload_speed(self) -> int:
        """Overall upload speed (byte/sec).

        Returns:
            The overall upload speed in bytes per second.
        """
        return int(self._struct["uploadSpeed"])

    def upload_speed_string(self, human_readable: bool = True) -> str:  # noqa: FBT001,FBT002
        """Return the upload speed as string.

        Parameters:
            human_readable: Return in human readable format or not.

        Returns:
            The upload speed string.
        """
        if human_readable:
            return human_readable_bytes(self.upload_speed, delim=" ", postfix="/s")
        return str(self.upload_speed) + " B/s"

    @property
    def num_active(self) -> int:
        """Return the number of active downloads.

        Returns:
            The number of active downloads.
        """
        return int(self._struct["numActive"])

    @property
    def num_waiting(self) -> int:
        """Return the number of waiting downloads.

        Returns:
            The number of waiting downloads.
        """
        return int(self._struct["numWaiting"])

    @property
    def num_stopped(self) -> int:
        """Return the number of stopped downloads in the current session.

        This value is capped by the [`--max-download-result`][aria2p.Options.max_download_result] option.

        Returns:
            The number of stopped downloads in the current session (capped).
        """
        return int(self._struct["numStopped"])

    @property
    def num_stopped_total(self) -> int:
        """Return the number of stopped downloads in the current session.

        This value is not capped by the [`--max-download-result`][aria2p.Options.max_download_result] option.

        Returns:
            The number of stopped downloads in the current session (not capped).
        """
        return int(self._struct["numStoppedTotal"])
