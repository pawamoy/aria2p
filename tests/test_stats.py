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

"""Tests for the `stats` module."""

from __future__ import annotations

import pytest

from aria2p import Stats


@pytest.fixture(scope="module")
def stats() -> Stats:
    """Provide a Stats instance.

    Returns:
        A Stats instance.
    """
    return Stats(
        {
            "downloadSpeed": "0",
            "numActive": "0",
            "numStopped": "0",
            "numStoppedTotal": "0",
            "numWaiting": "0",
            "uploadSpeed": "0",
        },
    )


def test_download_speed(stats: Stats) -> None:
    """Test the `download_speed` property.

    Parameters:
        stats: A Stats instance.
    """
    assert stats.download_speed == 0


def test_download_speed_string(stats: Stats) -> None:
    """Test the `download_speed_string` method.

    Parameters:
        stats: A Stats instance.
    """
    assert stats.download_speed_string() == "0.00 B/s"


def test_download_speed_string_not_human_readable(stats: Stats) -> None:
    """Test the `download_speed_string` method with human readable option.

    Parameters:
        stats: A Stats instance.
    """
    assert stats.download_speed_string(human_readable=False) == "0 B/s"


def test_upload_speed(stats: Stats) -> None:
    """Test the `upload_speed` property.

    Parameters:
        stats: A Stats instance.
    """
    assert stats.upload_speed == 0


def test_upload_speed_string(stats: Stats) -> None:
    """Test the `upload_speed_string` method.

    Parameters:
        stats: A Stats instance.
    """
    assert stats.upload_speed_string() == "0.00 B/s"


def test_upload_speed_string_not_human_readable(stats: Stats) -> None:
    """Test the `upload_speed_string` method with human readable option.

    Parameters:
        stats: A Stats instance.
    """
    assert stats.upload_speed_string(human_readable=False) == "0 B/s"


def test_num_active(stats: Stats) -> None:
    """Test the `numnum_active_waiting` property.

    Parameters:
        stats: A Stats instance.
    """
    assert stats.num_active == 0


def test_num_stopped(stats: Stats) -> None:
    """Test the `num_stopped` property.

    Parameters:
        stats: A Stats instance.
    """
    assert stats.num_stopped == 0


def test_num_stopped_total(stats: Stats) -> None:
    """Test the `num_stopped_total` property.

    Parameters:
        stats: A Stats instance.
    """
    assert stats.num_stopped_total == 0


def test_num_waiting(stats: Stats) -> None:
    """Test the `num_waiting` property.

    Parameters:
        stats: A Stats instance.
    """
    assert stats.num_waiting == 0
