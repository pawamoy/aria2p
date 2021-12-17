"""Tests for the `cli` module."""

import threading
import time

import pytest

from aria2p.cli.commands import top
from aria2p.cli.commands.add_magnet import add_magnets
from aria2p.cli.commands.add_metalink import add_metalinks
from aria2p.cli.commands.add_torrent import add_torrents
from aria2p.cli.commands.call import call
from aria2p.cli.commands.listen import listen
from aria2p.cli.commands.pause import pause
from aria2p.cli.commands.purge import purge
from aria2p.cli.commands.remove import remove
from aria2p.cli.commands.resume import resume
from aria2p.cli.commands.show import show
from aria2p.cli.main import main
from aria2p.cli.parser import get_parser

from . import BUNSENLABS_MAGNET, TESTS_DATA_DIR
from .conftest import Aria2Server


def out_lines(cs):
    return cs.readouterr().out.split("\n")


def err_lines(cs):
    return cs.readouterr().err.split("\n")


def first_out_line(cs):
    return out_lines(cs)[0]


def first_err_line(cs):
    return err_lines(cs)[0]


def test_show_help(capsys):
    """
    Show help.

    Arguments:
        capsys: Pytest fixture to capture output.
    """
    with pytest.raises(SystemExit):
        main(["-h"])
    captured = capsys.readouterr()
    assert "aria2p" in captured.out


def test_main_returns_2_when_no_remote_running(port):
    assert main([f"--port={port}"]) == 2


def test_parser_error_when_gids_and_all_option(capsys):
    with pytest.raises(SystemExit) as e:
        main(["pause", "-a", "0000000000000001"])
        assert e.value.code == 2
    lines = err_lines(capsys)
    assert lines[0].startswith("usage: aria2p pause")
    assert lines[1].endswith("-a/--all: not allowed with arguments gids")


def test_parser_error_when_no_gid_and_no_all_option(capsys):
    def assert_func(command, alias):
        with pytest.raises(SystemExit) as e:
            main([alias])
            assert e.value.code == 2
        lines = err_lines(capsys)
        assert lines[0].startswith("usage: aria2p " + command)
        assert lines[1].endswith("the following arguments are required: gids or --all")

    for command, aliases in [
        ("pause", ["stop"]),
        ("remove", ["rm", "del", "delete"]),
        ("resume", ["start"]),
    ]:
        assert_func(command, command)
        for alias in aliases:
            assert_func(command, alias)


def test_no_interface_deps_print_error(server, monkeypatch, capsys):
    monkeypatch.setattr(top, "Interface", None)
    main(["-p", str(server.port)])
    line = first_err_line(capsys)
    assert "aria2p[tui]" in line


def test_main_show_subcommand(server, capsys):
    main(["-p", str(server.port), "show"])
    first_line = first_out_line(capsys)
    for word in ("GID", "STATUS", "PROGRESS", "DOWN_SPEED", "UP_SPEED", "ETA", "NAME"):
        assert word in first_line


def test_errors_and_print_message(server, capsys):
    assert main(["-p", str(server.port), "call", "tellstatus", "-P", "invalid gid"]) > 0
    assert capsys.readouterr().err == "Invalid GID invalid gid\n"


def test_show_subcommand(tmp_path, port, capsys):
    with Aria2Server(tmp_path, port, session="1-dl-paused.txt") as server:
        assert show(server.api) == 0
        assert len(capsys.readouterr().out.rstrip("\n").split("\n")) == 2


def test_call_subcommand(server, capsys):
    assert call(server.api, "wrongMethod", []) == 1
    assert (
        capsys.readouterr().err == "aria2p: call: Unknown method wrongMethod.\n"
        "  Run 'aria2p call listmethods' to list the available methods.\n"
    )


def test_call_subcommand_with_json_params(tmp_path, port):
    with Aria2Server(tmp_path, port, session="1-dl-paused.txt") as server:
        assert call(server.api, "tellstatus", '["0000000000000001"]') == 0


def test_call_subcommand_with_no_params(server):
    assert call(server.api, "listmethods", None) == 0


def test_add_magnet_subcommand(server):
    assert add_magnets(server.api, [BUNSENLABS_MAGNET]) == 0


def test_add_torrent_subcommand(server):
    assert add_torrents(server.api, [TESTS_DATA_DIR / "bunsenlabs-helium-4.iso.torrent"]) == 0


def test_add_metalink_subcommand(server):
    assert add_metalinks(server.api, [TESTS_DATA_DIR / "debian.metalink"]) == 0


def test_pause_subcommand(tmp_path, port):
    with Aria2Server(tmp_path, port, session="1-dl.txt") as server:
        assert pause(server.api, ["0000000000000001"]) == 0


def test_pause_subcommand_already_paused(tmp_path, port, capsys):
    with Aria2Server(tmp_path, port, session="2-dls-paused.txt") as server:
        assert pause(server.api, ["0000000000000001", "0000000000000002"]) == 1
        assert (
            capsys.readouterr().err
            == "GID#0000000000000001 cannot be paused now\nGID#0000000000000002 cannot be paused now\n"
        )


def test_pause_subcommand_one_paused(tmp_path, port, capsys):
    with Aria2Server(tmp_path, port, session="one-active-one-paused.txt") as server:
        assert pause(server.api, ["0000000000000001", "0000000000000002"]) == 1
        assert "GID#0000000000000002 cannot be paused now" in capsys.readouterr().err


def test_pause_all_subcommand(server):
    assert pause(server.api, do_all=True) == 0


def test_pause_all_subcommand_doesnt_fail_with_already_paused_downloads(tmp_path, port):
    with Aria2Server(tmp_path, port, session="2-dls-paused.txt") as server:
        assert pause(server.api, do_all=True) == 0


def test_resume_subcommand(tmp_path, port, capsys):
    with Aria2Server(tmp_path, port, session="1-dl-paused.txt") as server:
        assert resume(server.api, ["0000000000000001"]) == 0


def test_resume_subcommand_already_unpaused(tmp_path, port, capsys):
    with Aria2Server(tmp_path, port, session="2-dls.txt") as server:
        assert resume(server.api, ["0000000000000001", "0000000000000002"]) == 1
        assert (
            capsys.readouterr().err
            == "GID#0000000000000001 cannot be unpaused now\nGID#0000000000000002 cannot be unpaused now\n"
        )


def test_resume_subcommand_one_unpaused(tmp_path, port, capsys):
    with Aria2Server(tmp_path, port, session="one-active-one-paused.txt") as server:
        assert resume(server.api, ["0000000000000001", "0000000000000002"]) == 1
        assert capsys.readouterr().err == "GID#0000000000000001 cannot be unpaused now\n"


def test_resume_all_subcommand(server):
    assert resume(server.api, do_all=True) == 0


def test_resume_all_subcommand_doesnt_fail_with_already_active_downloads(tmp_path, port):
    with Aria2Server(tmp_path, port, session="2-dls.txt") as server:
        assert resume(server.api, do_all=True) == 0


def test_remove_subcommand(tmp_path, port):
    with Aria2Server(tmp_path, port, session="1-dl-paused.txt") as server:
        assert remove(server.api, ["0000000000000001"]) == 0


def test_remove_subcommand_one_failure(tmp_path, port, capsys):
    with Aria2Server(tmp_path, port, session="1-dl-paused.txt") as server:
        assert remove(server.api, ["0000000000000001", "0000000000000002"]) == 1
        assert capsys.readouterr().err == "GID 0000000000000002 is not found\n"


def test_remove_all_subcommand(server):
    assert remove(server.api, do_all=True) == 0


def test_purge_subcommand(tmp_path, port):
    with Aria2Server(tmp_path, port, session="very-small-download.txt") as server:
        assert purge(server.api) == 0


def test_listen_subcommand(tmp_path, port, capsys):
    with Aria2Server(tmp_path, port, session="2-dls-paused.txt") as server:

        def thread_target():
            time.sleep(2)
            server.api.resume_all()
            time.sleep(3)
            server.api.stop_listening()

        thread = threading.Thread(target=thread_target)
        thread.start()
        listen(server.api, callbacks_module=TESTS_DATA_DIR / "callbacks.py", event_types=["start"])
    captured = capsys.readouterr()
    assert captured.err == ""
    assert captured.out == "started 0000000000000001\nstarted 0000000000000002\n"


@pytest.mark.parametrize("command", ["add", "add-magnet", "add-torrent", "add-metalink"])
def test_parse_valid_options(command):
    parser = get_parser()
    opts = parser.parse_args([command, "/some/file/on/the/disk", "-o", "opt1=val;opt2=val2, val3=val4"])
    assert opts.options == {"opt1": "val", "opt2": "val2, val3=val4"}


@pytest.mark.parametrize("command", ["add", "add-magnet", "add-torrent", "add-metalink"])
def test_parse_invalid_options(command, capsys):
    parser = get_parser()
    with pytest.raises(SystemExit):
        opts = parser.parse_args([command, "http://example.com", "-o", "opt1"])
    assert "Options strings must follow this format" in capsys.readouterr().err


@pytest.mark.parametrize(
    ("command", "option"),
    [("add", "uris"), ("add-magnet", "uris"), ("add-torrent", "torrent_files"), ("add-metalink", "metalink_files")],
)
def test_error_when_missing_arg(command, option, capsys):
    with pytest.raises(SystemExit):
        main([command])
    assert option in capsys.readouterr().err
