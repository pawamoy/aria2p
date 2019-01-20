from datetime import timedelta

from aria2p.utils import human_readable_bytes, human_readable_timedelta, bool_or_value, bool_to_str


def test_human_readable_bytes():
    assert human_readable_bytes(0) == "0.00B"
    assert human_readable_bytes(0, digits=0) == "0B"
    assert human_readable_bytes(0, digits=0, delim=" ") == "0 B"
    assert human_readable_bytes(0, digits=0, delim=" ", postfix="/s") == "0 B/s"
    assert human_readable_bytes(1024, digits=0, delim=" ", postfix="/s") == "1 KiB/s"
    assert human_readable_bytes(2048) == "2.00KiB"
    assert human_readable_bytes(2048 * 1024) == "2.00MiB"
    assert human_readable_bytes(2048 * 1024 * 1024) == "2.00GiB"
    assert human_readable_bytes(2048 * 1024 * 1024 * 1024) == "2.00TiB"


def test_human_readable_timedelta():
    assert human_readable_timedelta(timedelta(seconds=0)) == "0s"
    assert human_readable_timedelta(timedelta(seconds=1)) == "1s"
    assert human_readable_timedelta(timedelta(seconds=75)) == "1m15s"
    assert human_readable_timedelta(timedelta(seconds=3601)) == "1h1s"
    assert human_readable_timedelta(timedelta(seconds=3600 * 24 + 2)) == "1d2s"
    assert human_readable_timedelta(timedelta(days=1, seconds=3600 * 24 + 2)) == "2d2s"
    assert human_readable_timedelta(timedelta(days=3, seconds=3)) == "3d3s"
    assert human_readable_timedelta(timedelta(days=3)) == "3d"


def test_bool_or_value():
    assert bool_or_value("true") is True
    assert bool_or_value("false") is False
    assert bool_or_value("mem") == "mem"
    assert bool_or_value(None) is None
    assert bool_or_value(0) == 0
    assert bool_or_value(1) == 1


def test_bool_to_str():
    assert bool_to_str(True) == "true"
    assert bool_to_str(False) == "false"
    assert bool_to_str(None) is None
    assert bool_to_str(0) == 0
    assert bool_to_str(1) == 1
