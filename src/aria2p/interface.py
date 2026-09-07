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

"""Deprecated."""

# YORE: Bump 2: Remove file.

import warnings
from typing import Any

from aria2p._internal import interface as _interface


def __getattr__(name: str) -> Any:
    warnings.warn(
        "Names in `aria2p.interface` are deprecated and will become private in a future release.",
        DeprecationWarning,
        stacklevel=2,
    )
    try:
        return getattr(_interface, name)
    except AttributeError:
        return getattr(_interface, f"_{name}")
