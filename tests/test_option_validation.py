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

"""Option validation through the public API and Options setters."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Any
from unittest.mock import Mock, call

import pytest

from aria2p import API, Client, ClientException, Download, Options

if TYPE_CHECKING:
    from tests.conftest import Aria2Server


@pytest.fixture
def api_and_rpc(monkeypatch: pytest.MonkeyPatch) -> tuple[API, Mock]:
    client = Client()
    rpc = Mock(return_value="OK")
    monkeypatch.setattr(client, "call", rpc)

    return API(client), rpc


@pytest.mark.parametrize(
    ("name", "value"),
    [
        ("unknown-option", "true"),
        ("--split", "1"),
        ("max_download_limit", "1"),
        ("check-integrity", ""),
        ("check-integrity", "True"),
        ("check-integrity", 1),
        ("split", 0),
        ("split", True),
        ("split", 1.5),
        ("split", 2**63),
        ("max-connection-per-server", 17),
        ("timeout", 0),
        ("timeout", 601),
        ("retry-wait", -1),
        ("max-download-limit", -1),
        ("max-download-limit", "1MB"),
        ("max-download-limit", "unlimited"),
        ("min-split-size", "1023K"),
        ("min-split-size", "1025M"),
        ("file-allocation", "invalid"),
        ("ftp-type", "invalid"),
        ("follow-torrent", "invalid"),
        ("log-level", "verbose"),
        ("proxy-method", "invalid"),
        ("uri-selector", "invalid"),
        ("seed-ratio", -0.1),
        ("seed-time", float("nan")),
        ("seed-time", float("inf")),
        ("gid", "0" * 16),
        ("gid", "invalid"),
        ("ssh-host-key-md", "invalid"),
        ("bt-prioritize-piece", "middle"),
        ("bt-prioritize-piece", "head=oops"),
        ("bt-external-ip", "invalid"),
        ("http-proxy", "http://proxy:invalid"),
        ("http-proxy", "socks5://proxy"),
        ("optimize-concurrent-downloads", "1:2:3"),
        ("optimize-concurrent-downloads", "nan:1"),
        ("dir", None),
        ("dir", {"invalid": "type"}),
        ("dir", ["/downloads"]),
        ("header", [1]),
        ("header", ("Accept: */*",)),
        ("user-agent", Path("aria2p")),
    ],
)
def test_invalid_values_leave_remote_and_local_options_unchanged(
    api_and_rpc: tuple[API, Mock], name: str, value: Any
) -> None:
    api, rpc = api_and_rpc
    options = Options(api, {"split": "5"})

    with pytest.raises(ValueError, match=name):
        options.set(name, value)

    # Reject the value before RPC and before updating the local cache.
    rpc.assert_not_called()
    assert options.get_struct() == {"split": "5"}


@pytest.mark.parametrize(
    ("name", "value", "expected"),
    [
        ("check-integrity", True, "true"),
        ("check-integrity", False, "false"),
        ("check-integrity", "false", "false"),
        ("split", 1, "1"),
        ("split", 2**32, str(2**32)),
        ("max-connection-per-server", 16, "16"),
        ("timeout", 600, "600"),
        ("max-download-limit", 0, "0"),
        ("max-download-limit", "20K", "20K"),
        ("min-split-size", "1M", "1M"),
        ("min-split-size", "1024M", "1024M"),
        ("seed-ratio", 1.5, "1.5"),
        ("seed-time", 0, "0"),
        ("follow-torrent", "mem", "mem"),
        ("gid", "0123456789abcdef", "0123456789abcdef"),
        ("bt-external-ip", "::1", "::1"),
        ("bt-prioritize-piece", "head=1M,tail", "head=1M,tail"),
        ("optimize-concurrent-downloads", "5:25", "5:25"),
        ("http-proxy", "proxy.example:8080", "proxy.example:8080"),
        ("http-proxy", "", ""),
        ("log", "", ""),
        ("http-passwd", "", ""),
        ("dir", "/path/on/remote/server", "/path/on/remote/server"),
        ("dir", Path("/path/on/remote/server"), "/path/on/remote/server"),
        ("header", ["Accept: */*", "User-Agent: aria2p"], ["Accept: */*", "User-Agent: aria2p"]),
        ("header", [], []),
    ],
)
def test_valid_values_are_serialized_for_rpc(
    api_and_rpc: tuple[API, Mock], name: str, value: Any, expected: Any
) -> None:
    api, rpc = api_and_rpc
    options = Options(api, {})

    assert options.set(name, value)

    rpc.assert_called_once_with(Client.CHANGE_GLOBAL_OPTION, [{name: expected}])
    assert options.get(name) == expected


@pytest.mark.parametrize("name", ["checksum", "index-out", "out", "pause", "select-file"])
def test_download_only_options_cannot_change_global_defaults(api_and_rpc: tuple[API, Mock], name: str) -> None:
    api, rpc = api_and_rpc

    with pytest.raises(ValueError, match=name):
        api.set_global_options({name: "unused"})

    rpc.assert_not_called()


@pytest.mark.parametrize(
    "name",
    [
        "bt-max-open-files",
        "download-result",
        "keep-unfinished-download-result",
        "log",
        "log-level",
        "max-concurrent-downloads",
        "max-download-result",
        "max-overall-download-limit",
        "max-overall-upload-limit",
        "optimize-concurrent-downloads",
        "save-cookies",
        "save-session",
        "server-stat-of",
        "dry-run",
        "metalink-base-uri",
        "parameterized-uri",
        "pause",
        "piece-length",
        "rpc-save-upload-metadata",
        "enable-rpc",
        "rpc-listen-port",
        "input-file",
    ],
)
def test_unavailable_download_options_are_rejected(api_and_rpc: tuple[API, Mock], name: str) -> None:
    api, rpc = api_and_rpc

    with pytest.raises(ValueError, match=name):
        api.set_options({name: "unused"}, ["0123456789abcdef"])

    rpc.assert_not_called()


@pytest.mark.parametrize("value", ["0", "3-1", "1048577", "1,a", ""])
def test_invalid_file_selection(api_and_rpc: tuple[API, Mock], value: str) -> None:
    api, rpc = api_and_rpc

    with pytest.raises(ValueError, match="select-file"):
        api.set_options({"select-file": value}, ["0123456789abcdef"])

    rpc.assert_not_called()


@pytest.mark.parametrize("value", [["0=file"], ["1="], ["invalid"], ["1=valid", "invalid"]])
def test_invalid_repeated_file_paths(api_and_rpc: tuple[API, Mock], value: list[str]) -> None:
    api, rpc = api_and_rpc

    with pytest.raises(ValueError, match="index-out"):
        api.set_options({"index-out": value}, ["0123456789abcdef"])

    rpc.assert_not_called()


@pytest.mark.parametrize(
    ("name", "value"),
    [("select-file", "1,3-5"), ("checksum", "sha-1=" + "0" * 40), ("out", "download.iso")],
)
def test_download_only_values(api_and_rpc: tuple[API, Mock], name: str, value: str) -> None:
    api, rpc = api_and_rpc

    assert api.set_options({name: value}, ["0123456789abcdef"]) == [True]

    rpc.assert_called_once_with(Client.CHANGE_OPTION, ["0123456789abcdef", {name: value}])


def test_repeated_file_paths_are_preserved(api_and_rpc: tuple[API, Mock]) -> None:
    api, rpc = api_and_rpc
    download = Download(api, {"gid": "0123456789abcdef"})
    options = Options(api, {}, download)
    paths = ["1=first.iso", "2=second.iso"]

    options.index_out = paths
    paths.append("3=third.iso")

    # Keep a snapshot of the submitted list, independent of caller mutations.
    rpc.assert_called_once_with(Client.CHANGE_OPTION, [download.gid, {"index-out": ["1=first.iso", "2=second.iso"]}])
    assert options.index_out == ["1=first.iso", "2=second.iso"]


def test_entire_batch_is_validated_before_changing_any_download(api_and_rpc: tuple[API, Mock]) -> None:
    api, rpc = api_and_rpc
    options = {"split": 2, "timeout": -1}

    with pytest.raises(ValueError, match="timeout"):
        api.set_options(options, ["0123456789abcdef", "fedcba9876543210"])

    rpc.assert_not_called()
    assert options == {"split": 2, "timeout": -1}


def test_options_objects_are_validated_and_input_is_preserved(api_and_rpc: tuple[API, Mock]) -> None:
    api, rpc = api_and_rpc
    options = Options(api, {"split": 2, "check-integrity": True})

    assert api.set_global_options(options)

    rpc.assert_called_once_with(Client.CHANGE_GLOBAL_OPTION, [{"split": "2", "check-integrity": "true"}])
    assert options.get_struct() == {"split": 2, "check-integrity": True}


@pytest.mark.parametrize("method", ["add_magnet", "add_uris", "add_torrent", "add_metalink"])
def test_invalid_creation_options_are_rejected_before_rpc_or_file_access(
    api_and_rpc: tuple[API, Mock], method: str
) -> None:
    api, rpc = api_and_rpc

    with pytest.raises(ValueError, match="max-concurrent-downloads"):
        getattr(api, method)("unused", options={"max-concurrent-downloads": 1})

    rpc.assert_not_called()


@pytest.mark.parametrize("path_type", [str, Path])
def test_creation_options_allow_pause_and_piece_length(
    api_and_rpc: tuple[API, Mock], path_type: type[str | Path]
) -> None:
    api, rpc = api_and_rpc
    rpc.side_effect = ["0123456789abcdef", {"gid": "0123456789abcdef"}]
    options = {"pause": True, "piece-length": "1M", "out": path_type("download.iso")}

    download = api.add_uris(["http://example.org/file"], options=options)

    assert download.gid == "0123456789abcdef"
    assert rpc.call_args_list[0] == call(
        Client.ADD_URI,
        params=[["http://example.org/file"], {"pause": "true", "piece-length": "1M", "out": "download.iso"}, None],
    )
    assert options["pause"] is True
    assert isinstance(options["out"], path_type)


def test_size_and_float_properties_return_python_numbers(api_and_rpc: tuple[API, Mock]) -> None:
    api, _ = api_and_rpc
    options = Options(api, {})

    options.set("max-download-limit", "20K")
    options.seed_ratio = 1.5

    assert options.max_download_limit == 20 * 1024
    assert options.seed_ratio == 1.5


def test_rpc_failure_leaves_local_values_unchanged(api_and_rpc: tuple[API, Mock]) -> None:
    api, rpc = api_and_rpc
    rpc.side_effect = ClientException(1, "Failure")
    options = Options(api, {"split": "5"})

    with pytest.raises(ClientException):
        options.set("split", 2)

    assert options.get("split") == "5"


@pytest.mark.parametrize(
    ("property_name", "option_name"),
    [
        ("bt_enable_hook_after_hash_check", "bt-enable-hook-after-hash-check"),
        ("metalink_enable_unique_protocol", "metalink-enable-unique-protocol"),
        ("keep_unfinished_download_result", "keep-unfinished-download-result"),
    ],
)
def test_properties_send_dashed_option_names(
    api_and_rpc: tuple[API, Mock], property_name: str, option_name: str
) -> None:
    api, rpc = api_and_rpc
    options = Options(api, {})

    setattr(options, property_name, True)

    rpc.assert_called_once_with(Client.CHANGE_GLOBAL_OPTION, [{option_name: "true"}])
    assert getattr(options, property_name) is True


def test_validated_options_with_daemon(server: Aria2Server, tmp_path: Path) -> None:
    # Create a paused download so no external network connection is needed.
    download = server.api.add_uris(
        ["http://localhost:8779/1024"], options={"pause": True, "out": Path("file"), "dir": tmp_path}
    )
    options = download.options

    assert download.dir == tmp_path
    assert download.files[0].path == tmp_path / "file"

    options.out = Path("renamed")
    assert options.set("max-download-limit", "20K")
    options.check_integrity = True
    options.header = ["Accept: */*", "User-Agent: aria2p"]

    remote_options = server.api.get_options([download])[0]
    assert remote_options.out == "renamed"
    assert remote_options.max_download_limit == 20 * 1024
    assert remote_options.check_integrity is True
    assert "Accept: */*" in remote_options.header
    assert "User-Agent: aria2p" in remote_options.header

    # An invalid update cannot replace either the cached or remote value.
    with pytest.raises(ValueError, match="max-download-limit"):
        options.set("max-download-limit", -1)

    assert options.max_download_limit == 20 * 1024
    assert server.api.get_options([download])[0].max_download_limit == 20 * 1024
