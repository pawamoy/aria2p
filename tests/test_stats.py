import pytest

from aria2p import Stats


@pytest.fixture(scope="module")
def stats():
    return Stats(
        {
            "downloadSpeed": "0",
            "numActive": "0",
            "numStopped": "0",
            "numStoppedTotal": "0",
            "numWaiting": "0",
            "uploadSpeed": "0",
        }
    )


def test_download_speed(stats):
    assert stats.download_speed == 0


def test_download_speed_string(stats):
    assert stats.download_speed_string() == "0.00 B/s"


def test_download_speed_string_not_human_readable(stats):
    assert stats.download_speed_string(human_readable=False) == "0 B/s"


def test_upload_speed(stats):
    assert stats.upload_speed == 0


def test_upload_speed_string(stats):
    assert stats.upload_speed_string() == "0.00 B/s"


def test_upload_speed_string_not_human_readable(stats):
    assert stats.upload_speed_string(human_readable=False) == "0 B/s"


def test_num_active(stats):
    assert stats.num_active == 0


def test_num_stopped(stats):
    assert stats.num_stopped == 0


def test_num_stopped_total(stats):
    assert stats.num_stopped_total == 0


def test_num_waiting(stats):
    assert stats.num_waiting == 0
