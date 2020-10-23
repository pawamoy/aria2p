# Why does this file exist, and why not put this in `__main__`?
#
# You might be tempted to import things from `__main__` later,
# but that will cause problems: the code will get executed twice:
#
# - When you run `python -m aria2p` python will execute
#   `__main__.py` as a script. That means there won't be any
#   `aria2p.__main__` in `sys.modules`.
# - When you import `__main__` it will get executed again (as a module) because
#   there's no `aria2p.__main__` in `sys.modules`.

"""Module that contains the command line application."""

import argparse
import json
import sys
from importlib import util as importlib_util
from pathlib import Path
from typing import List, Optional, Union

import requests
from loguru import logger

from aria2p import enable_logger
from aria2p.api import API
from aria2p.client import DEFAULT_HOST, DEFAULT_PORT, DEFAULT_TIMEOUT, Client, ClientException
from aria2p.types import PathOrStr
from aria2p.utils import read_lines

try:
    from aria2p.interface import Interface
except ImportError:
    Interface = None  # type: ignore  # noqa: WPS440 (variable overlap)


# ============ MAIN FUNCTION ============ #
def main(args: Optional[List[str]] = None) -> int:
    """
    Run the main program.

    This function is executed when you type `aria2p` or `python -m aria2p`.

    Arguments:
        args: Arguments passed from the command line.

    Returns:
        An exit code.
    """
    parser = get_parser()
    opts = parser.parse_args(args=args)
    kwargs = opts.__dict__  # noqa: WPS609 (special attribute)

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
    check_args(parser, opts)

    logger.debug("Instantiating API")
    api = API(
        Client(
            host=kwargs.pop("host"),
            port=kwargs.pop("port"),
            secret=kwargs.pop("secret"),
            timeout=kwargs.pop("client_timeout"),
        ),
    )

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
        "add-magnets": subcommand_add_magnets,
        "add-torrents": subcommand_add_torrents,
        "add-metalinks": subcommand_add_metalinks,
        "pause": subcommand_pause,
        "stop": subcommand_pause,  # alias for pause
        "resume": subcommand_resume,
        "start": subcommand_resume,  # alias for resume
        "remove": subcommand_remove,
        "rm": subcommand_remove,  # alias for remove
        "del": subcommand_remove,  # alias for remove
        "delete": subcommand_remove,  # alias for remove
        "purge": subcommand_purge,
        "autopurge": subcommand_purge,  # alias for purge
        "autoclear": subcommand_purge,  # alias for purge
        "autoremove": subcommand_purge,  # alias for purge
        "listen": subcommand_listen,
    }

    subcommand = kwargs.pop("subcommand")

    if subcommand:
        logger.debug("Running subcommand " + subcommand)
    try:
        return subcommands[subcommand](api, **kwargs)
    except ClientException as error:  # noqa: WPS440 (variable overlap)
        print(str(error), file=sys.stderr)
        return error.code


def check_args(parser: argparse.ArgumentParser, opts: argparse.Namespace) -> None:  # noqa: WPS231 (complex)
    """
    Additional checks for command line arguments.

    Arguments:
        parser: An argument parser.
        opts: Parsed options.
    """
    subparsers = [
        action
        for action in parser._actions  # noqa: WPS437 (protected attribute)
        if isinstance(action, argparse._SubParsersAction)  # noqa: WPS437
    ][0].choices

    gid_commands = (
        "pause",
        "stop",
        "remove",
        "rm",
        "del",
        "delete",
        "resume",
        "start",
        "autopurge",
        "autoclear",
        "autoremove",
    )

    if opts.subcommand in gid_commands:
        if not opts.do_all and not opts.gids:
            subparsers[opts.subcommand].error("the following arguments are required: gids or --all")
        elif opts.do_all and opts.gids:
            subparsers[opts.subcommand].error("argument -a/--all: not allowed with arguments gids")
    elif opts.subcommand and opts.subcommand.startswith("add"):
        if not opts.uris and not opts.from_file:
            subparsers[opts.subcommand].error("the following arguments are required: uris")


def get_parser() -> argparse.ArgumentParser:
    """
    Return a parser for the command-line options and arguments.

    Returns:
        An argument parser.
    """
    usage = "%(prog)s [GLOBAL_OPTS...] COMMAND [COMMAND_OPTS...]"  # noqa: WPS323 (%-formatting)
    description = "Command-line tool and Python library to interact with an `aria2c` daemon process through JSON-RPC."
    parser = argparse.ArgumentParser(add_help=False, usage=usage, description=description, prog="aria2p")

    main_help = "Show this help message and exit. Commands also accept the -h/--help option."
    subcommand_help = "Show this help message and exit."

    global_options = parser.add_argument_group(title="Global options")
    global_options.add_argument("-h", "--help", action="help", help=main_help)

    global_options.add_argument(
        "-p",
        "--port",
        dest="port",
        default=DEFAULT_PORT,
        type=int,
        help="Port to use to connect to the remote server.",
    )
    global_options.add_argument(
        "-H",
        "--host",
        dest="host",
        default=DEFAULT_HOST,
        help="Host address for the remote server.",
    )
    global_options.add_argument(
        "-s",
        "--secret",
        dest="secret",
        default="",
        help="Secret token to use to connect to the remote server.",
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
        "-P",
        "--log-path",
        dest="log_path",
        default=None,
        help="Log path to use. Can be a directory or a file.",
    )
    global_options.add_argument(
        "-T",
        "--client-timeout",
        dest="client_timeout",
        default=DEFAULT_TIMEOUT,
        type=float,
        help=f"Timeout in seconds for requests to the remote server. Floats supported. Default: {DEFAULT_TIMEOUT}.",
    )

    # ========= SUBPARSERS ========= #
    subparsers = parser.add_subparsers(dest="subcommand", title="Commands", metavar="", prog="aria2p")

    def subparser(command: str, text: str, **kwargs) -> argparse.ArgumentParser:  # noqa: WPS430 (nested function)
        sub = subparsers.add_parser(command, add_help=False, help=text, description=text, **kwargs)
        sub.add_argument("-h", "--help", action="help", help=subcommand_help)
        return sub

    add_parser = subparser("add", "Add downloads with URIs/Magnets/torrents/Metalinks.")
    add_magnets_parser = subparser("add-magnets", "Add downloads with Magnet URIs.", aliases=["add-magnet"])
    add_metalinks_parser = subparser("add-metalinks", "Add downloads with Metalink files.", aliases=["add-metalink"])
    add_torrents_parser = subparser("add-torrents", "Add downloads with torrent files.", aliases=["add-torrent"])
    subparser(
        "purge",
        "Automatically purge completed/removed/failed downloads.",
        aliases=["autoclear", "autopurge", "autoremove"],
    )
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
        "-P",
        "--params-list",
        dest="params",
        nargs="+",
        help="Parameters as a list of strings.",
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
        "-f",
        "--force",
        dest="force",
        action="store_true",
        help="Pause without contacting servers first.",
    )

    # ========= RESUME PARSER ========= #
    resume_parser.add_argument("gids", nargs="*", help="The GIDs of the downloads to resume.")
    resume_parser.add_argument("-a", "--all", action="store_true", dest="do_all", help="Resume all the downloads.")

    # ========= REMOVE PARSER ========= #
    remove_parser.add_argument("gids", nargs="*", help="The GIDs of the downloads to remove.")
    remove_parser.add_argument("-a", "--all", action="store_true", dest="do_all", help="Remove all the downloads.")
    remove_parser.add_argument(
        "-f",
        "--force",
        dest="force",
        action="store_true",
        help="Remove without contacting servers first.",
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

    Arguments:
        api: The API instance to use.

    Returns:
        int: Always 0.
    """
    downloads = api.get_downloads()

    def print_line(*args):  # noqa: WPS430 (nested function)
        print("{:<17} {:<9} {:>8} {:>12} {:>12} {:>8}  {}".format(*args))  # noqa: P101 (unindexed params)

    print_line("GID", "STATUS", "PROGRESS", "DOWN_SPEED", "UP_SPEED", "ETA", "NAME")

    for download in downloads:
        print_line(
            download.gid,
            download.status,
            download.progress_string(),
            download.download_speed_string(),
            download.upload_speed_string(),
            download.eta_string(),
            download.name,
        )

    return 0


def subcommand_top(api: API) -> int:
    """
    Top subcommand.

    Arguments:
        api: The API instance to use.

    Returns:
        int: Always 0.
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

    Arguments:
        api: The API instance to use.
        method: Name of the method to call.
        params: Parameters to use when calling method.

    Returns:
        int: Always 0.
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


def get_method(name: str) -> Optional[str]:
    """
    Return the actual aria2 method name from a differently formatted name.

    Arguments:
        name: A method name.

    Returns:
        The real method name.
    """
    methods = {}

    for method in Client.METHODS:
        methods[method.lower()] = method
        methods[method.split(".")[1].lower()] = method

    name = name.lower()
    name = name.replace("-", "")
    name = name.replace("_", "")

    return methods.get(name)


def subcommand_add(api: API, uris: List[str] = None, from_file: str = None) -> int:
    """
    Add magnet subcommand.

    Arguments:
        api: The API instance to use.
        uris: The URIs or file-paths to add.
        from_file: Path to the file to read uris from.
            Deprecated: Every URI that is a valid file-path
            and is not a torrent or a metalink is now read as an input file.

    Returns:
        int: 0 if OK else 1.
    """
    uris = uris or []

    if from_file:
        logger.warning(
            "Deprecation warning: every URI that is a valid file-path "
            "and is not a torrent or a metalink is now read as an input file.",
        )

    new_downloads = []

    for uri in uris:
        new_downloads.extend(api.add(uri))

    if new_downloads:
        for new_download in new_downloads:
            print(f"Created download {new_download.gid}")
        return 0

    print("No new download was created", file=sys.stderr)
    return 1


def subcommand_add_magnets(api: API, uris: List[str] = None, from_file: str = None) -> int:
    """
    Add magnet subcommand.

    Arguments:
        api: The API instance to use.
        uris: The URIs of the magnets.
        from_file: Path to the file to read uris from.

    Returns:
        int: Always 0.
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

    Arguments:
        api: The API instance to use.
        torrent_files: The paths to the torrent files.
        from_file: Path to the file to read torrent files paths from.

    Returns:
        int: Always 0.
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

    Arguments:
        api: The API instance to use.
        metalink_files: The paths to the metalink files.
        from_file: Path to the file to metalink files paths from.

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

    Arguments:
        api: The API instance to use.
        gids: The GIDs of the downloads to pause.
        do_all: Pause all downloads if True.
        force: Force pause or not (see API.pause).

    Returns:
        int: 0 if all success, 1 if one failure.
    """
    if do_all:
        if api.pause_all(force=force):
            return 0
        return 1

    try:
        downloads = api.get_downloads(gids)
    except ClientException as error:
        print(str(error), file=sys.stderr)
        return 1

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

    Arguments:
        api: The API instance to use.
        gids: The GIDs of the downloads to resume.
        do_all: Pause all downloads if True.

    Returns:
        int: 0 if all success, 1 if one failure.
    """
    if do_all:
        if api.resume_all():
            return 0
        return 1

    try:
        downloads = api.get_downloads(gids)
    except ClientException as error:
        print(str(error), file=sys.stderr)
        return 1

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

    Arguments:
        api: The API instance to use.
        gids: The GIDs of the downloads to remove.
        do_all: Pause all downloads if True.
        force: Force pause or not (see API.remove).

    Returns:
        int: 0 if all success, 1 if one failure.
    """
    if do_all:
        if api.remove_all():
            return 0
        return 1

    try:
        downloads = api.get_downloads(gids)
    except ClientException as error:
        print(str(error), file=sys.stderr)
        return 1

    ok = True
    result = api.remove(downloads, force=force)

    if all(result):
        return 0 if ok else 1

    for item in result:
        if isinstance(item, ClientException):
            print(item, file=sys.stderr)

    return 1


def subcommand_purge(api: API) -> int:
    """
    Purge subcommand.

    Arguments:
        api: The API instance to use.

    Returns:
        int: 0 if all success, 1 if one failure.
    """
    if api.autopurge():
        return 0
    return 1


def subcommand_listen(
    api: API,
    callbacks_module: PathOrStr = None,
    event_types: List[str] = None,
    timeout: int = 5,
) -> int:
    """
    Listen subcommand.

    Arguments:
        api: The API instance to use.
        callbacks_module: The path to the module to import, containing the callbacks as functions.
        event_types: The event types to process.
        timeout: The timeout to pass to the WebSocket connection, in seconds.

    Returns:
        int: Always 0.
    """
    if not callbacks_module:
        print("aria2p: listen: Please provide the callback module file path with -c option", file=sys.stderr)
        return 1

    if isinstance(callbacks_module, Path):
        callbacks_module = str(callbacks_module)

    if not event_types:
        event_types = ["start", "pause", "stop", "error", "complete", "btcomplete"]

    spec = importlib_util.spec_from_file_location("aria2p_callbacks", callbacks_module)
    callbacks = importlib_util.module_from_spec(spec)

    if callbacks is None:
        print(f"aria2p: Could not import module file {callbacks_module}", file=sys.stderr)
        return 1

    spec.loader.exec_module(callbacks)

    callbacks_kwargs = {}
    for callback_name in (  # noqa: WPS352 (multiline loop)
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
