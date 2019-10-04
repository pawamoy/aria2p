import os
import random
import signal
import string
from datetime import timedelta

import pytest

from aria2p.utils import (
    Queue,
    SignalHandler,
    bool_or_value,
    bool_to_str,
    human_readable_bytes,
    human_readable_timedelta,
)


class TestFunctions:
    def test_human_readable_bytes(self):
        assert human_readable_bytes(0) == "0.00B"

    def test_human_readable_bytes_0_digits(self):
        assert human_readable_bytes(0, digits=0) == "0B"

    def test_human_readable_bytes_space_delim(self):
        assert human_readable_bytes(0, digits=0, delim=" ") == "0 B"

    def test_human_readable_bytes_with_postfix(self):
        assert human_readable_bytes(0, digits=0, delim=" ", postfix="/s") == "0 B/s"

    def test_human_readable_bytes_all_kwargs(self):
        assert human_readable_bytes(1024, digits=0, delim=" ", postfix="/s") == "1 KiB/s"

    def test_human_readable_kibi_bytes(self):
        assert human_readable_bytes(2048) == "2.00KiB"

    def test_human_readable_mebi_bytes(self):
        assert human_readable_bytes(2048 * 1024) == "2.00MiB"

    def test_human_readable_giga_bytes(self):
        assert human_readable_bytes(2048 * 1024 * 1024) == "2.00GiB"

    def test_human_readable_tera_bytes(self):
        assert human_readable_bytes(2048 * 1024 * 1024 * 1024) == "2.00TiB"

    def test_human_readable_timedelta_force_print_0_seconds(self):
        assert human_readable_timedelta(timedelta(seconds=0)) == "0s"

    def test_human_readable_timedelta_one_second(self):
        assert human_readable_timedelta(timedelta(seconds=1)) == "1s"

    def test_human_readable_timedelta_more_than_60_seconds(self):
        assert human_readable_timedelta(timedelta(seconds=75)) == "1m15s"

    def test_human_readable_timedelta_more_than_3600_seconds(self):
        assert human_readable_timedelta(timedelta(seconds=3601)) == "1h1s"

    def test_human_readable_timedelta_more_than_1day_worth_seconds(self):
        assert human_readable_timedelta(timedelta(seconds=3600 * 24 + 2)) == "1d2s"

    def test_human_readable_timedelta_one_day_plus_more_than_1day_worth_seconds(self):
        assert human_readable_timedelta(timedelta(days=1, seconds=3600 * 24 + 2)) == "2d2s"

    def test_human_readable_timedelta_0_hours_0_minutes(self):
        assert human_readable_timedelta(timedelta(days=3, seconds=3)) == "3d3s"

    def test_human_readable_timedelta_only_days(self):
        assert human_readable_timedelta(timedelta(days=3)) == "3d"

    def test_human_readable_timedelta_only_hours(self):
        assert human_readable_timedelta(timedelta(seconds=3600 * 3)) == "3h"

    def test_human_readable_timedelta_only_minutes(self):
        assert human_readable_timedelta(timedelta(seconds=60 * 3)) == "3m"

    def test_bool_or_value_true_is_true(self):
        assert bool_or_value("true") is True

    def test_bool_or_value_false_is_false(self):
        assert bool_or_value("false") is False

    def test_bool_or_value_keep_string_value(self):
        assert bool_or_value("mem") == "mem"

    def test_bool_or_value_keep_none(self):
        assert bool_or_value(None) is None

    def test_bool_or_value_keep_false_int(self):
        assert bool_or_value(0) == 0

    def test_bool_or_value_keep_true_int(self):
        assert bool_or_value(1) == 1

    def test_bool_to_str_true_gives_true(self):
        assert bool_to_str(True) == "true"

    def test_bool_to_str_false_gives_false(self):
        assert bool_to_str(False) == "false"

    def test_bool_to_str_none_gives_none(self):
        assert bool_to_str(None) is None

    def test_bool_to_str_false_int_gives_int(self):
        assert bool_to_str(0) == 0

    def test_bool_to_str_true_int_gives_int(self):
        assert bool_to_str(1) == 1


class TestSignalHandler:
    def test_init(self):
        assert not SignalHandler([])
        assert not SignalHandler(["SIGTERM"])

    def test_trigger(self):
        triggered = SignalHandler(["SIGTERM"])
        assert not triggered
        os.kill(os.getpid(), signal.SIGTERM)
        assert triggered


def random_string(length):
    letters = string.ascii_lowercase
    return "".join(random.choice(letters) for _ in range(length))


class TestQueue:
    queue = Queue([0, "1", 2.3])
    queue_100 = Queue([random_string(16) for _ in range(100)])

    def test_init_queue(self):
        Queue([])
        assert Queue([0])

    def test_length(self):
        queue = Queue(range(100))
        assert len(queue) == 100

    def test_to_list(self):
        queue = Queue(range(5))
        assert list(queue) == queue.as_list() == [0, 1, 2, 3, 4]
        assert list(queue) is not list(queue)

    def test_bool(self):
        assert self.queue
        assert not Queue([])

    def test_get_item(self):
        assert self.queue[0] == 0
        assert self.queue[1] == "1"
        with pytest.raises(IndexError):
            print(self.queue[3])

    def test_index(self):
        assert self.queue.index(0) == 0
        assert self.queue.index(2.3) == 2
        assert self.queue.index("1") == 1

    def test_move_equal(self):
        assert not self.queue.move(0, 0)

    def test_move_down(self):
        queue = Queue([str(_) for _ in range(10, 0, -1)])
        assert queue.move("8", 6)
        assert list(queue) == ["10", "9", "7", "6", "5", "4", "8", "3", "2", "1"]

    def test_move_up(self):
        queue = Queue([str(_) for _ in range(10, 0, -1)])
        assert queue.move("1", 5)
        assert list(queue) == ["10", "9", "8", "7", "6", "1", "5", "4", "3", "2"]

    def test_sync(self):
        queue = Queue(range(1, 11))
        assert queue.move(10, 7)
        assert queue.move(10, 5)
        expected_mapping = {1: 0, 2: 1, 3: 2, 4: 3, 5: 4, 6: 6, 7: 7, 8: 8, 9: 9, 10: 5}
        assert queue._mapping == expected_mapping

    def test_remove(self):
        queue = Queue(range(5))
        queue.remove(3)
        queue.remove(1)
        assert list(queue) == [0, 2, 4]
        assert queue._mapping == {0: 0, 2: 1, 4: 2}

        del queue[1]
        assert list(queue) == [0, 4]
        assert queue._mapping == {0: 0, 4: 1}
