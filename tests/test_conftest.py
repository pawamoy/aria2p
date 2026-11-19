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

"""Tests for integration fixture diagnostics."""

from __future__ import annotations

from typing import TYPE_CHECKING
from unittest.mock import Mock

import pytest

from tests.conftest import Aria2Server

if TYPE_CHECKING:
    from pathlib import Path


def test_download_timeout_reports_last_status_and_daemon_output(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    # The download starts while polling, but does not finish before the deadline.
    server = Aria2Server(tmp_path, port=6800)
    initial_status = {
        "gid": "0000000000000001",
        "status": "waiting",
        "completedLength": "0",
        "totalLength": "100",
        "downloadSpeed": "0",
    }
    last_status = {
        **initial_status,
        "status": "active",
        "completedLength": "64",
        "downloadSpeed": "32",
        "errorCode": "2",
        "errorMessage": "Retrying connection",
    }
    monkeypatch.setattr(server.client, "tell_status", Mock(side_effect=[initial_status, last_status]))

    # Non-UTF-8 daemon output must not hide the original timeout.
    server.log_path = tmp_path / "daemon.log"
    server.log_path.write_bytes(b"Retrying HTTP request\n\xff\n")

    with pytest.raises(TimeoutError) as error:
        server.wait_for_download(timeout=0)

    message = str(error.value)
    assert "Download 0000000000000001 did not reach 'complete' within 0 seconds" in message
    assert "Last status: active" in message
    assert "completed: 64 bytes" in message
    assert "total: 100 bytes" in message
    assert "speed: 32 bytes/s" in message
    assert "error code: '2'" in message
    assert "error message: 'Retrying connection'" in message
    assert str(server.log_path) in message
    assert "Retrying HTTP request\n\ufffd\n" in message
