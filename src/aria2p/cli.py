"""
Module that contains the command line application.

Why does this file exist, and why not put this in __main__?

You might be tempted to import things from __main__ later,
but that will cause problems: the code will get executed twice:

- When you run `python -m aria2p` python will execute
  ``__main__.py`` as a script. That means there won't be any
  ``aria2p.__main__`` in ``sys.modules``.
- When you import __main__ it will get executed again (as a module) because
  there's no ``aria2p.__main__`` in ``sys.modules``.

Also see http://click.pocoo.org/5/setuptools/#setuptools-integration.
"""

import argparse
import importlib.util
import json
import sys
from collections import namedtuple
from pathlib import Path
from typing import Any, List, Optional, Union

import requests
from loguru import logger

from aria2p import Download, enable_logger

from .api import API
from .client import DEFAULT_HOST, DEFAULT_PORT, Client, ClientException
from .utils import get_version

try:
    from .interface import Interface
except ImportError:
    Interface = None


# ============ MAIN FUNCTION ============ #
def main(args: Optional[List[str]] = None) -> int:
    """The main function, which is executed when you type ``aria2p`` or ``python -m aria2p``."""

    parser = get_parser()
    args = parser.parse_args(args=args)
    kwargs = args.__dict__

    log_level = kwargs.pop("log_level")
    log_path = kwargs.pop("log_path")

    if log_path:
        log_path = Path(log_path)
        if log_path.is_dir():
            log_path = log_path / "aria2p-{time}.log"
        enable_logger(sink=log_path, level=log_level or "WARNING")
    elif log_level:
        enable_logger(sink=sys.stderr, level=log_level)

    logger.debug("Checking arguments")
    check_args(parser, args)

    logger.debug("Instantiating API")
    api = API(Client(host=kwargs.pop("host"), port=kwargs.pop("port"), secret=kwargs.pop("secret")))

    logger.info(f"API instantiated: {api!r}")

    # Warn if no aria2 daemon process seems to be running
    logger.debug("Testing connection")
    try:
        api.client.get_version()
    except requests.ConnectionError as error:
        print(f"[ERROR] {error}", file=sys.stderr)
        print(file=sys.stderr)
        print("Please make sure that an instance of aria2c is running with RPC mode enabled,", file=sys.stderr)
        print("and that you have provided the right host, port and secret token.", file=sys.stderr)
        print("More information at https://aria2p.readthedocs.io/en/latest.", file=sys.stderr)
        return 2

    subcommands = {
        None: subcommand_top,
        "show": subcommand_show,
        "top": subcommand_top,
        "call": subcommand_call,
        "add": subcommand_add,
        "add-magnet": subcommand_add_magnets,
        "add-magnets": subcommand_add_magnets,
        "add-torrent": subcommand_add_torrents,
        "add-torrents": subcommand_add_torrents,
        "add-metalink": subcommand_add_metalinks,
        "add-metalinks": subcommand_add_metalinks,
        "pause": subcommand_pause,
        "stop": subcommand_pause,  # alias for pause
        "resume": subcommand_resume,
        "start": subcommand_resume,  # alias for resume
        "remove": subcommand_remove,
        "rm": subcommand_remove,  # alias for remove
        "del": subcommand_remove,  # alias for remove
        "delete": subcommand_remove,  # alias for remove
        "autopurge": subcommand_autopurge,
        "autoclear": subcommand_autopurge,  # alias for autopurge
        "listen": subcommand_listen,
    }

    subcommand = kwargs.pop("subcommand")

    if subcommand:
        logger.debug("Running subcommand " + subcommand)
    try:
        return subcommands.get(subcommand)(api, **kwargs)
    except ClientException as error:
        print(error.message, file=sys.stderr)
        return error.code


def check_args(parser: argparse.ArgumentParser, args: namedtuple) -> None:
    """Additional checks for command line arguments."""
    subparser = [action for action in parser._actions if isinstance(action, argparse._SubParsersAction)][0].choices

    if args.subcommand in ("pause", "stop", "remove", "rm", "del", "delete", "resume", "start", "purge", "clear"):
        if not args.do_all and not args.gids:
            subparser[args.subcommand].error("the following arguments are required: gids or --all")
        elif args.do_all and args.gids:
            subparser[args.subcommand].error("argument -a/--all: not allowed with arguments gids")
    elif args.subcommand in ("add", "add-magnet", "add-magnets"):
        if not args.uris and not args.from_file:
            subparser[args.subcommand].error("the following arguments are required: uris or -f FILE")
    elif args.subcommand in ("add-torrent", "add-torrents"):
        if not args.torrent_files and not args.from_file:
            subparser[args.subcommand].error("the following arguments are required: torrent_files or -f FILE")
    elif args.subcommand in ("add-metalink", "add-metalinks"):
        if not args.metalink_files and not args.from_file:
            subparser[args.subcommand].error("the following arguments are required: metalink_files or -f FILE")


def get_parser() -> argparse.ArgumentParser:
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
    global_options.add_argument(
        "-L",
        "--log-level",
        dest="log_level",
        default=None,
        help="Log level to use",
        choices=("TRACE", "DEBUG", "INFO", "SUCCESS", "WARNING", "ERROR", "CRITICAL"),
        type=str.upper,
    )
    global_options.add_argument(
        "-P", "--log-path", dest="log_path", default=None, help="Log path to use. Can be a directory or a file."
    )

    # ========= SUBPARSERS ========= #
    subparsers = parser.add_subparsers(dest="subcommand", title="Commands", metavar="", prog="aria2p")

    def subparser(command: str, text: str, **kwargs) -> argparse.ArgumentParser:
        sub = subparsers.add_parser(command, add_help=False, help=text, description=text, **kwargs)
        sub.add_argument("-h", "--help", action="help", help=subcommand_help)
        return sub

    add_parser = subparser("add", "Add downloads with URIs/Magnets/torrents/Metalinks.")
    add_magnets_parser = subparser("add-magnets", "Add downloads with Magnet URIs.", aliases=["add-magnet"])
    add_metalinks_parser = subparser("add-metalinks", "Add downloads with Metalink files.", aliases=["add-metalink"])
    add_torrents_parser = subparser("add-torrents", "Add downloads with torrent files.", aliases=["add-torrent"])
    subparser("autopurge", "Automatically purge completed/removed/failed downloads.", aliases=["autoclear"])
    call_parser = subparser("call", "Call a remote method through the JSON-RPC client.")
    pause_parser = subparser("pause", "Pause downloads.", aliases=["stop"])
    remove_parser = subparser("remove", "Remove downloads.", aliases=["rm", "del", "delete"])
    resume_parser = subparser("resume", "Resume downloads.", aliases=["start"])
    subparser("show", "Show the download progression.")
    subparser("top", "Launch the top-like interactive interface.")
    listen_parser = subparser("listen", "Listen to notifications.")

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

    # ========= ADD PARSER ========= #
    add_parser.add_argument("uris", nargs="*", help="The URIs/file-paths to add.")
    add_parser.add_argument("-f", "--from-file", dest="from_file", help="Load URIs from a file.")

    # ========= ADD MAGNET PARSER ========= #
    add_magnets_parser.add_argument("uris", nargs="*", help="The magnet URIs to add.")
    add_magnets_parser.add_argument("-f", "--from-file", dest="from_file", help="Load URIs from a file.")

    # ========= ADD TORRENT PARSER ========= #
    add_torrents_parser.add_argument("torrent_files", nargs="*", help="The paths to the torrent files.")
    add_torrents_parser.add_argument("-f", "--from-file", dest="from_file", help="Load file paths from a file.")

    # ========= ADD METALINK PARSER ========= #
    add_metalinks_parser.add_argument("metalink_files", nargs="*", help="The paths to the metalink files.")
    add_metalinks_parser.add_argument("-f", "--from-file", dest="from_file", help="Load file paths from a file.")

    # ========= PAUSE PARSER ========= #
    pause_parser.add_argument("gids", nargs="*", help="The GIDs of the downloads to pause.")
    pause_parser.add_argument("-a", "--all", action="store_true", dest="do_all", help="Pause all the downloads.")
    pause_parser.add_argument(
        "-f", "--force", dest="force", action="store_true", help="Pause without contacting servers first."
    )

    # ========= RESUME PARSER ========= #
    resume_parser.add_argument("gids", nargs="*", help="The GIDs of the downloads to resume.")
    resume_parser.add_argument("-a", "--all", action="store_true", dest="do_all", help="Resume all the downloads.")

    # ========= REMOVE PARSER ========= #
    remove_parser.add_argument("gids", nargs="*", help="The GIDs of the downloads to remove.")
    remove_parser.add_argument("-a", "--all", action="store_true", dest="do_all", help="Remove all the downloads.")
    remove_parser.add_argument(
        "-f", "--force", dest="force", action="store_true", help="Remove without contacting servers first."
    )

    # ========= LISTEN PARSER ========= #
    listen_parser.add_argument(
        "-c",
        "--callbacks-module",
        dest="callbacks_module",
        help="Path to the Python module defining your notifications callbacks.",
    )
    listen_parser.add_argument(
        "event_types",
        nargs="*",
        help="The types of notifications to process: "
        "start, pause, stop, error, complete or btcomplete. "
        "Example: aria2p listen error btcomplete. "
        "Useful if you want to spawn multiple specialized aria2p listener, "
        "for example one for each type of notification, "
        "but still want to use only one callback file.",
    )
    listen_parser.add_argument(
        "-t",
        "--timeout",
        dest="timeout",
        type=float,
        default=5,
        help="Timeout in seconds to use when waiting for data over the WebSocket at each iteration. "
        "Use small values for faster reactivity when stopping to listen.",
    )

    return parser


# ============ SUBCOMMANDS ============ #
def subcommand_show(api: API) -> int:
    """
    Show subcommand.

    Parameters:
        api: the API instance to use.

    Returns:
        int: always 0.
    """
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

    return 0


def subcommand_top(api: API) -> int:
    """
    Top subcommand.

    Parameters:
        api: the API instance to use.

    Returns:
        int: always 0.
    """
    if Interface is None:
        print(
            "The top-interface dependencies are not installed. Try running `pip install aria2p[tui]` to install them.",
            file=sys.stderr,
        )
        return 1
    interface = Interface(api)
    success = interface.run()
    return 0 if success else 1


def subcommand_call(api: API, method: str, params: Union[str, List[str]]) -> int:
    """
    Call subcommand.

    Parameters:
        api: the API instance to use.
        method: name of the method to call.
        params: parameters to use when calling method.

    Returns:
        int: always 0.
    """
    real_method = get_method(method)
    if real_method is None:
        print(f"aria2p: call: Unknown method {method}.", file=sys.stderr)
        print("  Run 'aria2p call listmethods' to list the available methods.", file=sys.stderr)
        return 1

    if isinstance(params, str):
        params = json.loads(params)
    elif params is None:
        params = []

    response = api.client.call(real_method, params)
    print(json.dumps(response))

    return 0


def get_method(name: str, default: Any = None) -> str:
    """Return the actual aria2 method name from a differently formatted name."""
    methods = {}
    for method in Client.METHODS:
        methods[method.lower()] = method
        methods[method.split(".")[1].lower()] = method
    name = name.lower()
    name = name.replace("-", "")
    name = name.replace("_", "")
    return methods.get(name, default)


def read_lines(path: str) -> List[str]:
    with Path(path).open() as stream:
        return stream.readlines()


def subcommand_add(api: API, uris: List[str] = None, from_file: str = None) -> int:
    """
    Add magnet subcommand.

    Parameters:
        api: the API instance to use.
        uris: the URIs or file-paths to add.
        from_file: path to the file to read uris from.

    Returns:
        int: 0 if OK else 1.
    """
    ok = True

    if not uris:
        uris = []
    if from_file:
        try:
            uris.extend(read_lines(from_file))
        except OSError:
            print(f"Cannot open file: {from_file}", file=sys.stderr)
            ok = False

    for uri in uris:
        path = Path(uri)

        # On Windows, path.exists() generates an OSError when path is an URI
        # See https://github.com/pawamoy/aria2p/issues/41
        try:
            path_exists = path.exists()
        except OSError:
            path_exists = False

        if path_exists:
            if path.suffix == ".torrent":
                new_downloads = [api.add_torrent(path)]
            elif path.suffix == ".metalink":
                new_downloads = api.add_metalink(path)
            else:
                print(f"Cannot determine type of file {path}", file=sys.stderr)
                print(f"  Known extensions are .torrent and .metalink", file=sys.stderr)
                ok = False
                continue
        elif uri.startswith("magnet:?"):
            new_downloads = [api.add_magnet(uri)]
        else:
            new_downloads = [api.add_uris([uri])]

        for new_download in new_downloads:
            print(f"Created download {new_download.gid}")

    return 0 if ok else 1


def subcommand_add_magnets(api: API, uris: List[str] = None, from_file: str = None) -> int:
    """
    Add magnet subcommand.

    Parameters:
        api: the API instance to use.
        uris: the URIs of the magnets.
        from_file: path to the file to read uris from.

    Returns:
        int: always 0.
    """
    ok = True

    if not uris:
        uris = []
    if from_file:
        try:
            uris.extend(read_lines(from_file))
        except OSError:
            print(f"Cannot open file: {from_file}", file=sys.stderr)
            ok = False

    for uri in uris:
        new_download = api.add_magnet(uri)
        print(f"Created download {new_download.gid}")
    return 0 if ok else 1


def subcommand_add_torrents(api: API, torrent_files: List[str] = None, from_file: str = None) -> int:
    """
    Add torrent subcommand.

    Parameters:
        api: the API instance to use.
        torrent_files: the paths to the torrent files.
        from_file: path to the file to read torrent files paths from.

    Returns:
        int: always 0.
    """
    ok = True

    if not torrent_files:
        torrent_files = []
    if from_file:
        try:
            torrent_files.extend(read_lines(from_file))
        except OSError:
            print(f"Cannot open file: {from_file}", file=sys.stderr)
            ok = False

    for torrent_file in torrent_files:
        new_download = api.add_torrent(torrent_file)
        print(f"Created download {new_download.gid}")
    return 0 if ok else 1


def subcommand_add_metalinks(api: API, metalink_files: List[str] = None, from_file: str = None) -> int:
    """
    Add metalink subcommand.

    Parameters:
        api: the API instance to use.
        metalink_files: the paths to the metalink files.
        from_file: path to the file to metalink files paths from.

    Returns:
        int: 0 if OK else 1.
    """
    ok = True

    if not metalink_files:
        metalink_files = []
    if from_file:
        try:
            metalink_files.extend(read_lines(from_file))
        except OSError:
            print(f"Cannot open file: {from_file}", file=sys.stderr)
            ok = False

    for metalink_file in metalink_files:
        new_downloads = api.add_metalink(metalink_file)
        for download in new_downloads:
            print(f"Created download {download.gid}")
    return 0 if ok else 1


def subcommand_pause(api: API, gids: List[str] = None, do_all: bool = False, force: bool = False) -> int:
    """
    Pause subcommand.

    Parameters:
        api: the API instance to use.
        gids: the GIDs of the downloads to pause.
        do_all: pause all downloads if True.
        force: force pause or not (see API.pause).

    Returns:
        int: 0 if all success, 1 if one failure.
    """
    if do_all:
        if api.pause_all(force=force):
            return 0
        return 1

    # FIXME: could break if API.resume needs more info than just gid
    # See how we do that in subcommand_remove
    downloads = [Download(api, {"gid": gid}) for gid in gids]
    result = api.pause(downloads, force=force)
    if all(result):
        return 0
    for item in result:
        if isinstance(item, ClientException):
            print(item, file=sys.stderr)
    return 1


def subcommand_resume(api: API, gids: List[str] = None, do_all: bool = False) -> int:
    """
    Resume subcommand.

    Parameters:
        api: the API instance to use.
        gids: the GIDs of the downloads to resume.
        do_all: pause all downloads if True.

    Returns:
        int: 0 if all success, 1 if one failure.
    """
    if do_all:
        if api.resume_all():
            return 0
        return 1

    # FIXME: could break if API.resume needs more info than just gid
    # See how we do that in subcommand_remove
    downloads = [Download(api, {"gid": gid}) for gid in gids]
    result = api.resume(downloads)
    if all(result):
        return 0
    for item in result:
        if isinstance(item, ClientException):
            print(item, file=sys.stderr)
    return 1


def subcommand_remove(api: API, gids: List[str] = None, do_all: bool = False, force: bool = False) -> int:
    """
    Remove subcommand.

    Parameters:
        api: the API instance to use.
        gids: the GIDs of the downloads to remove.
        do_all: pause all downloads if True.
        force: force pause or not (see API.remove).

    Returns:
        int: 0 if all success, 1 if one failure.
    """
    if do_all:
        if api.remove_all():
            return 0
        return 1

    ok = True
    downloads = []

    for gid in gids:
        try:
            downloads.append(api.get_download(gid))
        except ClientException as error:
            print(str(error), file=sys.stderr)
            ok = False

    result = api.remove(downloads, force=force)
    if all(result):
        return 0 if ok else 1
    for item in result:
        if isinstance(item, ClientException):
            print(item, file=sys.stderr)
    return 1


def subcommand_autopurge(api: API) -> int:
    """
    Autopurge subcommand.

    Parameters:
        api: the API instance to use.

    Returns:
        int: 0 if all success, 1 if one failure.
    """
    version = get_version()
    if version.major == 0 and 9 > version.minor >= 7:
        print(
            "Future change warning: command 'autopurge' will be renamed 'purge' in version 0.9.0, "
            "with an 'autoremove' alias.",
            file=sys.stderr,
        )
    if api.autopurge():
        return 0
    return 1


def subcommand_listen(
    api: API, callbacks_module: Union[str, Path] = None, event_types: List[str] = None, timeout: int = 5
) -> int:
    """
    Listen subcommand.

    Parameters:
        api: the API instance to use.
        callbacks_module: the path to the module to import, containing the callbacks as functions.
        event_types: the event types to process.
        timeout: the timeout to pass to the WebSocket connection, in seconds.

    Returns:
        int: always 0.
    """
    if not callbacks_module:
        print("aria2p: listen: Please provide the callback module file path with -c option", file=sys.stderr)
        return 1

    if isinstance(callbacks_module, Path):
        callbacks_module = str(callbacks_module)

    if not event_types:
        event_types = ["start", "pause", "stop", "error", "complete", "btcomplete"]

    spec = importlib.util.spec_from_file_location("aria2p_callbacks", callbacks_module)
    callbacks = importlib.util.module_from_spec(spec)

    if callbacks is None:
        print(f"aria2p: Could not import module file {callbacks_module}", file=sys.stderr)
        return 1

    spec.loader.exec_module(callbacks)

    callbacks_kwargs = {}
    for callback_name in (
        "on_download_start",
        "on_download_pause",
        "on_download_stop",
        "on_download_error",
        "on_download_complete",
        "on_bt_download_complete",
    ):
        if callback_name[3:].replace("download", "").replace("_", "") in event_types:
            callback = getattr(callbacks, callback_name, None)
            if callback:
                callbacks_kwargs[callback_name] = callback

    api.listen_to_notifications(timeout=timeout, handle_signals=True, threaded=False, **callbacks_kwargs)
    return 0


def _changed_name(name, func):
    def _new_func(*args, **kwargs):
        logger.warning(
            f"Deprecation warning: function {name} was renamed {name}s in version 0.6.0,"
            f"and will be removed in version 0.9.0."
        )
        return func(*args, **kwargs)

    return _new_func


subcommand_add_magnet = _changed_name("subcommand_add_magnet", subcommand_add_magnets)
subcommand_add_torrent = _changed_name("subcommand_add_torrent", subcommand_add_torrents)
subcommand_add_metalink = _changed_name("subcommand_add_metalink", subcommand_add_metalinks)
