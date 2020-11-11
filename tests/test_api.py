"""Tests for the `api` module."""

import tempfile
import threading
import time
from pathlib import Path

import pytest

from aria2p import API, Client, Download

from . import (
    BUNSENLABS_MAGNET,
    BUNSENLABS_TORRENT,
    CONFIGS_DIR,
    DEBIAN_METALINK,
    SESSIONS_DIR,
    TESTS_TMP_DIR,
    XUBUNTU_MIRRORS,
    Aria2Server,
)


def test_add_magnet_method():
    with Aria2Server(port=7100) as server:
        assert server.api.add_magnet(BUNSENLABS_MAGNET)


def test_add_metalink_method():
    with Aria2Server(port=7101) as server:
        assert server.api.add_metalink(DEBIAN_METALINK)


def test_add_torrent_method():
    with Aria2Server(port=7102) as server:
        assert server.api.add_torrent(BUNSENLABS_TORRENT)


def test_add_uris_method():
    with Aria2Server(port=7103) as server:
        assert server.api.add_uris(XUBUNTU_MIRRORS)


def test_get_download_method():
    with Aria2Server(port=7104, session=SESSIONS_DIR / "dl-aria2-1.34.0-paused.txt") as server:
        assert server.api.get_download("2089b05ecca3d829")  # == server.api.get_downloads()[0].gid


def test_get_downloads_method():
    with Aria2Server(port=7105, session=SESSIONS_DIR / "dl-2-aria2.txt") as server:
        downloads = server.api.get_downloads()
        assert len(downloads) == 2
        assert isinstance(downloads[0], Download)
        assert downloads[0].gid == "2089b05ecca3d829"


def test_get_global_options_method():
    with Aria2Server(port=7106, config=CONFIGS_DIR / "max-5-dls.conf") as server:
        options = server.api.get_global_options()
        assert options.download is None
        assert options.max_concurrent_downloads == 5


@pytest.mark.skip("broken URL, https://github.com/pawamoy/aria2p/issues/76")
def test_get_options_method():
    with Aria2Server(port=7107, session=SESSIONS_DIR / "max-dl-limit-10000.txt") as server:
        downloads = server.api.get_downloads()
        options = server.api.get_options(downloads)[0]
        assert options.max_download_limit == 10000


def test_get_stats_method():
    with Aria2Server(port=7108) as server:
        assert server.api.get_stats()


def test_move_method():
    with Aria2Server(port=7109, session=SESSIONS_DIR / "2-dl-in-queue.txt") as server:
        downloads = server.api.get_downloads()
        assert server.api.move(downloads[0], 1) == 1
        new_pos_downloads = server.api.get_downloads()
        assert downloads == list(reversed(new_pos_downloads))


def test_move_down_method():
    with Aria2Server(port=7110, session=SESSIONS_DIR / "2-dl-in-queue.txt") as server:
        downloads = server.api.get_downloads()
        assert server.api.move_down(downloads[0]) == 1
        new_pos_downloads = server.api.get_downloads()
        assert downloads == list(reversed(new_pos_downloads))


def test_move_to_method():
    with Aria2Server(port=7111, session=SESSIONS_DIR / "2-dl-in-queue.txt") as server:
        downloads = server.api.get_downloads()
        assert server.api.move_to(downloads[0], 1) == 1
        new_pos_downloads = server.api.get_downloads()
        assert new_pos_downloads == [downloads[1], downloads[0]]

        assert server.api.move_to(downloads[1], -1) == 1
        new_pos_downloads = server.api.get_downloads()
        assert new_pos_downloads == downloads


def test_move_to_bottom_method():
    with Aria2Server(port=7112, session=SESSIONS_DIR / "2-dl-in-queue.txt") as server:
        downloads = server.api.get_downloads()
        assert server.api.move_to_bottom(downloads[0]) == 1
        new_pos_downloads = server.api.get_downloads()
        assert new_pos_downloads == [downloads[1], downloads[0]]


def test_move_to_top_method():
    with Aria2Server(port=7113, session=SESSIONS_DIR / "2-dl-in-queue.txt") as server:
        downloads = server.api.get_downloads()
        assert server.api.move_to_top(downloads[1]) == 0
        new_pos_downloads = server.api.get_downloads()
        assert new_pos_downloads == [downloads[1], downloads[0]]


def test_move_up_method():
    with Aria2Server(port=7114, session=SESSIONS_DIR / "2-dl-in-queue.txt") as server:
        downloads = server.api.get_downloads()
        assert server.api.move_up(downloads[0]) == 0
        new_pos_downloads = server.api.get_downloads()
        assert downloads == new_pos_downloads


def test_pause_method():
    with Aria2Server(port=7115, session=SESSIONS_DIR / "big-download.txt") as server:
        downloads = server.api.get_downloads()
        assert server.api.pause([downloads[0]])
        assert server.api.get_download(downloads[0].gid).status == "paused"


def test_pause_all_method():
    with Aria2Server(port=7116, session=SESSIONS_DIR / "3-dls.txt") as server:
        assert server.api.pause_all()
        # The following code block is commented out because we cannot ensure
        # that the downloads will be paused in sufficient time.
        # aria2c returns "OK" immediately, and only then proceeds to pause the downloads
        # (with potential additional steps like contacting trackers).
        # Therefore we simply check the the call goes well.

        # for _ in range(5):
        #     time.sleep(1)
        #     downloads = server.api.get_downloads()
        #     try:
        #         assert all([d.is_paused for d in downloads])
        #     except AssertionError:
        #         pass
        #     else:
        #         break
        # else:
        #     raise AssertionError


def test_autopurge_method():
    with Aria2Server(port=7117, session=SESSIONS_DIR / "3-dls.txt") as server:
        assert server.api.autopurge()


def test_remove_method():
    with Aria2Server(port=7118, session=SESSIONS_DIR / "3-dls.txt") as server:
        downloads = server.api.get_downloads()
        # FIXME: subject to failure
        assert server.api.remove(downloads) == [True for _ in downloads]
        downloads = server.api.get_downloads()
        assert not downloads


def test_remove_files_method():
    with Aria2Server(port=7131, session=SESSIONS_DIR / "very-small-remote-file.txt") as server:
        download = server.api.get_downloads()[0]
        while not download.is_complete:
            time.sleep(0.1)
            download.update()
        assert server.api.remove([download], files=True)
        for file in download.root_files_paths:
            assert not file.exists()


def test_remove_files_not_complete():
    with Aria2Server(port=7132, session=SESSIONS_DIR / "2-dl-in-queue.txt") as server:
        downloads = server.api.get_downloads()
        assert server.api.remove(downloads, files=True)
        for download in downloads:
            for file in download.root_files_paths:
                assert file.exists()


def test_remove_files_tree():
    with Aria2Server(port=1, run=False) as server:
        directory = server.tmp_dir / "some-directory"
        directory.mkdir()

        class _Download:
            is_complete = True
            root_files_paths = [directory]

        assert server.api.remove_files([_Download])
        assert not directory.exists()


def test_remove_all_method():
    with Aria2Server(port=7119, session=SESSIONS_DIR / "3-dls.txt") as server:
        # FIXME: subject to failure (probably because of api.remove)
        assert server.api.remove_all()
        downloads = server.api.get_downloads()
        assert not downloads


def test_resume_method():
    with Aria2Server(port=7120, session=SESSIONS_DIR / "2-dl-in-queue.txt") as server:
        downloads = server.api.get_downloads()
        assert server.api.resume(downloads)
        downloads = server.api.get_downloads()
        assert all([d.is_active for d in downloads])


def test_resume_all_method():
    with Aria2Server(port=7121, session=SESSIONS_DIR / "2-dl-in-queue.txt") as server:
        assert server.api.resume_all()
        downloads = server.api.get_downloads()
        assert all([d.is_active for d in downloads])


# TODO: write this test when search is implemented
# def test_search_method():
#     with Aria2Server(port=7122) as server:
#         assert server.api.search()


def test_set_global_options_method():
    with Aria2Server(port=7123, config=CONFIGS_DIR / "max-5-dls.conf") as server:
        assert server.api.set_global_options({"max-concurrent-downloads": "10"})
        options = server.api.get_global_options()
        assert options.max_concurrent_downloads == 10


@pytest.mark.skip("broken URL, https://github.com/pawamoy/aria2p/issues/76")
def test_set_options_method():
    with Aria2Server(port=7124, session=SESSIONS_DIR / "max-dl-limit-10000.txt") as server:
        downloads = server.api.get_downloads()
        assert server.api.set_options({"max-download-limit": "20000"}, downloads)[0]
        options = server.api.get_options(downloads)[0]
        assert options.max_download_limit == 20000


def test_copy_files_method():
    with Aria2Server(port=7125, session=SESSIONS_DIR / "very-small-remote-file.txt") as server:
        # initialize temp dir to copy to
        tmp_dir = Path(tempfile.mkdtemp(dir=TESTS_TMP_DIR))

        # wait until download is finished
        download = server.api.get_downloads()[0]
        while not download.is_complete:
            time.sleep(0.2)
            download.update()

        # actual method run
        server.api.copy_files([download], tmp_dir)

        # assert file was copied and contents are identical
        source = download.files[0].path
        target = tmp_dir / source.name

        assert source.exists()
        assert target.exists()

        with open(source) as stream:
            source_contents = stream.read()
        with open(target) as stream:
            target_contents = stream.read()
        assert source_contents == target_contents

        # clean up
        target.unlink()
        tmp_dir.rmdir()


def test_move_files_method():
    with Aria2Server(port=7126, session=SESSIONS_DIR / "very-small-remote-file.txt") as server:
        # initialize temp dir to copy to
        tmp_dir = Path(tempfile.mkdtemp(dir=TESTS_TMP_DIR))

        # wait until download is finished
        download = server.api.get_downloads()[0]
        while not download.is_complete:
            time.sleep(0.2)
            download.update()

        # read source contents before move
        source = download.files[0].path
        with open(source) as stream:
            source_contents = stream.read()

        # actual method run
        server.api.move_files([download], tmp_dir)

        # assert file was copied and contents are identical
        target = tmp_dir / source.name

        assert not source.exists()
        assert target.exists()

        with open(target) as stream:
            target_contents = stream.read()
        assert source_contents == target_contents

        # clean up
        target.unlink()
        tmp_dir.rmdir()


def test_listen_to_notifications():
    with Aria2Server(port=7127, session=SESSIONS_DIR / "2-dl-in-queue.txt") as server:
        server.api.listen_to_notifications(threaded=True, timeout=1)
    time.sleep(3)
    assert not server.api.listener.is_alive()


def test_listen_to_notifications_then_stop():
    api = API(Client(port=7128))
    api.listen_to_notifications(threaded=True, timeout=1)
    api.stop_listening()
    assert api.listener is None


def test_listen_to_notifications_callbacks(capsys):
    with Aria2Server(port=7129, session=SESSIONS_DIR / "2-dl-in-queue.txt") as server:
        server.api.listen_to_notifications(
            on_download_start=lambda api, gid: print("started " + gid), threaded=True, timeout=1
        )
        time.sleep(1)
        server.api.resume_all()
        time.sleep(3)
        server.api.stop_listening()
    assert capsys.readouterr().out == "started 2089b05ecca3d829\nstarted cca3d8292089b05e\n"


def test_listen_to_notifications_no_thread():
    with Aria2Server(port=7130, session=SESSIONS_DIR / "2-dl-in-queue.txt") as server:

        def thread_target():
            server.api.listen_to_notifications(threaded=False, timeout=1)

        thread = threading.Thread(target=thread_target)
        thread.start()
        time.sleep(1)
        server.client.stop_listening()
        time.sleep(1)
        server.api.stop_listening()
