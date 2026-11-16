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

"""Tests suite for `aria2p`.

CI runs the test suite against both aria2 and [aria2-next](https://github.com/AnInsomniacy/aria2-next).
aria2-next support starts at version 3.1.0. Local tests use aria2-next by default.

To test both daemons locally, install aria2 and/or aria2-next with your package manager and run:

```bash
ARIA2_ENGINE=aria2 make test
ARIA2_ENGINE=aria2-next make test
```

The tests use `aria2c` or `aria2-next` from your `PATH`.

Set `ARIA2` or `ARIA2_NEXT` to use an executable from another location.
"""

from __future__ import annotations

from pathlib import Path

TESTS_DIR = Path(__file__).parent
TESTS_TMP_DIR = TESTS_DIR / "tmp"
TESTS_DATA_DIR = TESTS_DIR / "data"
CONFIGS_DIR = TESTS_DATA_DIR / "configs"
SESSIONS_DIR = TESTS_DATA_DIR / "sessions"

BUNSENLABS_TORRENT = TESTS_DATA_DIR / "bunsenlabs-helium-4.iso.torrent"
BUNSENLABS_MAGNET = "magnet:?xt=urn:btih:7fb1b254fdbdd8863d686c7fa61b3b0b671551b1&dn=bl-Helium-4-amd64.iso"
DEBIAN_METALINK = TESTS_DATA_DIR / "download.meta4"
XUBUNTU_MIRRORS = [
    "http://ubuntutym2.u-toyama.ac.jp/xubuntu/18.04/release/xubuntu-18.04.1-desktop-amd64.iso",
    "http://ftp.free.fr/mirrors/ftp.xubuntu.com/releases/18.04/release/xubuntu-18.04.1-desktop-amd64.iso",
    "http://mirror.us.leaseweb.net/ubuntu-cdimage/xubuntu/releases/18.04/release/xubuntu-18.04.1-desktop-amd64.iso",
]

INPUT_FILES = [
    TESTS_DATA_DIR / "input_files" / "two-valid-downloads",
    TESTS_DATA_DIR / "input_files" / "one-valid-one-invalid-downloads",
    TESTS_DATA_DIR / "input_files" / "two-invalid-downloads",
]
