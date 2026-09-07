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

"""Fake HTTP server."""

from __future__ import annotations

from typing import TYPE_CHECKING

from fastapi import FastAPI
from fastapi.responses import StreamingResponse

if TYPE_CHECKING:
    from collections.abc import AsyncIterator


def translate_size(size: str) -> int:
    try:
        return int(size)
    except ValueError:
        pass
    size = size.lower()
    if size.endswith("k"):
        multiplier = 2**10
    elif size.endswith("m"):
        multiplier = 2**20
    elif size.endswith("g"):
        multiplier = 2**30
    else:
        raise ValueError("size unit not supported:", size)
    return int(size.rstrip("kmg")) * multiplier


async def virtual_file(size: int, chunks: int = 4096) -> AsyncIterator[bytes]:
    while size > 0:
        yield b"1" * min(size, chunks)
        size -= chunks


app = FastAPI()


@app.get("/{size}")
async def get(size: str) -> StreamingResponse:
    return StreamingResponse(
        virtual_file(translate_size(size)),
        media_type="application/octet-stream",
    )
