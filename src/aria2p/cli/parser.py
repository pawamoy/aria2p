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

from __future__ import annotations

import argparse
from typing import Any

from aria2p.client import DEFAULT_HOST, DEFAULT_PORT, DEFAULT_TIMEOUT


def check_args(parser: argparse.ArgumentParser, opts: argparse.Namespace) -> None:  # (complex)
    """Additional checks for command line arguments.

    Parameters:
        parser: An argument parser.
        opts: Parsed options.
    """
    subparsers = next(action for action in parser._actions if isinstance(action, argparse._SubParsersAction)).choices

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
    elif opts.subcommand:
        if opts.subcommand in {"add", "add-magnet", "add-magnets"} and opts.uris and not opts.from_file:
            subparsers[opts.subcommand].error("the following arguments are required: uris")
        elif opts.subcommand.startswith("add-torrent") and not opts.torrent_files and not opts.from_file:
            subparsers[opts.subcommand].error("the following arguments are required: torrent_files")
        elif opts.subcommand.startswith("add-metalink") and not opts.metalink_files and not opts.from_file:
            subparsers[opts.subcommand].error("the following arguments are required: metalink_files")


def parse_options_string(options_string: str | None = None) -> dict:
    """Parse string of options.

    Parameters:
        options_string: String of aria2c options.

    Raises:
        ArgumentTypeError: When the options string is not correctly formatted.

    Returns:
        Dictionary containing aria2c options.
    """
    options_string = options_string or ""
    options = {}
    for download_option in options_string.split(";"):
        try:
            opt, val = download_option.split("=", 1)
        except ValueError:
            raise argparse.ArgumentTypeError(  # noqa: B904,TRY200
                "Options strings must follow this format:\nopt-name=opt-value;opt-name2=opt-value2",
            )
        options[opt.strip()] = val.strip()
    return options


def get_parser() -> argparse.ArgumentParser:
    """Return a parser for the command-line options and arguments.

    Returns:
        An argument parser.
    """
    usage = "%(prog)s [GLOBAL_OPTS...] COMMAND [COMMAND_OPTS...]"
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

    def subparser(command: str, text: str, **kwargs: Any) -> argparse.ArgumentParser:
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

    # ========= REUSABLE OPTIONS ========= #
    def add_options_argument(_parser: argparse.ArgumentParser) -> None:
        _parser.add_argument(
            "-o",
            "--options",
            dest="options",
            type=parse_options_string,
            help="Options for the new download(s), separated by semi-colons. "
            "Example: 'dir=~/aria2_downloads;max-download-limit=100K'",
        )

    def add_position_argument(_parser: argparse.ArgumentParser) -> None:
        _parser.add_argument(
            "-p",
            "--position",
            dest="position",
            type=int,
            help="Position at which to add the new download(s) in the queue. Starts at 0 (top).",
        )

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
    add_options_argument(add_parser)
    add_position_argument(add_parser)

    # ========= ADD MAGNET PARSER ========= #
    add_magnets_parser.add_argument("uris", nargs="*", help="The magnet URIs to add.")
    add_magnets_parser.add_argument("-f", "--from-file", dest="from_file", help="Load URIs from a file.")
    add_options_argument(add_magnets_parser)
    add_position_argument(add_magnets_parser)

    # ========= ADD TORRENT PARSER ========= #
    add_torrents_parser.add_argument("torrent_files", nargs="*", help="The paths to the torrent files.")
    add_torrents_parser.add_argument("-f", "--from-file", dest="from_file", help="Load file paths from a file.")
    add_options_argument(add_torrents_parser)
    add_position_argument(add_torrents_parser)

    # ========= ADD METALINK PARSER ========= #
    add_metalinks_parser.add_argument("metalink_files", nargs="*", help="The paths to the metalink files.")
    add_metalinks_parser.add_argument("-f", "--from-file", dest="from_file", help="Load file paths from a file.")
    add_options_argument(add_metalinks_parser)
    add_position_argument(add_metalinks_parser)

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
