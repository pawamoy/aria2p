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

"""Tests for selecting downloads with patterns and field filters."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import Mock

import pytest

from aria2p import API, Client, Download


@pytest.fixture
def search_api() -> API:
    # Use each RPC download list so a search covers active, queued, and stopped downloads.
    client = Mock(spec=Client)
    structs = []
    for gid, name, status, length in [
        ("1", "linux.iso", "active", "1024"),
        ("2", "linux.iso.sig", "waiting", "128"),
        ("3", "forest sounds.flac", "paused", "1024"),
        ("4", "other.iso", "complete", "2048"),
    ]:
        structs.append(
            {
                "gid": gid,
                "status": status,
                "totalLength": length,
                "completedLength": "0",
                "downloadSpeed": "0",
                "uploadSpeed": "0",
                "dir": "/downloads",
                "files": [{"path": f"/downloads/{name}"}],
            }
        )
    client.tell_active.return_value = structs[:1]
    client.tell_waiting.return_value = structs[1:3]
    client.tell_stopped.return_value = structs[3:]
    return API(client)


@pytest.mark.parametrize(
    ("patterns", "expected_gids"),
    [
        (None, ["1", "2", "3", "4"]),
        ([], ["1", "2", "3", "4"]),
        (["linux"], ["1", "2"]),
        (["forest sounds"], ["3"]),
        (["linux", "other"], ["1", "2", "4"]),
        (["linux", "iso"], ["1", "2", "4"]),
        (["LINUX"], ["1", "2"]),
        ([".*"], ["1", "2", "3", "4"]),
        (["unknown"], []),
    ],
)
def test_search_name_patterns(search_api: API, patterns: list[str] | None, expected_gids: list[str]) -> None:
    matches = search_api.search(patterns)

    # Regex searches ignore case; overlapping matches appear only once in daemon order.
    assert [download.gid for download in matches] == expected_gids


@pytest.mark.parametrize(
    ("patterns", "expected_gids"),
    [
        ([r"\.iso$"], ["1", "4"]),
        ([r"^linux", r"flac$"], ["1", "2", "3"]),
        ([r"(?i)LINUX"], ["1", "2"]),
        ([r"(?-i:LINUX)"], []),
        ([r"(?-i:linux)"], ["1", "2"]),
        ([r"(?-i:linux)\.ISO$"], ["1"]),
        (["forest", r"\.iso$"], ["1", "3", "4"]),
        (["linux", r"\.iso$"], ["1", "2", "4"]),
        (["missing", r"\.iso$"], ["1", "4"]),
        ([r"^missing$"], []),
    ],
)
def test_search_regular_expressions(search_api: API, patterns: list[str], expected_gids: list[str]) -> None:
    matches = search_api.search(patterns)

    assert [download.gid for download in matches] == expected_gids


@pytest.mark.parametrize(
    ("filters", "expected_gids"),
    [
        ({"status": "waiting"}, ["2"]),
        ({"status": "PAUSED"}, []),
        ({"total_length": 1024}, ["1", "3"]),
        ({"total_length": "1024"}, ["1", "3"]),
        ({"is_paused": True}, ["3"]),
        ({"is_paused": "TRUE"}, ["3"]),
        ({"is_torrent": "false"}, ["1", "2", "3", "4"]),
        ({"dir": Path("/downloads")}, ["1", "2", "3", "4"]),
        ({"dir": "/downloads"}, ["1", "2", "3", "4"]),
        ({"name": "linux.iso"}, ["1"]),
        ({"error_code": None}, ["1", "2", "3", "4"]),
        ({"status": "paused", "total_length": 1024}, ["3"]),
        ({"status": "paused", "total_length": 2048}, []),
        ({"num_seeders": 0}, []),
    ],
)
def test_search_field_filters(search_api: API, filters: dict[str, object], expected_gids: list[str]) -> None:
    matches = search_api.search(filters=filters)

    # Missing optional fields cannot satisfy a filter; typed values and CLI strings can.
    assert [download.gid for download in matches] == expected_gids


def test_search_combines_patterns_and_filters(search_api: API) -> None:
    # One pattern matches the audio file; another matches two ISO files.
    matches = search_api.search(
        ["forest", r"\.iso$"],
        filters={"total_length": 1024, "is_paused": True},
    )

    # Only the audio file satisfies both filters, even though each ISO matches the regex.
    assert [download.gid for download in matches] == ["3"]


def test_search_existing_downloads_without_rpc() -> None:
    client = Mock(spec=Client)
    api = API(client)
    downloads = [Download(api, {"gid": "1", "status": "paused"})]

    matches = api.search(filters={"status": "paused"}, downloads=downloads)
    empty_matches = api.search(downloads=[])

    # An explicitly empty collection stays empty and never becomes a request for all downloads.
    assert matches == downloads
    assert empty_matches == []
    assert client.mock_calls == []


@pytest.mark.parametrize("field", ["statuz", "totalLength", "live", "options", "api", "pause", "__dict__"])
def test_search_rejects_unsupported_fields_before_rpc(field: str) -> None:
    client = Mock(spec=Client)
    api = API(client)

    with pytest.raises(ValueError, match="Unknown search field"):
        api.search(filters={field: "value"})

    assert client.mock_calls == []


def test_search_rejects_invalid_regex_before_rpc() -> None:
    client = Mock(spec=Client)
    api = API(client)

    with pytest.raises(ValueError, match="Invalid regular expression"):
        api.search(["["])

    assert client.mock_calls == []
