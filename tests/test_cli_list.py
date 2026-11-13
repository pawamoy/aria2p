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

"""Tests for selecting, ordering, and formatting downloads with the list command."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

# YORE: Bump 2: Replace `, show` with `` within line.
from aria2p import API, Client, Download, list_downloads, show
from aria2p._internal.cli.main import main
from tests.conftest import Aria2Server

if TYPE_CHECKING:
    from pathlib import Path


@pytest.fixture
def listed_downloads(monkeypatch: pytest.MonkeyPatch) -> list[Download]:
    # Keep daemon order different from name order, and speeds different numerically and lexically.
    api = API()
    downloads = []
    for gid, name, status, completed, speed in (
        ("0000000000000001", "Zebra.iso", "active", 1024, 1024),
        ("0000000000000002", "alpha.zip", "paused", 2048, 9),
        ("0000000000000003", "beta.iso", "paused", 2048, 100),
    ):
        downloads.append(
            Download(
                api,
                {
                    "gid": gid,
                    "status": status,
                    "dir": "/downloads",
                    "files": [
                        {
                            "index": "1",
                            "path": f"/downloads/{name}",
                            "length": "4096",
                            "completedLength": str(completed),
                            "selected": "true",
                            "uris": [],
                        }
                    ],
                    "totalLength": "4096",
                    "completedLength": str(completed),
                    "downloadSpeed": str(speed),
                    "uploadSpeed": "0",
                },
            )
        )

    monkeypatch.setattr(API, "get_downloads", lambda self: downloads)
    monkeypatch.setattr(Client, "get_version", lambda self: {})
    return downloads


@pytest.mark.usefixtures("listed_downloads")
def test_list_defaults_to_names(capsys: pytest.CaptureFixture) -> None:
    assert main(["list"]) == 0

    assert capsys.readouterr().out.splitlines() == ["Zebra.iso", "alpha.zip", "beta.iso"]


@pytest.mark.parametrize(
    ("patterns", "names"),
    [
        (["0000000000000002"], ["alpha.zip"]),
        (["*.iso"], ["Zebra.iso", "beta.iso"]),
        (["*.iso", "0000000000000001", "alpha.*"], ["Zebra.iso", "alpha.zip", "beta.iso"]),
        (["zebra.iso"], []),
        (["missing*"], []),
    ],
)
@pytest.mark.usefixtures("listed_downloads")
def test_list_selects_gids_and_patterns(capsys: pytest.CaptureFixture, patterns: list[str], names: list[str]) -> None:
    assert main(["list", *patterns]) == 0

    assert capsys.readouterr().out.splitlines() == names


@pytest.mark.usefixtures("listed_downloads")
def test_list_filters_then_sorts_then_limits(capsys: pytest.CaptureFixture) -> None:
    assert main(["list", "*.iso", "--sort=-progress,name", "--limit", "1"]) == 0

    assert capsys.readouterr().out == "beta.iso\n"


@pytest.mark.usefixtures("listed_downloads")
def test_list_sorts_multiple_fields(capsys: pytest.CaptureFixture) -> None:
    assert main(["list", "-s", "status,-name"]) == 0

    assert capsys.readouterr().out.splitlines() == ["Zebra.iso", "beta.iso", "alpha.zip"]


@pytest.mark.usefixtures("listed_downloads")
def test_list_sorts_raw_speeds_with_human_readable_output(capsys: pytest.CaptureFixture) -> None:
    assert main(["list", "-s", "download_speed", "-H", "-f", "{name} {download_speed}"]) == 0

    lines = capsys.readouterr().out.splitlines()
    assert [line.split()[0] for line in lines] == ["alpha.zip", "beta.iso", "Zebra.iso"]
    assert lines[-1] == "Zebra.iso 1.00 KiB/s"


@pytest.mark.parametrize("options", [["-l"], ["--long"], ["--format=long"]])
@pytest.mark.usefixtures("listed_downloads")
def test_list_long_format(capsys: pytest.CaptureFixture, options: list[str]) -> None:
    assert main(["list", *options]) == 0

    lines = capsys.readouterr().out.splitlines()
    assert lines[0].split() == ["GID", "STATUS", "PROGRESS", "DOWN_SPEED", "UP_SPEED", "ETA", "NAME"]
    assert lines[1].split() == ["0000000000000001", "active", "25.00%", "1024", "0", "3", "Zebra.iso"]
    assert len(lines) == 4


def test_list_gid_format(listed_downloads: list[Download], capsys: pytest.CaptureFixture) -> None:
    assert main(["list", "-f", "gid"]) == 0

    assert capsys.readouterr().out.splitlines() == [download.gid for download in listed_downloads]


@pytest.mark.usefixtures("listed_downloads")
def test_list_custom_format(capsys: pytest.CaptureFixture) -> None:
    assert (
        main(
            [
                "list",
                "0000000000000001",
                "-f",
                "{{{name}}} {total_length:d} {completed_length:d} {progress:.1f}% {eta}s",
            ]
        )
        == 0
    )

    assert capsys.readouterr().out == "{Zebra.iso} 4096 1024 25.0% 3s\n"


@pytest.mark.usefixtures("listed_downloads")
def test_list_human_readable_format(capsys: pytest.CaptureFixture) -> None:
    assert (
        main(
            [
                "list",
                "0000000000000001",
                "-H",
                "-f",
                "{total_length} {completed_length} {download_speed} {upload_speed} {eta}",
            ]
        )
        == 0
    )

    assert capsys.readouterr().out == "4.00 KiB 1.00 KiB 1.00 KiB/s 0.00 B/s 3s\n"


def test_list_unknown_eta(listed_downloads: list[Download], capsys: pytest.CaptureFixture) -> None:
    # A stopped transfer cannot estimate its remaining time.
    listed_downloads[0]._struct["downloadSpeed"] = "0"

    assert main(["list", "0000000000000001", "-f", "{eta}"]) == 0
    assert main(["list", "0000000000000001", "-H", "-f", "{eta}"]) == 0

    assert capsys.readouterr().out == "-\n-\n"


@pytest.mark.parametrize("options", [["--limit", "0"], ["missing*"]])
@pytest.mark.usefixtures("listed_downloads")
def test_list_empty_selection(capsys: pytest.CaptureFixture, options: list[str]) -> None:
    assert main(["list", *options]) == 0

    assert capsys.readouterr().out == ""


def test_list_empty_daemon(listed_downloads: list[Download], capsys: pytest.CaptureFixture) -> None:
    listed_downloads.clear()

    assert main(["list"]) == 0

    assert capsys.readouterr().out == ""


@pytest.mark.parametrize(
    ("options", "error"),
    [
        (["--limit=-1"], "limit must be zero or greater"),
        (["--sort=missing"], "unknown sort field"),
        (["--sort=name,"], "unknown sort field"),
        (["--format={missing}"], "unknown format field"),
        (["--format={name.upper}"], "unknown format field"),
        (["--format={"], "aria2p: list:"),
        (["--format={name:d}"], "invalid format"),
    ],
)
@pytest.mark.usefixtures("listed_downloads")
def test_list_invalid_options(capsys: pytest.CaptureFixture, options: list[str], error: str) -> None:
    assert main(["list", *options]) == 1

    captured = capsys.readouterr()
    assert captured.out == ""
    assert error in captured.err


def test_list_does_not_print_partial_output(listed_downloads: list[Download], capsys: pytest.CaptureFixture) -> None:
    # Formatting works for the first download but fails when another download has an unknown ETA.
    listed_downloads[1]._struct["downloadSpeed"] = "0"

    assert main(["list", "-f", "{eta:d}"]) == 1

    captured = capsys.readouterr()
    assert captured.out == ""
    assert "invalid format" in captured.err


@pytest.mark.usefixtures("listed_downloads")
def test_list_rejects_conflicting_formats(capsys: pytest.CaptureFixture) -> None:
    with pytest.raises(SystemExit) as error:
        main(["list", "-l", "-f", "gid"])

    assert error.value.code == 2
    assert "not allowed" in capsys.readouterr().err


@pytest.mark.usefixtures("listed_downloads")
def test_list_python_api(capsys: pytest.CaptureFixture) -> None:
    assert list_downloads(API(), ["*.zip"]) == 0

    assert capsys.readouterr().out == "alpha.zip\n"


# YORE: Bump 2: Remove block.
@pytest.mark.parametrize("empty", [False, True])
def test_show_warns_and_preserves_table_output(
    listed_downloads: list[Download], capsys: pytest.CaptureFixture, empty: bool
) -> None:
    # Both populated and empty tables remain available through the deprecated Python API.
    if empty:
        listed_downloads.clear()

    with pytest.warns(DeprecationWarning, match="'show'.*version 2.*'list -l -H'") as warnings:
        assert show(API()) == 0

    show_output = capsys.readouterr().out
    assert len(warnings) == 1
    assert warnings[0].filename == __file__

    # The recommended replacement produces the same table without a deprecation warning.
    assert main(["list", "-l", "-H"]) == 0

    assert capsys.readouterr().out == show_output


def test_main_list_with_daemon(tmp_path: Path, port: int, capsys: pytest.CaptureFixture) -> None:
    with Aria2Server(tmp_path, port, session="1-dl-paused.txt") as server:
        assert main(["-p", str(server.port), "list", "-f", "{gid} {status}"]) == 0

    assert capsys.readouterr().out == "0000000000000001 paused\n"
