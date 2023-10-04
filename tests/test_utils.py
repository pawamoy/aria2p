"""Tests for the `utils` module."""

from __future__ import annotations

from datetime import timedelta
from typing import Any

import pytest

from aria2p.utils import bool_or_value, bool_to_str, human_readable_bytes, human_readable_timedelta


@pytest.mark.parametrize(
    ("args", "kwargs", "expected"),
    [
        ([0], {}, "0.00B"),
        ([0], {"digits": 0}, "0B"),
        ([0], {"digits": 0, "delim": " "}, "0 B"),
        ([0], {"digits": 0, "delim": " ", "postfix": "/s"}, "0 B/s"),
        ([1024], {"digits": 0, "delim": " ", "postfix": "/s"}, "1 KiB/s"),
        ([2048], {}, "2.00KiB"),
        ([2048 * 1024], {}, "2.00MiB"),
        ([2048 * 1024 * 1024], {}, "2.00GiB"),
        ([2048 * 1024 * 1024 * 1024], {}, "2.00TiB"),
    ],
)
def test_human_readable_bytes(args: list[int], kwargs: Any, expected: str) -> None:
    """Test the `human_readable_bytes` function.

    Parameters:
        args: Positional arguments passed to the function.
        kwargs: Keyword arguments passed to the function.
        expected: The expected result.
    """
    assert human_readable_bytes(*args, **kwargs) == expected


@pytest.mark.parametrize(
    ("td", "expected"),
    [
        (timedelta(seconds=0), "0s"),
        (timedelta(seconds=1), "1s"),
        (timedelta(seconds=75), "1m15s"),
        (timedelta(seconds=3601), "1h1s"),
        (timedelta(seconds=3600 * 24 + 2), "1d2s"),
        (timedelta(days=1, seconds=3600 * 24 + 2), "2d2s"),
        (timedelta(days=3, seconds=3), "3d3s"),
        (timedelta(days=3), "3d"),
        (timedelta(seconds=3600 * 3), "3h"),
        (timedelta(seconds=60 * 3), "3m"),
    ],
)
def test_human_readable_timedelta_force_print_0_seconds(td: timedelta, expected: str) -> None:
    """Test the `human_readable_timedelta` function.

    Parameters:
        td: A timedelta.
        expected: The expected result.
    """
    assert human_readable_timedelta(td) == expected


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("true", True),
        ("false", False),
        ("mem", "mem"),
        (None, None),
        (0, 0),
        (1, 1),
    ],
)
def test_bool_or_value_true_is_true(value: str | int | None, expected: bool | str | int | None) -> None:
    """Test the `bool_or_value` function.

    Parameters:
        value: Value passed to the function.
        expected: The expected result.
    """
    assert bool_or_value(value) == expected


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (True, "true"),
        (False, "false"),
        (None, None),
        (0, 0),
        (1, 1),
    ],
)
def test_bool_to_str_true_gives_true(value: bool | int | None, expected: str | int | None) -> None:
    """Test the `bool_to_str` function.

    Parameters:
        value: Value passed to the function.
        expected: The expected result.
    """
    assert bool_to_str(value) == expected
