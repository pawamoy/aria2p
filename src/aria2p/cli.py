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
from .client import JSONRPCClient, JSONRPCError


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


def get_parser():
    """Return a parser for the command-line options and arguments."""
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="subcommand")

    call_parser = subparsers.add_parser("call", help="Call a remote method through the JSON-RPC client.")

    call_parser.add_argument("method")

    call_parser_mxg = call_parser.add_mutually_exclusive_group()
    call_parser_mxg.add_argument("-p", "--params", dest="params", nargs="+")
    call_parser_mxg.add_argument("-j", "--json-params", dest="json_params")

    add_magnet_parser = subparsers.add_parser("add-magnet", help="Add a download with a Magnet URI.")
    add_magnet_parser.add_argument("uri")

    add_torrent_parser = subparsers.add_parser("add-torrent", help="Add a download with a Torrent file.")
    add_torrent_parser.add_argument("torrent_file")

    # sub-commands: list, add, pause, resume, stop, remove, search, info

    return parser


def main(args=None):
    """The main function, which is executed when you type ``aria2p`` or ``python -m aria2p``."""
    client = JSONRPCClient()
    api = API(client)

    parser = get_parser()
    args = parser.parse_args(args=args)

    try:

        if args.subcommand == "call":

            method = get_method(args.method)
            if method is None:
                print(
                    f"Unknown method {args.method}. Run '{sys.argv[0]} -m listmethods' to list the available methods."
                )
                return 1

            params = []
            if args.params:
                params = args.params
            elif args.json_params:
                params = json.loads(args.json_params)

            response = client.call(method, params)
            print(json.dumps(response))

            return 0

        elif args.subcommand == "add-magnet":
            api.add_magnet(args.uri)

        elif args.subcommand == "add-torrent":
            api.add_torrent(args.torrent_file)

        else:
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

    except JSONRPCError as e:
        print(e.message)
        return e.code

    return 0
