"""aria2p package.

Command-line tool and library to interact with an aria2c daemon process with JSON-RPC.
"""

from __future__ import annotations

import sys
from typing import TextIO

from loguru import logger

from aria2p.api import API, AsyncAPI
from aria2p.client import Client, AsyncClient, ClientException
from aria2p.downloads import BitTorrent, Download, AsyncDownload, File
from aria2p.options import SyncOptions, AsyncOptions
from aria2p.stats import Stats

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
    logger.configure(handlers=[{"sink": sink, "level": level}])
    logger.enable("aria2p")


__all__ = [
    "API",
    "AsyncAPI",
    "ClientException",
    "Client",
    "AsyncClient",
    "Download",
    "AsyncDownload",
    "BitTorrent",
    "File",
    "SyncOptions",
    "AsyncOptions",
    "Stats",
    "enable_logger",
]
