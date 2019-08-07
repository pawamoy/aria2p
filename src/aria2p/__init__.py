"""
aria2p package.

This package provides a command-line tool and a Python library to interact
with an ``aria2c`` daemon process through JSON-RPC.

If you read this message, you probably want to learn about the library and not the command-line tool:
please refer to the README.md included in this package to get the link to the official documentation.
"""

from loguru import logger

from .api import API
from .client import Client, ClientException
from .downloads import BitTorrent, Download, File
from .options import Options
from .stats import Stats

logger.disable("aria2p")

__all__ = ["API", "ClientException", "Client", "Download", "BitTorrent", "File", "Options", "Stats"]

# TODO: use proper logging messages (esp. in except: pass)
# TODO: maybe add type annotations
# TODO: handle both str and pathlib.Path for paths consistently
# TODO: add command "add" for normal downloads!!
# TODO: add "--options" options for "add" commands
# TODO: in API, support download arguments to be both Download or str (GID)?
# TODO: add clean parameter for api.move_files method (to clean .aria2 files)
# TODO: add value verification for options (see man page)

# Roadmap:
# - feature: Ability to hide metadata downloads (magnet URIs)
# - feature: Ability to move files to another directory
# - feature: Ability to tag downloads with markers (like categories)
# - feature: Ability to execute instructions on events (download completed, etc.)
# - feature: Improved queue
# - feature: Interactive display (htop-style) with sorting, filtering and actions
# - feature: Ability to search current downloads with patterns and filters on fields
