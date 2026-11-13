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

# Validate options accepted by aria2's RPC methods.
#
# The option names, scopes, and value rules follow the aria2 1.37 manual:
# https://aria2.github.io/manual/en/html/aria2c.html#input-file
# https://aria2.github.io/manual/en/html/aria2c.html#methods
#
# Keep the initial-download list separate from the change-option exceptions:
# some options can only be supplied when a download is created. Validation does
# not inspect paths on the client, because the daemon may run on another host.

from __future__ import annotations

import math
import re
from ipaddress import ip_address
from typing import TYPE_CHECKING
from urllib.parse import urlsplit

if TYPE_CHECKING:
    from typing import Literal

# Values are strings on the wire, except for repeatable header and index-out values.
_RPCValue = str | list[str]

_INITIAL_OPTIONS = frozenset({
    "all-proxy",
    "all-proxy-passwd",
    "all-proxy-user",
    "allow-overwrite",
    "allow-piece-length-change",
    "always-resume",
    "async-dns",
    "auto-file-renaming",
    "bt-enable-hook-after-hash-check",
    "bt-enable-lpd",
    "bt-exclude-tracker",
    "bt-external-ip",
    "bt-force-encryption",
    "bt-hash-check-seed",
    "bt-load-saved-metadata",
    "bt-max-peers",
    "bt-metadata-only",
    "bt-min-crypto-level",
    "bt-prioritize-piece",
    "bt-remove-unselected-file",
    "bt-request-peer-speed-limit",
    "bt-require-crypto",
    "bt-save-metadata",
    "bt-seed-unverified",
    "bt-stop-timeout",
    "bt-tracker",
    "bt-tracker-connect-timeout",
    "bt-tracker-interval",
    "bt-tracker-timeout",
    "check-integrity",
    "checksum",
    "conditional-get",
    "connect-timeout",
    "content-disposition-default-utf8",
    "continue",
    "dir",
    "dry-run",
    "enable-http-keep-alive",
    "enable-http-pipelining",
    "enable-mmap",
    "enable-peer-exchange",
    "file-allocation",
    "follow-metalink",
    "follow-torrent",
    "force-save",
    "ftp-passwd",
    "ftp-pasv",
    "ftp-proxy",
    "ftp-proxy-passwd",
    "ftp-proxy-user",
    "ftp-reuse-connection",
    "ftp-type",
    "ftp-user",
    "gid",
    "hash-check-only",
    "header",
    "http-accept-gzip",
    "http-auth-challenge",
    "http-no-cache",
    "http-passwd",
    "http-proxy",
    "http-proxy-passwd",
    "http-proxy-user",
    "http-user",
    "https-proxy",
    "https-proxy-passwd",
    "https-proxy-user",
    "index-out",
    "lowest-speed-limit",
    "max-connection-per-server",
    "max-download-limit",
    "max-file-not-found",
    "max-mmap-limit",
    "max-resume-failure-tries",
    "max-tries",
    "max-upload-limit",
    "metalink-base-uri",
    "metalink-enable-unique-protocol",
    "metalink-language",
    "metalink-location",
    "metalink-os",
    "metalink-preferred-protocol",
    "metalink-version",
    "min-split-size",
    "no-file-allocation-limit",
    "no-netrc",
    "no-proxy",
    "out",
    "parameterized-uri",
    "pause",
    "pause-metadata",
    "piece-length",
    "proxy-method",
    "realtime-chunk-checksum",
    "referer",
    "remote-time",
    "remove-control-file",
    "retry-wait",
    "reuse-uri",
    "rpc-save-upload-metadata",
    "seed-ratio",
    "seed-time",
    "select-file",
    "split",
    "ssh-host-key-md",
    "stream-piece-selector",
    "timeout",
    "uri-selector",
    "use-head",
    "user-agent",
})

_GLOBAL_ONLY_OPTIONS = frozenset({
    "bt-max-open-files",
    "download-result",
    "keep-unfinished-download-result",
    "log",
    "log-level",
    "max-concurrent-downloads",
    "max-download-result",
    "max-overall-download-limit",
    "max-overall-upload-limit",
    "optimize-concurrent-downloads",
    "save-cookies",
    "save-session",
    "server-stat-of",
})

_GLOBAL_OPTIONS = (_INITIAL_OPTIONS | _GLOBAL_ONLY_OPTIONS) - {"checksum", "index-out", "out", "pause", "select-file"}
_DOWNLOAD_OPTIONS = _INITIAL_OPTIONS - {"dry-run", "metalink-base-uri", "parameterized-uri", "pause", "piece-length", "rpc-save-upload-metadata"}

_BOOLEAN_OPTIONS = frozenset({
    "allow-overwrite",
    "allow-piece-length-change",
    "always-resume",
    "async-dns",
    "auto-file-renaming",
    "bt-enable-hook-after-hash-check",
    "bt-enable-lpd",
    "bt-force-encryption",
    "bt-hash-check-seed",
    "bt-load-saved-metadata",
    "bt-metadata-only",
    "bt-remove-unselected-file",
    "bt-require-crypto",
    "bt-save-metadata",
    "bt-seed-unverified",
    "check-integrity",
    "conditional-get",
    "content-disposition-default-utf8",
    "continue",
    "dry-run",
    "enable-http-keep-alive",
    "enable-http-pipelining",
    "enable-mmap",
    "enable-peer-exchange",
    "force-save",
    "ftp-pasv",
    "ftp-reuse-connection",
    "hash-check-only",
    "http-accept-gzip",
    "http-auth-challenge",
    "http-no-cache",
    "keep-unfinished-download-result",
    "metalink-enable-unique-protocol",
    "no-netrc",
    "parameterized-uri",
    "pause",
    "pause-metadata",
    "realtime-chunk-checksum",
    "remote-time",
    "remove-control-file",
    "reuse-uri",
    "rpc-save-upload-metadata",
    "use-head",
})

_CHOICES = {
    "bt-min-crypto-level": ("plain", "arc4"),
    "download-result": ("default", "full", "hide"),
    "file-allocation": ("none", "prealloc", "trunc", "falloc"),
    "follow-metalink": ("true", "mem", "false"),
    "follow-torrent": ("true", "mem", "false"),
    "ftp-type": ("binary", "ascii"),
    "log-level": ("debug", "info", "notice", "warn", "error"),
    "metalink-preferred-protocol": ("http", "https", "ftp", "none"),
    "proxy-method": ("get", "tunnel"),
    "stream-piece-selector": ("default", "inorder", "random", "geom"),
    "uri-selector": ("inorder", "feedback", "adaptive"),
}

# Unbounded numeric options use aria2's signed 64-bit parser.
_INTEGER_RANGES = {
    "bt-max-open-files": (1, 2**63 - 1),
    "bt-max-peers": (0, 2**63 - 1),
    "bt-stop-timeout": (0, 2**63 - 1),
    "bt-tracker-connect-timeout": (1, 600),
    "bt-tracker-interval": (0, 2**63 - 1),
    "bt-tracker-timeout": (1, 600),
    "connect-timeout": (1, 600),
    "max-concurrent-downloads": (1, 2**63 - 1),
    "max-connection-per-server": (1, 16),
    "max-download-result": (0, 2**63 - 1),
    "max-file-not-found": (0, 2**63 - 1),
    "max-resume-failure-tries": (0, 2**63 - 1),
    "max-tries": (0, 2**63 - 1),
    "retry-wait": (0, 600),
    "split": (1, 2**63 - 1),
    "timeout": (1, 600),
}

_SIZE_OPTIONS = frozenset({
    "bt-request-peer-speed-limit",
    "lowest-speed-limit",
    "max-download-limit",
    "max-mmap-limit",
    "max-overall-download-limit",
    "max-overall-upload-limit",
    "max-upload-limit",
    "min-split-size",
    "no-file-allocation-limit",
    "piece-length",
})


def _size(value: str) -> int:
    """Parse aria2's binary K and M size suffixes."""
    match = re.fullmatch(r"([0-9]+)([KMkm]?)", value)
    if match is None:
        raise ValueError("expected a nonnegative integer with an optional K or M suffix")
    return int(match[1]) * {"": 1, "K": 1024, "M": 1024**2}[match[2].upper()]


def _validate_value(key: str, value: str) -> None:
    """Check a serialized scalar value against the option's rules."""
    if key in _BOOLEAN_OPTIONS:
        if value not in {"true", "false"}:
            raise ValueError("expected true or false")
    elif key in _CHOICES:
        if value not in _CHOICES[key]:
            raise ValueError(f"expected one of {', '.join(_CHOICES[key])}")
    elif key in _INTEGER_RANGES:
        lower, upper = _INTEGER_RANGES[key]
        if re.fullmatch(r"[0-9]+", value) is None or not lower <= int(value) <= upper:
            raise ValueError(f"expected an integer between {lower} and {upper}")
    elif key in _SIZE_OPTIONS:
        lower, upper = (1024**2, 1024**3) if key in {"min-split-size", "piece-length"} else (0, 2**63 - 1)
        if not lower <= _size(value) <= upper:
            raise ValueError(f"expected a size between {lower} and {upper} bytes")
    elif key in {"seed-ratio", "seed-time"}:
        number = float(value)
        if not math.isfinite(number) or number < 0:
            raise ValueError("expected a finite nonnegative number")
    elif key == "gid":
        if re.fullmatch(r"[0-9a-fA-F]{16}", value) is None or int(value, 16) == 0:
            raise ValueError("expected a nonzero 16-character hexadecimal GID")
    elif key in {"checksum", "ssh-host-key-md"}:
        # Supported hash algorithms depend on the daemon's build. Check the
        # syntax here and leave algorithm availability to the daemon.
        if re.fullmatch(r"[a-zA-Z0-9-]+=[0-9a-fA-F]+", value) is None:
            raise ValueError("expected HASH_TYPE=HEX_DIGEST")
    elif key == "select-file":
        for part in value.split(","):
            match = re.fullmatch(r"([0-9]+)(?:-([0-9]+))?", part)
            if match is None or not 1 <= int(match[1]) <= int(match[2] or match[1]) <= 2**20:
                raise ValueError("expected file indexes or ranges between 1 and 1048576")
    elif key == "index-out":
        if re.fullmatch(r"[0-9]+=.+", value) is None or int(value.partition("=")[0]) < 1:
            raise ValueError("expected INDEX=PATH with a positive index")
    elif key == "bt-prioritize-piece":
        for part in value.split(","):
            name, separator, size = part.partition("=")
            if name not in {"head", "tail"}:
                raise ValueError("expected head[=SIZE] or tail[=SIZE]")
            if separator:
                _size(size)
    elif key == "optimize-concurrent-downloads":
        if value not in {"true", "false"}:
            parts = value.split(":")
            if len(parts) != 2 or any(not math.isfinite(float(part)) or float(part) < 0 for part in parts):  # noqa: PLR2004
                raise ValueError("expected true, false, or two nonnegative numbers A:B")
    elif key == "bt-external-ip" and value:
        ip_address(value)
    elif key in {"all-proxy", "http-proxy", "https-proxy", "ftp-proxy"} and value:
        proxy = urlsplit(value if "://" in value else f"http://{value}")
        if proxy.scheme != "http" or not proxy.hostname or any(char.isspace() for char in value):
            raise ValueError("expected an HTTP proxy URL")
        # Accessing port also checks its syntax and range.
        if proxy.port == 0:
            raise ValueError("expected a positive proxy port")


def _validate_options(options: dict, scope: Literal["initial", "global", "download"]) -> dict[str, _RPCValue]:
    """Return validated RPC values without changing the caller's dictionary.

    Raise ValueError for unknown names, options unavailable in the requested
    scope, unsupported Python types, or invalid values. Validate the entire
    dictionary before the caller sends any RPC requests.
    """
    allowed = {"initial": _INITIAL_OPTIONS, "global": _GLOBAL_OPTIONS, "download": _DOWNLOAD_OPTIONS}[scope]
    result: dict[str, _RPCValue] = {}
    for key, value in options.items():
        if not isinstance(key, str) or key not in allowed:
            raise ValueError(f"Unknown or unavailable option {key!r} for {scope} options")
        if isinstance(value, list):
            if key not in {"header", "index-out"} or any(not isinstance(item, str) for item in value):
                raise ValueError(f"Invalid value for option {key!r}: only header and index-out accept lists of strings")
        elif not isinstance(value, (str, int, float, bool)):
            raise ValueError(f"Invalid value for option {key!r}: expected a string, number, or boolean")  # noqa: TRY004
        try:
            if isinstance(value, list):
                for item in value:
                    _validate_value(key, item)
                result[key] = value.copy()
            else:
                serialized = str(value).lower() if isinstance(value, bool) else str(value)
                _validate_value(key, serialized)
                result[key] = serialized
        except ValueError:
            # Do not echo values: options can contain credentials.
            raise ValueError(f"Invalid value for option {key!r}") from None
    return result
