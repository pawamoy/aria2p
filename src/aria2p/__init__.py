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

"""aria2p package.

Command-line tool and library to interact with an aria2c daemon process with JSON-RPC.
"""

from __future__ import annotations

from aria2p._internal.api import API, InputFileContentsType, OperationResult, OptionsType
from aria2p._internal.cli.commands.add import add
from aria2p._internal.cli.commands.add_magnet import add_magnets
from aria2p._internal.cli.commands.add_metalink import add_metalinks
from aria2p._internal.cli.commands.add_torrent import add_torrents
from aria2p._internal.cli.commands.call import call, get_method
from aria2p._internal.cli.commands.listen import listen
from aria2p._internal.cli.commands.pause import pause
from aria2p._internal.cli.commands.purge import purge
from aria2p._internal.cli.commands.remove import remove
from aria2p._internal.cli.commands.resume import resume
from aria2p._internal.cli.commands.show import show
from aria2p._internal.cli.commands.top import top
from aria2p._internal.cli.main import commands, main
from aria2p._internal.cli.parser import check_args, get_parser, parse_options_string
from aria2p._internal.client import (
    DEFAULT_HOST,
    DEFAULT_ID,
    DEFAULT_PORT,
    DEFAULT_TIMEOUT,
    JSONRPC_CODES,
    JSONRPC_INTERNAL_ERROR,
    JSONRPC_INVALID_PARAMS,
    JSONRPC_INVALID_REQUEST,
    JSONRPC_METHOD_NOT_FOUND,
    JSONRPC_PARSER_ERROR,
    NOTIFICATION_BT_COMPLETE,
    NOTIFICATION_COMPLETE,
    NOTIFICATION_ERROR,
    NOTIFICATION_PAUSE,
    NOTIFICATION_START,
    NOTIFICATION_STOP,
    NOTIFICATION_TYPES,
    CallReturnType,
    CallsType,
    Client,
    ClientException,
    Multicalls2Type,
    Notification,
)
from aria2p._internal.downloads import BitTorrent, Download, File
from aria2p._internal.interface import (
    Column,
    Exit,
    HorizontalScroll,
    Interface,
    Key,
    Keys,
    Palette,
    color_palette_parser,
    configs,
    key_bind_parser,
)
from aria2p._internal.logger import enable_logger
from aria2p._internal.options import Options, OptionType
from aria2p._internal.stats import Stats
from aria2p._internal.utils import (
    SignalHandler,
    bool_or_value,
    bool_to_str,
    get_version,
    human_readable_bytes,
    human_readable_timedelta,
    load_configuration,
    read_lines,
)

__all__ = [
    "API",
    "DEFAULT_HOST",
    "DEFAULT_ID",
    "DEFAULT_PORT",
    "DEFAULT_TIMEOUT",
    "JSONRPC_CODES",
    "JSONRPC_INTERNAL_ERROR",
    "JSONRPC_INVALID_PARAMS",
    "JSONRPC_INVALID_REQUEST",
    "JSONRPC_METHOD_NOT_FOUND",
    "JSONRPC_PARSER_ERROR",
    "NOTIFICATION_BT_COMPLETE",
    "NOTIFICATION_COMPLETE",
    "NOTIFICATION_ERROR",
    "NOTIFICATION_PAUSE",
    "NOTIFICATION_START",
    "NOTIFICATION_STOP",
    "NOTIFICATION_TYPES",
    "BitTorrent",
    "CallReturnType",
    "CallsType",
    "Client",
    "ClientException",
    "Column",
    "Download",
    "Exit",
    "File",
    "HorizontalScroll",
    "InputFileContentsType",
    "Interface",
    "Key",
    "Keys",
    "Multicalls2Type",
    "Notification",
    "OperationResult",
    "OptionType",
    "Options",
    "OptionsType",
    "Palette",
    "SignalHandler",
    "Stats",
    "add",
    "add_magnets",
    "add_metalinks",
    "add_torrents",
    "bool_or_value",
    "bool_to_str",
    "call",
    "check_args",
    "color_palette_parser",
    "commands",
    "configs",
    "enable_logger",
    "get_method",
    "get_parser",
    "get_version",
    "human_readable_bytes",
    "human_readable_timedelta",
    "key_bind_parser",
    "listen",
    "load_configuration",
    "main",
    "parse_options_string",
    "pause",
    "purge",
    "read_lines",
    "remove",
    "resume",
    "show",
    "top",
]
