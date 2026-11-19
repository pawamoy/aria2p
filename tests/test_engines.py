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

"""Tests for engine detection and the shared public API."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING
from unittest.mock import Mock

import pytest
from requests.exceptions import ConnectionError  # noqa: A004

from aria2p import API, Client, ClientException, Download, Options

if TYPE_CHECKING:
    from tests.conftest import Aria2Server


@pytest.fixture
def next_api(monkeypatch: pytest.MonkeyPatch) -> API:
    client = Client()
    monkeypatch.setattr(client, "get_version", lambda: {"product": "aria2-next", "version": "3.1.0"})
    return API(client)


def test_detection_is_lazy_and_cached_for_the_connection(monkeypatch: pytest.MonkeyPatch) -> None:
    version = Mock(return_value={"version": "1.37.0"})
    client = Client()
    monkeypatch.setattr(client, "get_version", version)

    api = API(client)
    version.assert_not_called()

    assert api.engine.name == "aria2"
    assert api.engine.version == "1.37.0"
    assert api.engine.capabilities.control_files
    assert api.engine.capabilities.ftp
    assert api.engine.capabilities.metalink3
    assert not api.engine.capabilities.move_download
    version.assert_called_once_with()

    # A different endpoint must not inherit the previous daemon's capabilities.
    client.port += 1
    version.return_value = {"product": "aria2-next", "version": "3.1.0"}

    assert api.engine.name == "aria2-next"
    assert api.engine.capabilities.move_download
    assert not api.engine.capabilities.control_files
    assert not api.engine.capabilities.ftp
    assert not api.engine.capabilities.metalink3
    assert version.call_count == 2


@pytest.mark.parametrize("initial_engine", ["aria2", "aria2-next"])
def test_check_engine_detects_a_replacement_engine_at_the_same_endpoint(
    monkeypatch: pytest.MonkeyPatch, initial_engine: str
) -> None:
    versions = {"aria2": {"version": "1.37.0"}, "aria2-next": {"product": "aria2-next", "version": "3.1.0"}}
    replacement_engine = "aria2-next" if initial_engine == "aria2" else "aria2"
    version = Mock(return_value=versions[initial_engine])
    client = Client()
    monkeypatch.setattr(client, "get_version", version)
    change = Mock(return_value="OK")
    monkeypatch.setattr(client, "change_global_option", change)
    api = API(client)
    assert api.engine.name == initial_engine

    # Replace the daemon without changing the client's endpoint or credentials.
    version.return_value = versions[replacement_engine]
    engine = api.check_engine()

    assert engine.name == replacement_engine
    assert engine.capabilities.move_download is (replacement_engine == "aria2-next")
    assert engine.capabilities.ftp is (replacement_engine == "aria2")
    assert api.engine is engine
    assert version.call_count == 2

    # Option validation must use the replacement engine's limits.
    if replacement_engine == "aria2-next":
        assert api.set_global_options({"max-connection-per-server": 32})
        change.assert_called_once_with({"max-connection-per-server": "32"})
    else:
        with pytest.raises(ValueError, match="max-connection-per-server"):
            api.set_global_options({"max-connection-per-server": 32})

        change.assert_not_called()


@pytest.mark.parametrize(
    "failure", [ConnectionError("Server is stopped"), {"product": "aria2-next", "version": "3.0.9"}]
)
def test_failed_check_engine_discards_stale_engine_and_allows_retry(
    monkeypatch: pytest.MonkeyPatch, failure: Exception | dict
) -> None:
    version = Mock(side_effect=[{"version": "1.37.0"}, failure, {"product": "aria2-next", "version": "3.1.0"}])
    client = Client()
    monkeypatch.setattr(client, "get_version", version)
    api = API(client)
    assert api.engine.name == "aria2"

    # A stopped or unsupported replacement daemon must not leave the old engine cached.
    with pytest.raises(ConnectionError if isinstance(failure, Exception) else ValueError):
        api.check_engine()

    # Once a supported daemon is ready, ordinary access retries discovery.
    assert api.engine.name == "aria2-next"
    assert api.engine.capabilities.move_download
    assert version.call_count == 3


@pytest.mark.parametrize("version", ["2.8.6", "3.0.9", "3.1.0-rc1", "invalid"])
def test_unsupported_next_versions_fail_before_changing_downloads(
    monkeypatch: pytest.MonkeyPatch, version: str
) -> None:
    client = Client()
    monkeypatch.setattr(client, "get_version", lambda: {"product": "aria2-next", "version": version})
    change = Mock()
    monkeypatch.setattr(client, "change_global_option", change)

    with pytest.raises(ValueError, match=r"3\.1\.0 or later"):
        API(client).set_global_options({"max-download-limit": 1000})

    change.assert_not_called()


@pytest.mark.parametrize("version", ["3.1.0", "3.2.0", "3.10.0", "4.0.0", "3.1.0+build"])
def test_next_supported_versions(monkeypatch: pytest.MonkeyPatch, version: str) -> None:
    client = Client()
    monkeypatch.setattr(client, "get_version", lambda: {"product": "aria2-next", "version": version})

    assert API(client).engine.capabilities.move_download


@pytest.mark.parametrize(
    "options",
    [{"always-resume": True}, {"piece-length": "1M"}, {"max-resume-failure-tries": 10}, {"ftp-passwd": "private"}],
)
def test_unsupported_next_options_fail_without_rpc_writes(
    next_api: API, monkeypatch: pytest.MonkeyPatch, options: dict
) -> None:
    add = Mock()
    monkeypatch.setattr(next_api.client, "add_uri", add)

    with pytest.raises(ValueError, match="unsupported by aria2-next") as error:
        next_api.add_uris(["https://example.org/file"], options)

    # Error messages name the option but never expose credential values.
    assert "private" not in str(error.value)
    add.assert_not_called()


@pytest.mark.parametrize("scope", ["initial", "download", "global"])
def test_next_header_updates_keep_all_values(next_api: API, monkeypatch: pytest.MonkeyPatch, scope: str) -> None:
    rpc = Mock(return_value="OK")
    monkeypatch.setattr(next_api.client, "call", rpc)
    headers = ["Accept: */*", "User-Agent: aria2p"]

    if scope == "initial":
        rpc.side_effect = ["0123456789abcdef", {"gid": "0123456789abcdef"}]
        next_api.add_uris(["https://example.org/file"], {"header": headers})
        sent_options = rpc.call_args_list[0].kwargs["params"][1]
    elif scope == "download":
        next_api.set_options({"header": headers}, ["0123456789abcdef"])
        sent_options = rpc.call_args.args[1][1]
    else:
        options = Options(next_api, {})
        options.header = headers
        sent_options = rpc.call_args.args[1][0]
        assert options.header == headers

    assert sent_options == {"header": "Accept: */*\nUser-Agent: aria2p"}
    assert headers == ["Accept: */*", "User-Agent: aria2p"]


@pytest.mark.parametrize(
    ("name", "value", "expected"),
    [
        ("max-connection-per-server", 256, {"max-connection-per-server": "256"}),
        ("min-split-size", "16K", {"min-split-size": "16K"}),
        ("bt-require-crypto", True, {"bt-encryption": "required"}),
        ("bt-force-encryption", False, {"bt-encryption": "preferred"}),
        ("bt-encryption", "disabled", {"bt-encryption": "disabled"}),
    ],
)
def test_next_option_values_and_aliases(
    next_api: API, monkeypatch: pytest.MonkeyPatch, name: str, value: str | bool | int, expected: dict
) -> None:
    change = Mock(return_value="OK")
    monkeypatch.setattr(next_api.client, "change_global_option", change)
    options = Options(next_api, {})

    assert options.set(name, value)

    change.assert_called_once_with(expected)


@pytest.mark.parametrize("value", [0, 257])
def test_next_connection_limit_bounds(next_api: API, value: int) -> None:
    with pytest.raises(ValueError, match="max-connection-per-server"):
        next_api.set_global_options({"max-connection-per-server": value})


def test_next_rejects_ftp_before_adding_a_task(next_api: API, monkeypatch: pytest.MonkeyPatch) -> None:
    add = Mock()
    monkeypatch.setattr(next_api.client, "add_uri", add)

    with pytest.raises(ValueError, match="FTP downloads are unsupported"):
        next_api.add_uris(["ftp://example.org/file"])

    add.assert_not_called()


def test_metalink3_capability(server: Aria2Server) -> None:
    # Keep coverage for legacy Metalink documents alongside the shared v4 fixture.
    path = Path(__file__).parent / "data" / "debian.metalink"

    if server.api.engine.capabilities.metalink3:
        assert server.api.add_metalink(path, options={"pause": True})
    else:
        with pytest.raises(ValueError, match="Metalink 3 is unsupported"):
            server.api.add_metalink(path, options={"pause": True})


def test_remove_only_cleans_control_files_for_engines_that_use_them(server: Aria2Server) -> None:
    download = server.api.add_uris(["http://127.0.0.1:8779/64k"], {"pause": True, "out": "file.txt"})
    control_file = download.control_file_path
    control_file.write_bytes(b"existing adjacent file")

    assert server.api.remove([download]) == [True]

    assert control_file.exists() is not server.api.engine.capabilities.control_files


def test_native_move_failure_preserves_the_download(
    next_api: API, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    source = tmp_path / "file.txt"
    source.write_bytes(b"partial download")
    struct = {"gid": "0123456789abcdef", "status": "paused", "dir": str(tmp_path), "files": [{"path": str(source)}]}
    download = Download(next_api, struct)
    monkeypatch.setattr(next_api.client, "tell_status", lambda gid: struct)
    move = Mock(side_effect=ClientException(1, "Cannot move download"))
    monkeypatch.setattr(next_api.client, "move_download", move)

    with pytest.raises(ClientException, match="Cannot move download"):
        download.move_files(tmp_path / "destination", force=True)

    assert source.read_bytes() == b"partial download"
    assert download.dir == tmp_path
    assert download.is_paused


def test_low_level_move_method_is_explicit_and_preserves_rpc_errors(monkeypatch: pytest.MonkeyPatch) -> None:
    client = Client()
    rpc = Mock(side_effect=ClientException(-32601, "moveDownload"))
    monkeypatch.setattr(client, "call", rpc)

    with pytest.raises(ClientException, match="moveDownload"):
        client.move_download("0123456789abcdef", Path("/downloads"))

    rpc.assert_called_once_with(Client.MOVE_DOWNLOAD, ["0123456789abcdef", str(Path("/downloads"))])


def test_invalid_option_names_do_not_require_a_running_daemon(monkeypatch: pytest.MonkeyPatch) -> None:
    client = Client()
    version = Mock(side_effect=AssertionError("Invalid names must fail before discovery"))
    monkeypatch.setattr(client, "get_version", version)

    with pytest.raises(ValueError, match="unknown-option"):
        API(client).set_global_options({"unknown-option": True})

    version.assert_not_called()


def test_conflicting_encryption_options_fail_without_rpc_writes(next_api: API, monkeypatch: pytest.MonkeyPatch) -> None:
    change = Mock()
    monkeypatch.setattr(next_api.client, "change_global_option", change)

    with pytest.raises(ValueError, match="Do not combine"):
        next_api.set_global_options({"bt-encryption": "disabled", "bt-require-crypto": True})

    change.assert_not_called()


def test_encryption_aliases_share_the_native_policy(next_api: API, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(next_api.client, "change_global_option", lambda options: "OK")
    options = Options(next_api, {"bt-encryption": "required"})

    assert options.bt_require_crypto is True
    assert options.bt_force_encryption is True

    options.bt_require_crypto = False

    assert options.bt_require_crypto is False
    assert options.bt_force_encryption is False
    assert options.get("bt-encryption") == "preferred"
    assert options.get_struct() == {"bt-encryption": "preferred"}

    assert next_api.set_global_options(options)
