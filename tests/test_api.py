from aria2p import Download

from . import (
    BUNSENLABS_MAGNET,
    BUNSENLABS_TORRENT,
    CONFIGS_DIR,
    DEBIAN_METALINK,
    SESSIONS_DIR,
    TESTS_DATA_DIR,
    TESTS_TMP_DIR,
    XUBUNTU_MIRRORS,
    Aria2Server,
)


def test_add_magnet_method():
    with Aria2Server() as server:
        assert server.api.add_magnet(BUNSENLABS_MAGNET)


def test_add_metalink_method():
    with Aria2Server() as server:
        assert server.api.add_metalink(DEBIAN_METALINK)


def test_add_torrent_method():
    with Aria2Server() as server:
        assert server.api.add_torrent(BUNSENLABS_TORRENT)


def test_add_uris_method():
    with Aria2Server() as server:
        assert server.api.add_uris(XUBUNTU_MIRRORS)


def test_get_download_method():
    with Aria2Server(session=SESSIONS_DIR / "dl-aria2-1.34.0-paused.txt") as server:
        assert server.api.get_download("2089b05ecca3d829")  # == server.api.get_downloads()[0].gid


def test_get_downloads_method():
    with Aria2Server(session=SESSIONS_DIR / "dl-2-aria2.txt") as server:
        downloads = server.api.get_downloads()
        assert len(downloads) == 2
        assert isinstance(downloads[0], Download)
        assert downloads[0].gid == "2089b05ecca3d829"


def test_get_global_options_method():
    with Aria2Server(config=CONFIGS_DIR / "max-5-dls.conf") as server:
        options = server.api.get_global_options()
        assert options.download is None
        assert options.max_concurrent_downloads == 5


def test_get_options_method():
    with Aria2Server(session=SESSIONS_DIR / "max-dl-limit-10000.txt") as server:
        downloads = server.api.get_downloads()
        options = server.api.get_options(downloads)[0]
        assert options.max_download_limit == 10000


def test_get_stats_method():
    with Aria2Server() as server:
        assert server.api.get_stats()


def test_move_method():
    with Aria2Server(session=SESSIONS_DIR / "2-dl-in-queue.txt") as server:
        downloads = server.api.get_downloads()
        assert server.api.move(downloads[0], 1)
        new_pos_downloads = server.api.get_downloads()
        assert downloads == list(reversed(new_pos_downloads))


# def test_move_down_method():
#     with Aria2Server() as server:
#         assert server.api.move_down()
#
#
# def test_move_to_method():
#     with Aria2Server() as server:
#         assert server.api.move_to()
#
#
# def test_move_to_bottom_method():
#     with Aria2Server() as server:
#         assert server.api.move_to_bottom()
#
#
# def test_move_to_top_method():
#     with Aria2Server() as server:
#         assert server.api.move_to_top()
#
#
# def test_move_up_method():
#     with Aria2Server() as server:
#         assert server.api.move_up()
#
#
# def test_pause_method():
#     with Aria2Server() as server:
#         assert server.api.pause()
#
#
# def test_pause_all_method():
#     with Aria2Server() as server:
#         assert server.api.pause_all()
#
#
# def test_purge_method():
#     with Aria2Server() as server:
#         assert server.api.purge()
#
#
# def test_remove_method():
#     with Aria2Server() as server:
#         assert server.api.remove()
#
#
# def test_remove_all_method():
#     with Aria2Server() as server:
#         assert server.api.remove_all()
#
#
# def test_resume_method():
#     with Aria2Server() as server:
#         assert server.api.resume()
#
#
# def test_resume_all_method():
#     with Aria2Server() as server:
#         assert server.api.resume_all()
#
#
# def test_search_method():
#     with Aria2Server() as server:
#         assert server.api.search()
#
#
# def test_set_global_options_method():
#     with Aria2Server() as server:
#         assert server.api.set_global_options()
#
#
# def test_set_options_method():
#     with Aria2Server() as server:
#         assert server.api.set_options()
