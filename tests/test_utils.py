from datetime import timedelta

from aria2p.utils import bool_or_value, bool_to_str, human_readable_bytes, human_readable_timedelta


def test_human_readable_bytes():
    assert human_readable_bytes(0) == "0.00B"


def test_human_readable_bytes_0_digits():
    assert human_readable_bytes(0, digits=0) == "0B"


def test_human_readable_bytes_space_delim():
    assert human_readable_bytes(0, digits=0, delim=" ") == "0 B"


def test_human_readable_bytes_with_postfix():
    assert human_readable_bytes(0, digits=0, delim=" ", postfix="/s") == "0 B/s"


def test_human_readable_bytes_all_kwargs():
    assert human_readable_bytes(1024, digits=0, delim=" ", postfix="/s") == "1 KiB/s"


def test_human_readable_kibi_bytes():
    assert human_readable_bytes(2048) == "2.00KiB"


def test_human_readable_mebi_bytes():
    assert human_readable_bytes(2048 * 1024) == "2.00MiB"


def test_human_readable_giga_bytes():
    assert human_readable_bytes(2048 * 1024 * 1024) == "2.00GiB"


def test_human_readable_tera_bytes():
    assert human_readable_bytes(2048 * 1024 * 1024 * 1024) == "2.00TiB"


def test_human_readable_timedelta_force_print_0_seconds():
    assert human_readable_timedelta(timedelta(seconds=0)) == "0s"


def test_human_readable_timedelta_one_second():
    assert human_readable_timedelta(timedelta(seconds=1)) == "1s"


def test_human_readable_timedelta_more_than_60_seconds():
    assert human_readable_timedelta(timedelta(seconds=75)) == "1m15s"


def test_human_readable_timedelta_more_than_3600_seconds():
    assert human_readable_timedelta(timedelta(seconds=3601)) == "1h1s"


def test_human_readable_timedelta_more_than_1day_worth_seconds():
    assert human_readable_timedelta(timedelta(seconds=3600 * 24 + 2)) == "1d2s"


def test_human_readable_timedelta_one_day_plus_more_than_1day_worth_seconds():
    assert human_readable_timedelta(timedelta(days=1, seconds=3600 * 24 + 2)) == "2d2s"


def test_human_readable_timedelta_0_hours_0_minutes():
    assert human_readable_timedelta(timedelta(days=3, seconds=3)) == "3d3s"


def test_human_readable_timedelta_only_days():
    assert human_readable_timedelta(timedelta(days=3)) == "3d"


def test_human_readable_timedelta_only_hours():
    assert human_readable_timedelta(timedelta(seconds=3600 * 3)) == "3h"


def test_human_readable_timedelta_only_minutes():
    assert human_readable_timedelta(timedelta(seconds=60 * 3)) == "3m"


def test_bool_or_value_true_is_true():
    assert bool_or_value("true") is True


def test_bool_or_value_false_is_false():
    assert bool_or_value("false") is False


def test_bool_or_value_keep_string_value():
    assert bool_or_value("mem") == "mem"


def test_bool_or_value_keep_none():
    assert bool_or_value(None) is None


def test_bool_or_value_keep_false_int():
    assert bool_or_value(0) == 0


def test_bool_or_value_keep_true_int():
    assert bool_or_value(1) == 1


def test_bool_to_str_true_gives_true():
    assert bool_to_str(True) == "true"


def test_bool_to_str_false_gives_false():
    assert bool_to_str(False) == "false"


def test_bool_to_str_none_gives_none():
    assert bool_to_str(None) is None


def test_bool_to_str_false_int_gives_int():
    assert bool_to_str(0) == 0


def test_bool_to_str_true_int_gives_int():
    assert bool_to_str(1) == 1
