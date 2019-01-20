from . import Aria2Server


def test_stats_properties_and_methods():
    with Aria2Server(port=7300) as server:
        stats = server.api.get_stats()
    assert stats.download_speed == 0
    assert stats.download_speed_string() == "0.00 B/s"
    assert stats.download_speed_string(human_readable=False) == "0 B/s"
    assert stats.upload_speed == 0
    assert stats.upload_speed_string() == "0.00 B/s"
    assert stats.upload_speed_string(human_readable=False) == "0 B/s"
    assert stats.num_active == 0
    assert stats.num_stopped == 0
    assert stats.num_stopped_total == 0
    assert stats.num_waiting == 0
