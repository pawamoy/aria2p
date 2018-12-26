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
from datetime import timedelta

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

    mutually_exclusive = parser.add_mutually_exclusive_group()

    rpc_group = mutually_exclusive.add_argument_group()
    rpc_group.add_argument("-m", "--method", dest="method")

    rpc_params_group = rpc_group.add_mutually_exclusive_group()
    rpc_params_group.add_argument("-p", "--params", dest="params", nargs="+")
    rpc_params_group.add_argument("-j", "--json-params", dest="json_params")

    # general_group = mutually_exclusive.add_argument_group()
    # sub-commands: list, add, pause, resume, stop, remove, search, info
    # use click?

    return parser


def main(args=None):
    """The main function, which is executed when you type ``aria2p`` or ``python -m aria2p``."""
    client = JSONRPCClient()

    parser = get_parser()
    args = parser.parse_args(args=args)

    if args.method:
        method = get_method(args.method)
        params = []
        if args.params:
            params = args.params
        elif args.json_params:
            params = json.loads(args.json_params)
        if method is None:
            print(f"Unknown method {args.method}. Run '{sys.argv[0]} -m listmethods' to list the available methods.")
            return 1
        try:
            response = client.call(method, params)
        except JSONRPCError as e:
            print(e.message)
            return e.code
        else:
            print(json.dumps(response))
        return 0

    api = API(client)

    try:
        downloads = api.get_downloads()
    except Exception as e:
        print(e)
        return 1

    print(f"{'GID':<17} "
          f"{'STATUS':<9} "
          f"{'PROGRESS':>8} "
          f"{'DOWN_SPEED':>12} "
          f"{'UP_SPEED':>12} "
          f"{'ETA':>8}  "
          f"NAME")

    for download in downloads:
        print(f"{download.gid:<17} "
              f"{download.status:<9} "
              f"{download.progress_string():>8} "
              f"{download.download_speed_string():>12} "
              f"{download.upload_speed_string():>12} "
              f"{download.eta_string():>8}  "
              f"{download.name}")

    return 0
