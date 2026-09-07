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
