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

# List selected downloads with configurable output and ordering.

from __future__ import annotations

import sys
from datetime import timedelta
from fnmatch import fnmatchcase
from operator import attrgetter
from string import Formatter
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from aria2p._internal.api import API
    from aria2p._internal.downloads import Download


_FIELDS = (
    "gid",
    "status",
    "progress",
    "total_length",
    "completed_length",
    "download_speed",
    "upload_speed",
    "eta",
    "name",
)
_FORMATS = {
    "name": "{name}",
    "gid": "{gid}",
    "long": "{gid:<17} {status:<9} {progress:>7.2f}% {download_speed:>12} {upload_speed:>12} {eta:>8}  {name}",
}
_LONG_HEADER = "{:<17} {:<9} {:>8} {:>12} {:>12} {:>8}  {}".format(
    "GID", "STATUS", "PROGRESS", "DOWN_SPEED", "UP_SPEED", "ETA", "NAME"
)


def _format_values(download: Download, *, human_readable: bool) -> dict[str, str | int | float]:
    values = {field: getattr(download, field) for field in _FIELDS if field != "eta"}
    values["eta"] = "-" if download.eta == timedelta.max else int(download.eta.total_seconds())
    if human_readable:
        for field in ("total_length", "completed_length", "download_speed", "upload_speed", "eta"):
            values[field] = getattr(download, f"{field}_string")()
    return values


def _validate_options(template: str, sort_fields: list[str], limit: int | None) -> None:
    if limit is not None and limit < 0:
        raise ValueError("limit must be zero or greater")
    for _, field, _, _ in Formatter().parse(template):
        if field is not None and field not in _FIELDS:
            raise ValueError(f"unknown format field {field!r}; choose from {', '.join(_FIELDS)}")
    for field in sort_fields:
        if field.removeprefix("-") not in _FIELDS:
            raise ValueError(f"unknown sort field {field!r}; choose from {', '.join(_FIELDS)}")


def list_downloads(
    api: API,
    patterns: list[str] | None = None,
    *,
    output_format: str = "name",
    sort: str | None = None,
    limit: int | None = None,
    human_readable: bool = False,
) -> int:
    """Print downloads selected by exact GIDs or case-sensitive shell-style name patterns.

    Parameters:
        api: The API instance to use.
        patterns: Select downloads matching any pattern. Omit to select all downloads.
        output_format: Use `name`, `gid`, `long`, or a Python format string with download fields.
        sort: Comma-separated field names, each optionally prefixed with `-` for descending order.
        limit: Maximum number of downloads to print after filtering and sorting. Zero prints no downloads.
        human_readable: Format sizes, speeds, and ETA with human-readable units. Otherwise use bytes, bytes per second, and seconds.

    Returns:
        Zero on success, or one for invalid formatting, sorting, or limits.
    """
    template = _FORMATS.get(output_format, output_format)
    sort_fields = sort.split(",") if sort is not None else []
    try:
        _validate_options(template, sort_fields, limit)
    except ValueError as error:
        print(f"aria2p: list: {error}", file=sys.stderr)
        return 1

    downloads = api.get_downloads()
    if patterns:
        downloads = [
            download
            for download in downloads
            if any(pattern == download.gid or fnmatchcase(download.name, pattern) for pattern in patterns)
        ]

    # Stable sorts preserve the priority of fields listed earlier and compare raw numeric values.
    for field in reversed(sort_fields):
        downloads = sorted(downloads, key=attrgetter(field.removeprefix("-")), reverse=field.startswith("-"))
    if limit is not None:
        downloads = downloads[:limit]

    try:
        # Render all rows first so an invalid format cannot leave partial output in a pipeline.
        rows = [template.format_map(_format_values(download, human_readable=human_readable)) for download in downloads]
    except (ValueError, KeyError, IndexError, AttributeError, TypeError) as error:
        print(f"aria2p: list: invalid format: {error}", file=sys.stderr)
        return 1

    if output_format == "long":
        print(_LONG_HEADER)
    for row in rows:
        print(row)
    return 0
