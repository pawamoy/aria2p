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
        try:
            response = client.call(method, params)
        except JSONRPCError as e:
            print(e.message)
            sys.exit(e.code)
        else:
            print(json.dumps(response))
        return 0

    api = API(client)
    downloads = api.get_downloads()

    for download in downloads:
        total = int(download.total_length)
        completed = int(download.completed_length)
        download_speed = int(download.download_speed)
        if total == 0:
            progress = "?"
        else:
            progress = "%.2f%%" % (completed / total * 100)
        if download_speed > 0:
            eta = str(timedelta(seconds=int((total - completed) / download_speed)))
        else:
            eta = "-"
        unit = 'B/s'
        for u in ('kB/s', 'MB/s'):
            if download_speed > 1000:
                download_speed /= 1024
                unit = u
        download_speed = "%.2f " % download_speed + unit
        print(f"{download.gid} {download.status:<8} {progress:<8} {download_speed:<12} {eta:<12} {download.name}")

    return 0
