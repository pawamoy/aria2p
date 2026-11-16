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

# Engine identity and capabilities obtained through aria2.getVersion.

from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass(frozen=True)
class EngineCapabilities:
    """Features available through the connected engine."""

    ftp: bool
    """Whether FTP downloads are supported."""
    metalink3: bool
    """Whether Metalink 3 documents are supported."""
    control_files: bool
    """Whether resume state uses adjacent `.aria2` files."""
    move_download: bool
    """Whether the engine provides a native RPC to move unfinished downloads."""


@dataclass(frozen=True)
class Engine:
    """Identity and capabilities of a connected aria2 or aria2-next daemon."""

    name: str
    """The engine product name, either `aria2` or `aria2-next`."""
    version: str
    """The version reported by the daemon."""
    capabilities: EngineCapabilities
    """Features supported by this engine."""


def _detect_engine(version_info: dict) -> Engine:
    """Identify the daemon and reject unsupported aria2-next releases."""
    name = version_info.get("product", "aria2")
    version = version_info["version"]
    if name not in {"aria2", "aria2-next"}:
        raise ValueError(f"Unsupported engine: {name!r}")
    if name == "aria2-next":
        match = re.fullmatch(r"(\d+)\.(\d+)\.(\d+)(?:\+.*)?", version)
        if match is None or tuple(map(int, match.groups())) < (3, 1, 0):
            raise ValueError(f"aria2-next {version} is unsupported; version 3.1.0 or later is required")
    is_next = name == "aria2-next"
    return Engine(
        name,
        version,
        EngineCapabilities(ftp=not is_next, metalink3=not is_next, control_files=not is_next, move_download=is_next),
    )


# These aria2 options are ignored or absent in aria2-next 3.1.0. Keep the list
# explicit so a successful RPC cannot silently discard a caller's settings.
# https://github.com/AnInsomniacy/aria2-next/blob/v3.1.0/src/options/Options.cc
# https://github.com/AnInsomniacy/aria2-next/blob/v3.1.0/src/options/Catalog.cc
_NEXT_UNSUPPORTED_OPTIONS = frozenset(
    {
        "allow-piece-length-change",
        "always-resume",
        "async-dns",
        "bt-enable-hook-after-hash-check",
        "bt-hash-check-seed",
        "bt-load-saved-metadata",
        "bt-max-open-files",
        "bt-metadata-only",
        "bt-min-crypto-level",
        "bt-prioritize-piece",
        "bt-remove-unselected-file",
        "bt-request-peer-speed-limit",
        "bt-save-metadata",
        "bt-stop-timeout",
        "bt-tracker-connect-timeout",
        "bt-tracker-interval",
        "bt-tracker-timeout",
        "conditional-get",
        "content-disposition-default-utf8",
        "enable-http-pipelining",
        "enable-mmap",
        "ftp-passwd",
        "ftp-pasv",
        "ftp-proxy",
        "ftp-proxy-passwd",
        "ftp-proxy-user",
        "ftp-reuse-connection",
        "ftp-type",
        "ftp-user",
        "http-auth-challenge",
        "max-mmap-limit",
        "max-resume-failure-tries",
        "metalink-base-uri",
        "metalink-enable-unique-protocol",
        "metalink-language",
        "metalink-location",
        "metalink-os",
        "metalink-preferred-protocol",
        "metalink-version",
        "no-file-allocation-limit",
        "optimize-concurrent-downloads",
        "parameterized-uri",
        "piece-length",
        "proxy-method",
        "realtime-chunk-checksum",
        "reuse-uri",
        "server-stat-of",
        "ssh-host-key-md",
        "stream-piece-selector",
        "uri-selector",
        "use-head",
    }
)
