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

import sys
from typing import TextIO

from loguru import logger

logger.disable("aria2p")


def enable_logger(sink: str | TextIO = sys.stderr, level: str = "WARNING") -> None:
    """Enable the logging of messages.

    Configure the `logger` variable imported from `loguru`.

    Parameters:
        sink (file): An opened file pointer, or stream handler. Default to standard error.
        level (str): The log level to use. Possible values are TRACE, DEBUG, INFO, WARNING, ERROR, CRITICAL.
            Default to WARNING.
    """
    logger.remove()
    logger.configure(handlers=[{"sink": sink, "level": level}])  # ty:ignore[invalid-argument-type]
    logger.enable("aria2p")
