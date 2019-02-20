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

import requests
from aria2p import Download

from .api import API
from .client import DEFAULT_HOST, DEFAULT_PORT, Client, ClientException


# ============ MAIN FUNCTION ============ #
def main(args=None):
    """The main function, which is executed when you type ``aria2p`` or ``python -m aria2p``."""

    parser = get_parser()
    args = parser.parse_args(args=args)
    kwargs = args.__dict__

    api = API(Client(host=kwargs.pop("host"), port=kwargs.pop("port"), secret=kwargs.pop("secret")))

    # Warn if no aria2 daemon process seems to be running
    try:
        api.client.get_version()
    except requests.ConnectionError as e:
        print(f"[ERROR] {e}", file=sys.stderr)
        print(file=sys.stderr)
        print("Please make sure that an instance of aria2c is running with RPC mode enabled,", file=sys.stderr)
        print("and that you have provided the right host, port and secret token.", file=sys.stderr)
        print("More information at https://aria2p.readthedocs.io/en/latest.", file=sys.stderr)
        return 2

    subcommands = {
        None: subcommand_show,
        "show": subcommand_show,
        "call": subcommand_call,
        "add-magnet": subcommand_add_magnet,
        "add-torrent": subcommand_add_torrent,
        "add-metalink": subcommand_add_metalink,
        "pause": subcommand_pause,
        "pause-all": subcommand_pause_all,
        "resume": subcommand_resume,
        "resume-all": subcommand_resume_all,
        "remove": subcommand_remove,
        "remove-all": subcommand_remove_all,
        "purge": subcommand_purge,
        "autopurge": subcommand_autopurge,
    }

    subcommand = kwargs.pop("subcommand")

    try:
        return subcommands.get(subcommand)(api, **kwargs)
    except ClientException as e:
        print(e.message)
        return e.code


def get_parser():
    """Return a parser for the command-line options and arguments."""
    usage = "%(prog)s [GLOBAL_OPTS...] COMMAND [COMMAND_OPTS...]"
    description = "Command-line tool and Python library to interact with an `aria2c` daemon process through JSON-RPC."
    parser = argparse.ArgumentParser(add_help=False, usage=usage, description=description, prog="aria2p")

    main_help = "Show this help message and exit. Commands also accept the -h/--help option."
    subcommand_help = "Show this help message and exit."

    global_options = parser.add_argument_group(title="Global options")
    global_options.add_argument("-h", "--help", action="help", help=main_help)

    global_options.add_argument(
        "-p", "--port", dest="port", default=DEFAULT_PORT, type=int, help="Port to use to connect to the remote server."
    )
    global_options.add_argument(
        "-H", "--host", dest="host", default=DEFAULT_HOST, help="Host address for the remote server."
    )
    global_options.add_argument(
        "-s", "--secret", dest="secret", default="", help="Secret token to use to connect to the remote server."
    )

    # ========= SUBPARSERS ========= #
    subparsers = parser.add_subparsers(dest="subcommand", title="Commands", metavar="", prog="aria2p")

    def subparser(command, text, **kwargs):
        p = subparsers.add_parser(command, add_help=False, help=text, description=text, **kwargs)
        p.add_argument("-h", "--help", action="help", help=subcommand_help)
        return p

    add_magnet_parser = subparser("add-magnet", "Add a download with a Magnet URI.")
    add_metalink_parser = subparser("add-metalink", "Add a download with a Metalink file.")
    add_torrent_parser = subparser("add-torrent", "Add a download with a Torrent file.")
    subparser("autopurge", "Automatically purge completed/removed/failed downloads.", aliases=["autoclear"])
    call_parser = subparser("call", "Call a remote method through the JSON-RPC client.")
    pause_parser = subparser("pause", "Pause downloads.")
    purge_parser = subparser("purge", "Purge downloads.", aliases=["clear"])
    pause_all_parser = subparser("pause-all", "Pause all downloads.")
    remove_parser = subparser("remove", "Remove downloads.", aliases=["rm"])
    remove_all_parser = subparser("remove-all", "Remove all downloads.")
    resume_parser = subparser("resume", "Resume downloads.")
    subparser("resume-all", "Resume all downloads.")
    subparser("show", "Show the download progression.")

    # ========= CALL PARSER ========= #
    call_parser.add_argument(
        "method",
        help=(
            "The method to call (case insensitive). "
            "Dashes and underscores will be removed so you can use as many as you want, or none. "
            "Prefixes like 'aria2.' or 'system.' are also optional."
        ),
    )
    call_parser_mxg = call_parser.add_mutually_exclusive_group()
    call_parser_mxg.add_argument(
        "-P", "--params-list", dest="params", nargs="+", help="Parameters as a list of strings."
    )
    call_parser_mxg.add_argument(
        "-J",
        "--json-params",
        dest="params",
        help="Parameters as a JSON string. You should always wrap it at least once in an array '[]'.",
    )

    # ========= ADD MAGNET PARSER ========= #
    add_magnet_parser.add_argument("uri", help="The magnet URI to use.")

    # ========= ADD TORRENT PARSER ========= #
    add_torrent_parser.add_argument("torrent_file", help="The path to the torrent file.")

    # ========= ADD METALINK PARSER ========= #
    add_metalink_parser.add_argument("metalink_file", help="The path to the metalink file.")

    # ========= PAUSE PARSER ========= #
    pause_parser.add_argument("gids", nargs="+", help="The GIDs of the downloads to pause.")
    pause_parser.add_argument(
        "-f", "--force", dest="force", action="store_true", help="Pause without contacting servers first."
    )

    # ========= PAUSE ALL PARSER ========= #
    pause_all_parser.add_argument(
        "-f", "--force", dest="force", action="store_true", help="Pause without contacting servers first."
    )

    # ========= RESUME PARSER ========= #
    resume_parser.add_argument("gids", nargs="+", help="The GIDs of the downloads to resume.")

    # ========= REMOVE PARSER ========= #
    remove_parser.add_argument("gids", nargs="+", help="The GIDs of the downloads to remove.")
    remove_parser.add_argument(
        "-f", "--force", dest="force", action="store_true", help="Remove without contacting servers first."
    )

    # ========= REMOVE ALL PARSER ========= #
    remove_all_parser.add_argument(
        "-f", "--force", dest="force", action="store_true", help="Remove without contacting servers first."
    )

    # ========= PURGE PARSER ========= #
    purge_parser.add_argument("gids", nargs="*", help="The GIDs of the downloads to purge.")

    # TODO: when API is ready
    # info_parser = subparsers.add_parser("info", help="Show information about downloads.")
    # info_parser_mxg = info_parser.add_mutually_exclusive_group()
    # info_parser_mxg.add_argument("gids", nargs="+")
    # info_parser_mxg.add_argument("-a", "--all", dest="select_all", action="store_true")
    # TODO: add --format, --fields

    # TODO: when API is ready
    # list_parser = subparsers.add_parser("list", help="List downloads.", aliases=["ls"])
    # list_parser.add_argument("-f", "--format", dest="format")
    # list_parser.add_argument("-s", "--sort", dest="sort")
    # TODO: add --hide-metadata

    # TODO: when API is ready
    # search_parser = subparsers.add_parser("search", help="Search downloads using patterns or regular expressions.")
    # search_parser.add_argument("-L", "--literal", dest="literal", action="store_true")

    # TODO: add options (--set), stats, move-files, save-session, shutdown

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
        print(f"[ERROR] call: Unknown method {method}.", file=sys.stderr)
        print(file=sys.stderr)
        print("Run '{sys.argv[0]} -m listmethods' to list the available methods.", file=sys.stderr)
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
    for method in Client.METHODS:
        methods[method.lower()] = method
        methods[method.split(".")[1].lower()] = method
    name = name.lower()
    name = name.replace("-", "")
    name = name.replace("_", "")
    return methods.get(name, default)


# ============ ADD MAGNET SUBCOMMAND ============ #
def subcommand_add_magnet(api, uri):
    new_download = api.add_magnet(uri)
    print(f"Created download {new_download.gid}")
    return 0


# ============ ADD TORRENT SUBCOMMAND ============ #
def subcommand_add_torrent(api, torrent_file):
    new_download = api.add_torrent(torrent_file)
    print(f"Created download {new_download.gid}")
    return 0


# ============ ADD METALINK SUBCOMMAND ============ #
def subcommand_add_metalink(api: API, metalink_file):
    new_download = api.add_metalink(metalink_file)
    print(f"Created download {new_download.gid}")
    return 0


# ============ PAUSE SUBCOMMAND ============ #
def subcommand_pause(api: API, gids, force=False):
    downloads = [Download(api, {"gid": gid}) for gid in gids]
    result = api.pause(downloads, force=force)
    if all(result):
        return 0
    for item in result:
        if isinstance(item, ClientException):
            print(item)
    return 1


# ============ PAUSE ALL SUBCOMMAND ============ #
def subcommand_pause_all(api: API, force=False):
    if api.pause_all(force=force):
        return 0
    return 1


# ============ RESUME SUBCOMMAND ============ #
def subcommand_resume(api: API, gids):
    downloads = [Download(api, {"gid": gid}) for gid in gids]
    result = api.resume(downloads)
    if all(result):
        return 0
    for item in result:
        if isinstance(item, ClientException):
            print(item)
    return 1


# ============ RESUME ALL SUBCOMMAND ============ #
def subcommand_resume_all(api: API):
    if api.resume_all():
        return 0
    return 1


# ============ REMOVE SUBCOMMAND ============ #
def subcommand_remove(api: API, gids, force=False):
    downloads = [Download(api, {"gid": gid}) for gid in gids]
    result = api.remove(downloads, force=force)
    if all(result):
        return 0
    for item in result:
        if isinstance(item, ClientException):
            print(item)
    return 1


# ============ REMOVE ALL SUBCOMMAND ============ #
def subcommand_remove_all(api: API, force=False):
    if api.remove_all(force=force):
        return 0
    return 1


# ============ PURGE SUBCOMMAND ============ #
def subcommand_purge(api: API, gids):
    downloads = [Download(api, {"gid": gid}) for gid in gids]
    result = api.purge(downloads)
    if all(result):
        return 0
    for item in result:
        if isinstance(item, ClientException):
            print(item)
    return 1


# ============ AUTOPURGE SUBCOMMAND ============ #
def subcommand_autopurge(api: API):
    if api.autopurge():
        return 0
    return 1


# ============ INFO SUBCOMMAND ============ #
# def subcommand_info(api: API, gids, select_all=False):
#     if select_all:
#         downloads = api.get_downloads()
#     else:
#         downloads = api.get_downloads(gids)
#
#     api.info(downloads)
#     return 0


# ============ LIST SUBCOMMAND ============ #
# def subcommand_list(api: API, list_format=None, sort=None):
#     api.list(list_format=list_format, sort=sort)
#     return 0


# ============ SEARCH SUBCOMMAND ============ #
# def subcommand_search(api: API, ):
#     api.search()
#     return 0
