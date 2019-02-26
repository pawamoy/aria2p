import time
from unittest.mock import patch

from aria2p import cli

from . import BUNSENLABS_MAGNET, SESSIONS_DIR, TESTS_DATA_DIR, Aria2Server


def _first_line(cs):
    return cs.readouterr().out.split("\n")[0]


def test_main_returns_2_when_no_remote_running():
    assert cli.main([]) == 2


@patch("aria2p.cli.subcommand_show")
def test_main_no_command_defaults_to_show(mocked_function):
    with Aria2Server(port=7500) as server:
        cli.main(["-p", str(server.port)])
        assert mocked_function.called


def test_main_show_subcommand(capsys):
    with Aria2Server(port=7501) as server:
        cli.main(["-p", str(server.port), "show"])
        first_line = _first_line(capsys)
        for word in ("GID", "STATUS", "PROGRESS", "DOWN_SPEED", "UP_SPEED", "ETA", "NAME"):
            assert word in first_line


def test_errors_and_print_message(capsys):
    with Aria2Server(port=7502) as server:
        assert cli.main(["-p", str(server.port), "call", "tellstatus", "-P", "invalid gid"]) > 0
        assert capsys.readouterr().err == "Invalid GID invalid gid\n"


def test_show_subcommand(capsys):
    with Aria2Server(port=7503, session=SESSIONS_DIR / "dl-aria2-1.34.0-paused.txt") as server:
        assert cli.subcommand_show(server.api) == 0
        assert len(capsys.readouterr().out.rstrip("\n").split("\n")) == 2


def test_call_subcommand(capsys):
    with Aria2Server(port=7504) as server:
        assert cli.subcommand_call(server.api, "wrongMethod", []) == 1
        assert (
            capsys.readouterr().err == "[ERROR] call: Unknown method wrongMethod.\n\n"
            "Run 'aria2p call listmethods' to list the available methods.\n"
        )


def test_call_subcommand_with_json_params():
    with Aria2Server(port=7505, session=SESSIONS_DIR / "dl-aria2-1.34.0-paused.txt") as server:
        assert cli.subcommand_call(server.api, "tellstatus", '["2089b05ecca3d829"]') == 0


def test_call_subcommand_with_no_params():
    with Aria2Server(port=7506) as server:
        assert cli.subcommand_call(server.api, "listmethods", None) == 0


def test_add_magnet_subcommand():
    with Aria2Server(port=7507) as server:
        assert cli.subcommand_add_magnet(server.api, BUNSENLABS_MAGNET) == 0


def test_add_torrent_subcommand():
    with Aria2Server(port=7508) as server:
        assert cli.subcommand_add_torrent(server.api, TESTS_DATA_DIR / "bunsenlabs-helium-4.iso.torrent") == 0


def test_add_metalink_subcommand():
    with Aria2Server(port=7509) as server:
        assert cli.subcommand_add_metalink(server.api, TESTS_DATA_DIR / "debian.metalink") == 0


def test_pause_subcommand(capsys):
    with Aria2Server(port=7510, session=SESSIONS_DIR / "dl-aria2-1.34.0.txt") as server:
        assert cli.subcommand_pause(server.api, ["2089b05ecca3d829"]) == 0


def test_pause_subcommand_already_paused(capsys):
    with Aria2Server(port=7511, session=SESSIONS_DIR / "2-dl-in-queue.txt") as server:
        assert cli.subcommand_pause(server.api, ["2089b05ecca3d829", "cca3d8292089b05e"]) == 1
        assert (
            capsys.readouterr().err
            == "GID#2089b05ecca3d829 cannot be paused now\nGID#cca3d8292089b05e cannot be paused now\n"
        )


def test_pause_subcommand_one_paused(capsys):
    with Aria2Server(port=7512, session=SESSIONS_DIR / "one-active-one-paused.txt") as server:
        assert cli.subcommand_pause(server.api, ["2089b05ecca3d829", "cca3d8292089b05e"]) == 1
        assert capsys.readouterr().err == "GID#cca3d8292089b05e cannot be paused now\n"


def test_pause_all_subcommand():
    with Aria2Server(port=7513) as server:
        assert cli.subcommand_pause_all(server.api) == 0


def test_pause_all_subcommand_fails():
    with Aria2Server(port=7514, session=SESSIONS_DIR / "2-dl-in-queue.txt") as server:
        assert cli.subcommand_pause_all(server.api) == 1


def test_resume_subcommand(capsys):
    with Aria2Server(port=7515, session=SESSIONS_DIR / "dl-aria2-1.34.0-paused.txt") as server:
        assert cli.subcommand_resume(server.api, ["2089b05ecca3d829"]) == 0


def test_resume_subcommand_already_unpaused(capsys):
    with Aria2Server(port=7516, session=SESSIONS_DIR / "dl-2-aria2.txt") as server:
        assert cli.subcommand_resume(server.api, ["2089b05ecca3d829", "cca3d8292089b05e"]) == 1
        assert (
            capsys.readouterr().err
            == "GID#2089b05ecca3d829 cannot be unpaused now\nGID#cca3d8292089b05e cannot be unpaused now\n"
        )


def test_resume_subcommand_one_unpaused(capsys):
    with Aria2Server(port=7517, session=SESSIONS_DIR / "one-active-one-paused.txt") as server:
        assert cli.subcommand_resume(server.api, ["2089b05ecca3d829", "cca3d8292089b05e"]) == 1
        assert capsys.readouterr().err == "GID#2089b05ecca3d829 cannot be unpaused now\n"


def test_resume_all_subcommand():
    with Aria2Server(port=7518) as server:
        assert cli.subcommand_resume_all(server.api) == 0


def test_resume_all_subcommand_fails():
    with Aria2Server(port=7519, session=SESSIONS_DIR / "dl-2-aria2.txt") as server:
        assert cli.subcommand_resume_all(server.api) == 1


def test_remove_subcommand():
    with Aria2Server(port=7520, session=SESSIONS_DIR / "dl-aria2-1.34.0-paused.txt") as server:
        assert cli.subcommand_remove(server.api, ["2089b05ecca3d829"]) == 0


def test_remove_subcommand_one_failure(capsys):
    with Aria2Server(port=7520, session=SESSIONS_DIR / "dl-aria2-1.34.0-paused.txt") as server:
        assert cli.subcommand_remove(server.api, ["2089b05ecca3d829", "cca3d8292089b05e"]) == 1
        assert capsys.readouterr().err == "GID cca3d8292089b05e is not found\n"


def test_remove_all_subcommand():
    with Aria2Server(port=7521) as server:
        assert cli.subcommand_remove_all(server.api) == 0


# def test_remove_all_subcommand_fails():
#     with Aria2Server(port=7521) as server:
#         assert cli.subcommand_remove_all(server.api) == 0


def test_purge_subcommand():
    with Aria2Server(port=7520, session=SESSIONS_DIR / "very-small-remote-file.txt") as server:
        while not server.api.get_download("2089b05ecca3d829").is_complete:
            time.sleep(0.2)
        assert cli.subcommand_purge(server.api, ["2089b05ecca3d829"]) == 0


def test_purge_subcommand_one_failure(capsys):
    with Aria2Server(port=7520, session=SESSIONS_DIR / "small-file-and-paused-file.txt") as server:
        while not server.api.get_download("2089b05ecca3d829").is_complete:
            time.sleep(0.2)
        assert cli.subcommand_purge(server.api, ["2089b05ecca3d829", "208a3d8299b05ecc"]) == 1
        assert capsys.readouterr().err == "Could not remove download result of GID#208a3d8299b05ecc\n"


def test_autopurge_subcommand():
    with Aria2Server(port=7521, session=SESSIONS_DIR / "very-small-remote-file.txt") as server:
        assert cli.subcommand_autopurge(server.api) == 0


# def test_purge_all_subcommand_fails():
#     with Aria2Server(port=7521) as server:
#         assert cli.subcommand_purge_all(server.api) == 0
