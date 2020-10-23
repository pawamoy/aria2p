"""
aria2p package.

Command-line tool and library to interact with an aria2c daemon process with JSON-RPC.
"""

import sys

from loguru import logger

from aria2p.api import API
from aria2p.client import Client, ClientException
from aria2p.downloads import BitTorrent, Download, File
from aria2p.options import Options
from aria2p.stats import Stats

logger.disable("aria2p")


def enable_logger(sink=sys.stderr, level="WARNING"):
    """
    Enable the logging of messages.

    Configure the `logger` variable imported from `loguru`.

    Arguments:
        sink (file): An opened file pointer, or stream handler. Default to standard error.
        level (str): The log level to use. Possible values are TRACE, DEBUG, INFO, WARNING, ERROR, CRITICAL.
            Default to WARNING.
    """
    logger.remove()
    logger.configure(handlers=[{"sink": sink, "level": level}])
    logger.enable("aria2p")


__all__ = [  # noqa: WPS410 (the only __variable__ we use)
    "API",
    "ClientException",
    "Client",
    "Download",
    "BitTorrent",
    "File",
    "Options",
    "Stats",
    "enable_logger",
]
