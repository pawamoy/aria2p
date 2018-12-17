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
from .client import JSONRPCClient


def get_method(name, default=None):
    methods = {}
    for method in JSONRPCClient.METHODS:
        methods[method.lower()] = method
        methods[method.split(".")[1].lower()] = method
    name = name.lower()
    name = name.replace("-", "")
    name = name.replace("_", "")
    return methods.get(name, default)


def get_parser():
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
            sys.exit(1)
        print(json.dumps(client.call(method, params)))
        return 0

    api = API(client)
    downloads = api.get_downloads()

    for download in downloads:
        if float(download.total_length) == 0.0:
            progress = "?"
        else:
            progress = "%.2f%%" % (float(download.completed_length) / float(download.total_length) * 100)
        print(f"{download.gid} {download.status:<8} {progress:<8} {download.name}")

    return 0
