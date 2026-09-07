"""aria2p package.

Command-line tool and library to interact with an aria2c daemon process with JSON-RPC.
"""

from __future__ import annotations

from aria2p._internal.api import API
from aria2p._internal.cli.main import main
from aria2p._internal.client import (
    JSONRPC_CODES,
    JSONRPC_INTERNAL_ERROR,
    JSONRPC_INVALID_PARAMS,
    JSONRPC_INVALID_REQUEST,
    JSONRPC_METHOD_NOT_FOUND,
    JSONRPC_PARSER_ERROR,
    Client,
    ClientException,
)
from aria2p._internal.downloads import BitTorrent, Download, File
from aria2p._internal.logger import enable_logger
from aria2p._internal.options import Options
from aria2p._internal.stats import Stats

__all__ = [
    "API",
    "JSONRPC_CODES",
    "JSONRPC_INTERNAL_ERROR",
    "JSONRPC_INVALID_PARAMS",
    "JSONRPC_INVALID_REQUEST",
    "JSONRPC_METHOD_NOT_FOUND",
    "JSONRPC_PARSER_ERROR",
    "BitTorrent",
    "Client",
    "ClientException",
    "Download",
    "File",
    "Options",
    "Stats",
    "enable_logger",
    "main",
]
