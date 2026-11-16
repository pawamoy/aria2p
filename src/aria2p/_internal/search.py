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

# Validation and matching helpers for download searches.

from __future__ import annotations

import re
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from aria2p._internal.downloads import Download

# Only local scalar properties are searchable. Properties such as live and options
# would issue additional RPC calls, and relationship properties retrieve other downloads.
_SEARCH_FIELDS = frozenset(
    {
        "name",
        "gid",
        "status",
        "total_length",
        "completed_length",
        "upload_length",
        "bitfield",
        "download_speed",
        "upload_speed",
        "info_hash",
        "num_seeders",
        "seeder",
        "piece_length",
        "num_pieces",
        "connections",
        "error_code",
        "error_message",
        "following_id",
        "belongs_to_id",
        "dir",
        "verified_length",
        "verify_integrity_pending",
        "progress",
        "eta",
        "is_active",
        "is_waiting",
        "is_paused",
        "has_failed",
        "is_complete",
        "is_removed",
        "is_metadata",
        "is_torrent",
    }
)


def _validate_search_field(field: str) -> None:
    """Reject fields that cannot be searched without additional RPC calls."""
    if field not in _SEARCH_FIELDS:
        raise ValueError(f"Unknown search field {field!r}. Available fields: {', '.join(sorted(_SEARCH_FIELDS))}")


def _compile_search_pattern(pattern: str) -> re.Pattern[str]:
    """Compile a case-insensitive regex, allowing scoped flags such as (?-i:...)."""
    try:
        return re.compile(pattern, re.IGNORECASE)
    except re.error as error:
        raise ValueError(f"Invalid regular expression {pattern!r}: {error}") from error


def _matches_filter(download: Download, field: str, expected: object) -> bool:
    """Compare typed API values or their string representations from the CLI."""
    try:
        value = getattr(download, field)
    except KeyError:
        # aria2 omits some fields, such as numSeeders, for non-torrent downloads.
        return False

    if isinstance(expected, str):
        if isinstance(value, bool):
            return str(value).lower() == expected.lower()
        return str(value) == expected
    return value == expected
