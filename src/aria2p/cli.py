"""
Module that contains the command line application.

Why does this file exist, and why not put this in __main__?

  You might be tempted to import things from __main__ later,
  but that will cause problems: the code will get executed twice:

  - When you run `python -maria2p` python will execute
    ``__main__.py`` as a script. That means there won't be any
    ``aria2p.__main__`` in ``sys.modules``.
  - When you import __main__ it will get executed again (as a module) because
    there's no ``aria2p.__main__`` in ``sys.modules``.

  Also see (1) from http://click.pocoo.org/5/setuptools/#setuptools-integration
"""

import argparse
import json
import sys

from .api import API
from .client import DEFAULT_HOST, DEFAULT_PORT, JSONRPCClient, JSONRPCError


# ============ MAIN FUNCTION ============ #
def main(args=None):
    """The main function, which is executed when you type ``aria2p`` or ``python -m aria2p``."""

    parser = get_parser()
    args = parser.parse_args(args=args)
    kwargs = args.__dict__

    api = API(JSONRPCClient(host=kwargs.pop("host"), port=kwargs.pop("port"), secret=kwargs.pop("secret")))

    subcommands = {
        None: subcommand_show,
        "call": subcommand_call,
        "add-magnet": subcommand_add_magnet,
        "add-torrent": subcommand_add_torrent,
        "show": subcommand_show,
    }

    subcommand = kwargs.pop("subcommand")

    try:
        return subcommands.get(subcommand)(api, **kwargs)
    except JSONRPCError as e:
        print(e.message)
        return e.code


def get_parser():
    """Return a parser for the command-line options and arguments."""
    parser = argparse.ArgumentParser()

    parser.add_argument("-p", "--port", dest="port", default=DEFAULT_PORT, type=int)
    parser.add_argument("-H", "--host", dest="host", default=DEFAULT_HOST)
    parser.add_argument("-s", "--secret", dest="secret", default="")

    subparsers = parser.add_subparsers(dest="subcommand")

    subparsers.add_parser("show", help="Show the download progression.")

    call_parser = subparsers.add_parser("call", help="Call a remote method through the JSON-RPC client.")
    call_parser.add_argument("method")
    call_parser_mxg = call_parser.add_mutually_exclusive_group()
    call_parser_mxg.add_argument("-P", "--params-list", dest="params", nargs="+")
    call_parser_mxg.add_argument("-J", "--json-params", dest="params")

    add_magnet_parser = subparsers.add_parser("add-magnet", help="Add a download with a Magnet URI.")
    add_magnet_parser.add_argument("uri")

    add_torrent_parser = subparsers.add_parser("add-torrent", help="Add a download with a Torrent file.")
    add_torrent_parser.add_argument("torrent_file")

    # sub-commands: list, add, pause, resume, stop, remove, search, info

    return parser


# ============ SHOW SUBCOMMAND ============ #
def subcommand_show(api):
    downloads = api.get_downloads()

    print(
        f"{'GID':<17} "
        f"{'STATUS':<9} "
        f"{'PROGRESS':>8} "
        f"{'DOWN_SPEED':>12} "
        f"{'UP_SPEED':>12} "
        f"{'ETA':>8}  "
        f"NAME"
    )

    for download in downloads:
        print(
            f"{download.gid:<17} "
            f"{download.status:<9} "
            f"{download.progress_string():>8} "
            f"{download.download_speed_string():>12} "
            f"{download.upload_speed_string():>12} "
            f"{download.eta_string():>8}  "
            f"{download.name}"
        )


# ============ CALL SUBCOMMAND ============ #
def subcommand_call(api, method, params):
    method = get_method(method)
    if method is None:
        print(f"Unknown method {method}. Run '{sys.argv[0]} -m listmethods' to list the available methods.")
        return 1

    if isinstance(params, str):
        params = json.loads(params)
    elif params is None:
        params = []

    response = api.client.call(method, params)
    print(json.dumps(response))

    return 0


def get_method(name, default=None):
    """Return the actual method name from a differently formatted name."""
    methods = {}
    for method in JSONRPCClient.METHODS:
        methods[method.lower()] = method
        methods[method.split(".")[1].lower()] = method
    name = name.lower()
    name = name.replace("-", "")
    name = name.replace("_", "")
    return methods.get(name, default)


# ============ ADD MAGNET SUBCOMMAND ============ #
def subcommand_add_magnet(api, uri):
    api.add_magnet(uri)
    return 0


# ============ ADD TORRENT SUBCOMMAND ============ #
def subcommand_add_torrent(api, torrent_file):
    api.add_torrent(torrent_file)
    return 0
