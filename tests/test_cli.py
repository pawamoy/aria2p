from unittest.mock import patch

from aria2p import cli

from . import Aria2Server


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
