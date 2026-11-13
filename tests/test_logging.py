# SPDX-License-Identifier: ISC
#
# ISC License
#
# Copyright (c) 2020, Timothée Mazzucotelli and contributors
#
# Permission to use, copy, modify, and/or distribute this software for any
# purpose with or without fee is hereby granted, provided that the above
# copyright notice and this permission notice appear in all copies.
#
# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
# WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
# ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
# WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
# ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
# OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING
from unittest.mock import Mock

import pytest
import requests
from loguru import logger

from aria2p import API, Client, ClientException, Download, enable_logger
from aria2p._internal.cli.commands.add_magnet import add_magnets
from aria2p._internal.cli.commands.add_metalink import add_metalinks
from aria2p._internal.cli.commands.add_torrent import add_torrents
from aria2p._internal.cli.commands.pause import pause
from aria2p._internal.cli.commands.remove import remove
from aria2p._internal.cli.commands.resume import resume
from aria2p._internal.cli.main import main
from aria2p._internal.interface import _Interface

if TYPE_CHECKING:
    from collections.abc import Callable


@pytest.fixture
def log_file(tmp_path: Path) -> Path:
    log_path = tmp_path / "aria2p.log"
    enable_logger(sink=str(log_path), level="TRACE")
    return log_path


@pytest.mark.parametrize("log_level", [None, "WARNING", "ERROR"])
def test_deprecation_warning_is_printed_independently_of_logging(
    log_level: str | None,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture,
) -> None:
    # No daemon is needed to report the deprecated command-line option.
    monkeypatch.setattr(Client, "get_version", Mock(return_value={}))
    log_path = tmp_path / "aria2p.log"
    args = ["add", "--from-file", "downloads.txt"]
    if log_level is None:
        logger.disable("aria2p")
    else:
        args = ["--log-path", str(log_path), "--log-level", log_level, *args]

    try:
        exit_code = main(args)
    finally:
        logger.enable("aria2p")

    captured = capsys.readouterr()
    warning = "Deprecation warning: every URI that is a valid file-path and is not a torrent or a metalink is now read as an input file."
    assert exit_code == 1
    assert captured.out == ""
    assert captured.err == f"{warning}\nNo new download was created\n"

    # A file sink and its level must not control the user-facing warning.
    if log_level is not None:
        logs = log_path.read_text()
        assert (warning in logs) == (log_level == "WARNING")
        if log_level == "WARNING":
            assert "WARNING" in logs


def test_connection_failure_is_logged_and_printed(
    log_file: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture,
) -> None:
    monkeypatch.setattr(Client, "get_version", Mock(side_effect=requests.ConnectionError("connection refused")))

    exit_code = main(["show"])

    captured = capsys.readouterr()
    logs = log_file.read_text()
    assert exit_code == 2
    assert captured.out == ""
    assert "[ERROR] connection refused" in captured.err
    assert "Please make sure" in captured.err
    assert "Could not connect to aria2: connection refused" in logs
    assert "ConnectionError" in logs


def test_command_failure_is_logged_and_printed(
    log_file: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture,
) -> None:
    monkeypatch.setattr(Client, "get_version", Mock(return_value={}))
    monkeypatch.setattr(Client, "call", Mock(side_effect=ClientException(1, "Invalid GID")))

    exit_code = main(["call", "tellstatus", "-P", "invalid"])

    captured = capsys.readouterr()
    assert exit_code == 1
    assert captured.out == ""
    assert captured.err == "Invalid GID\n"
    assert "Command 'call' failed: Invalid GID" in log_file.read_text()


@pytest.mark.parametrize("command", [add_magnets, add_torrents, add_metalinks])
def test_unreadable_input_file_is_logged_and_printed(
    command: Callable[..., int],
    log_file: Path,
    tmp_path: Path,
    capsys: pytest.CaptureFixture,
) -> None:
    missing_file = tmp_path / "missing.txt"

    exit_code = command(API(), from_file=str(missing_file))

    captured = capsys.readouterr()
    logs = log_file.read_text()
    assert exit_code == 1
    assert captured.out == ""
    assert captured.err == f"Cannot open file: {missing_file}\n"
    assert f"Cannot read input file '{missing_file}'" in logs
    assert "FileNotFoundError" in logs


@pytest.mark.parametrize(("command", "operation"), [(pause, "pause"), (resume, "resume"), (remove, "remove")])
def test_download_lookup_failure_is_logged_and_printed(
    command: Callable[..., int],
    operation: str,
    log_file: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture,
) -> None:
    monkeypatch.setattr(API, "get_downloads", Mock(side_effect=ClientException(1, "Invalid GID")))

    exit_code = command(API(), gids=["invalid"])

    captured = capsys.readouterr()
    assert exit_code == 1
    assert captured.out == ""
    assert captured.err == "Invalid GID\n"
    assert f"Could not get downloads to {operation}: Invalid GID" in log_file.read_text()


def test_theme_failure_is_logged_without_interrupting_resize(
    log_file: Path,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture,
) -> None:
    # A missing optional theme must not prevent the interface from resizing.
    monkeypatch.setattr(Path, "home", Mock(return_value=tmp_path))

    _Interface().post_resize()

    captured = capsys.readouterr()
    logs = log_file.read_text()
    assert captured.out == captured.err == ""
    assert "Could not re-apply pywal color theme" in logs
    assert str(tmp_path / ".cache" / "wal" / "sequences") in logs
    assert "FileNotFoundError" in logs


def test_retry_without_uri_is_logged(log_file: Path) -> None:
    download = Download(API(), {"gid": "0000000000000001", "status": "error", "files": []})

    results = API().retry_downloads([download])

    assert results == []
    assert f"Cannot retry download {download.gid}: no URI available" in log_file.read_text()


def test_failed_retry_is_logged(log_file: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    download = Download(
        API(),
        {"gid": "0000000000000001", "status": "error", "files": [{"uris": [{"uri": "https://example.com/file"}]}]},
    )
    error = ClientException(1, "Could not add URI")
    monkeypatch.setattr(Download, "options", property(lambda self: {}))
    monkeypatch.setattr(API, "add_uris", Mock(side_effect=error))

    results = API().retry_downloads([download])

    assert results == [error]
    assert f"Failed to retry download {download.gid}: Could not add URI" in log_file.read_text()
