"""Tests for the `api` module."""

from __future__ import annotations

import threading
import time
from typing import TYPE_CHECKING

import pytest

from aria2p import API, Client, ClientException, Download
from tests import BUNSENLABS_MAGNET, BUNSENLABS_TORRENT, CONFIGS_DIR, DEBIAN_METALINK, INPUT_FILES, XUBUNTU_MIRRORS
from tests.conftest import Aria2Server

if TYPE_CHECKING:
    from pathlib import Path


def test_add_magnet_method(server: Aria2Server) -> None:
    assert server.api.add_magnet(BUNSENLABS_MAGNET)


def test_add_metalink_method(server: Aria2Server) -> None:
    assert server.api.add_metalink(DEBIAN_METALINK)


def test_add_torrent_method(server: Aria2Server) -> None:
    assert server.api.add_torrent(BUNSENLABS_TORRENT)


def test_add_uris_method(server: Aria2Server) -> None:
    assert server.api.add_uris(XUBUNTU_MIRRORS)


def test_get_download_method(tmp_path: Path, port: int) -> None:
    with Aria2Server(tmp_path, port, session="1-dl-paused.txt") as server:
        assert server.api.get_download("0000000000000001")  # == server.api.get_downloads()[0].gid


def test_get_downloads_method(tmp_path: Path, port: int) -> None:
    with Aria2Server(tmp_path, port, session="2-dls.txt") as server:
        downloads = server.api.get_downloads()
        assert len(downloads) == 2
        assert isinstance(downloads[0], Download)
        assert downloads[0].gid == "0000000000000001"


def test_get_global_options_method(tmp_path: Path, port: int) -> None:
    with Aria2Server(tmp_path, port, config=CONFIGS_DIR / "max-5-dls.conf") as server:
        options = server.api.get_global_options()
        assert options.download is None
        assert options.max_concurrent_downloads == 5


def test_get_options_method(tmp_path: Path, port: int) -> None:
    with Aria2Server(tmp_path, port, session="max-dl-limit-10000.txt") as server:
        downloads = server.api.get_downloads()
        options = server.api.get_options(downloads)[0]
        assert options.max_download_limit == 10000


def test_get_stats_method(server: Aria2Server) -> None:
    assert server.api.get_stats()


def test_move_method(tmp_path: Path, port: int) -> None:
    with Aria2Server(tmp_path, port, session="2-dls-paused.txt") as server:
        downloads = server.api.get_downloads()
        assert server.api.move(downloads[0], 1) == 1
        new_pos_downloads = server.api.get_downloads()
        assert downloads == list(reversed(new_pos_downloads))


def test_move_down_method(tmp_path: Path, port: int) -> None:
    with Aria2Server(tmp_path, port, session="2-dls-paused.txt") as server:
        downloads = server.api.get_downloads()
        assert server.api.move_down(downloads[0]) == 1
        new_pos_downloads = server.api.get_downloads()
        assert downloads == list(reversed(new_pos_downloads))


def test_move_to_method(tmp_path: Path, port: int) -> None:
    with Aria2Server(tmp_path, port, session="2-dls-paused.txt") as server:
        downloads = server.api.get_downloads()
        assert server.api.move_to(downloads[0], 1) == 1
        new_pos_downloads = server.api.get_downloads()
        assert new_pos_downloads == [downloads[1], downloads[0]]

        assert server.api.move_to(downloads[1], -1) == 1
        new_pos_downloads = server.api.get_downloads()
        assert new_pos_downloads == downloads


def test_move_to_bottom_method(tmp_path: Path, port: int) -> None:
    with Aria2Server(tmp_path, port, session="2-dls-paused.txt") as server:
        downloads = server.api.get_downloads()
        assert server.api.move_to_bottom(downloads[0]) == 1
        new_pos_downloads = server.api.get_downloads()
        assert new_pos_downloads == [downloads[1], downloads[0]]


def test_move_to_top_method(tmp_path: Path, port: int) -> None:
    with Aria2Server(tmp_path, port, session="2-dls-paused.txt") as server:
        downloads = server.api.get_downloads()
        assert server.api.move_to_top(downloads[1]) == 0
        new_pos_downloads = server.api.get_downloads()
        assert new_pos_downloads == [downloads[1], downloads[0]]


def test_move_up_method(tmp_path: Path, port: int) -> None:
    with Aria2Server(tmp_path, port, session="2-dls-paused.txt") as server:
        downloads = server.api.get_downloads()
        assert server.api.move_up(downloads[0]) == 0
        new_pos_downloads = server.api.get_downloads()
        assert downloads == new_pos_downloads


def test_pause_method(tmp_path: Path, port: int) -> None:
    with Aria2Server(tmp_path, port, session="big-download.txt") as server:
        time.sleep(0.1)
        downloads = server.api.get_downloads()
        if downloads[0].has_failed:
            pytest.xfail("Failed to establish connection (sporadic error)")
        assert server.api.pause([downloads[0]])
        assert downloads[0].live.status == "paused"


def test_pause_all_method(tmp_path: Path, port: int) -> None:
    with Aria2Server(tmp_path, port, session="3-dls.txt") as server:
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


def test_autopurge_method(tmp_path: Path, port: int) -> None:
    with Aria2Server(tmp_path, port, session="3-dls.txt") as server:
        assert server.api.autopurge()


def test_remove_method(tmp_path: Path, port: int) -> None:
    with Aria2Server(tmp_path, port, session="3-dls.txt") as server:
        downloads = server.api.get_downloads()
        if not all(server.api.remove(downloads)):
            pytest.xfail("Sporadic failures")
        downloads = server.api.get_downloads()
        assert not downloads


def test_remove_files_method(tmp_path: Path, port: int) -> None:
    with Aria2Server(tmp_path, port, session="very-small-download.txt") as server:
        time.sleep(1)
        download = server.api.get_downloads()[0]
        while not download.live.is_complete:
            if download.has_failed:
                pytest.xfail("Failed to establish connection (sporadic error)")
            time.sleep(0.1)
        assert server.api.remove([download], files=True)
        for file in download.root_files_paths:
            assert not file.exists()


def test_remove_files_not_complete(tmp_path: Path, port: int) -> None:
    with Aria2Server(tmp_path, port, session="2-dls-paused.txt") as server:
        downloads = server.api.get_downloads()
        assert server.api.remove(downloads, files=True)
        for download in downloads:
            for file in download.root_files_paths:
                assert file.exists()


def test_remove_files_tree(server: Aria2Server) -> None:
    directory = server.tmp_dir / "some-directory"
    directory.mkdir()

    class _Download:
        is_complete = True
        root_files_paths = [directory]  # noqa: RUF012

    assert server.api.remove_files([_Download])  # type: ignore[list-item]
    assert not directory.exists()


def test_remove_all_method(tmp_path: Path, port: int) -> None:
    with Aria2Server(tmp_path, port, session="3-dls.txt") as server:
        if not server.api.remove_all():
            pytest.xfail("Sporadic failures")
        downloads = server.api.get_downloads()
        assert not downloads


def test_resume_method(tmp_path: Path, port: int) -> None:
    with Aria2Server(tmp_path, port, session="2-dls-paused.txt") as server:
        downloads = server.api.get_downloads()
        assert server.api.resume(downloads)
        downloads = server.api.get_downloads()
        active = [d.is_active for d in downloads]
        if not all(active):
            pytest.xfail("Not all downloads were resumed (sporadic error)")
        assert all(active)


def test_resume_all_method(tmp_path: Path, port: int) -> None:
    with Aria2Server(tmp_path, port, session="2-dls-paused.txt") as server:
        time.sleep(0.1)
        assert server.api.resume_all()
        time.sleep(0.1)
        downloads = server.api.get_downloads()
        for download in downloads:
            if download.has_failed:
                pytest.xfail("Failed to establish connection (sporadic error)")
        assert all(d.is_active for d in downloads)


def test_set_global_options_method(tmp_path: Path, port: int) -> None:
    with Aria2Server(tmp_path, port, config=CONFIGS_DIR / "max-5-dls.conf") as server:
        assert server.api.set_global_options({"max-concurrent-downloads": "10"})
        options = server.api.get_global_options()
        assert options.max_concurrent_downloads == 10


def test_set_options_method(tmp_path: Path, port: int) -> None:
    with Aria2Server(tmp_path, port, session="max-dl-limit-10000.txt") as server:
        downloads = server.api.get_downloads()
        try:
            assert server.api.set_options({"max-download-limit": "20000"}, downloads)[0]
        except ClientException:
            pytest.xfail("Cannot change option for some reason")
        try:
            options = server.api.get_options(downloads)[0]
        except ClientException:
            pytest.xfail("Cannot change option for some reason")
        assert options.max_download_limit == 20000


# @pytest.mark.flaky(reruns=5)
def test_copy_files_method(tmp_path_factory: pytest.TempPathFactory, port: int) -> None:
    with Aria2Server(tmp_path_factory.mktemp("copy_files"), port, session="very-small-download.txt") as server:
        # initialize temp dir to copy to
        tmp_dir = tmp_path_factory.mktemp("copy_files")

        # wait until download is finished
        download = server.api.get_downloads()[0]
        while not download.live.is_complete:
            if download.has_failed:
                pytest.xfail("Failed to establish connection (sporadic error)")
            time.sleep(0.2)

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


def test_move_files_method(tmp_path_factory: pytest.TempPathFactory, port: int) -> None:
    with Aria2Server(tmp_path_factory.mktemp("move_files"), port, session="very-small-download.txt") as server:
        # initialize temp dir to copy to
        tmp_dir = tmp_path_factory.mktemp("move_files")

        # wait until download is finished
        download = server.api.get_downloads()[0]
        while not download.live.is_complete:
            if download.has_failed:
                pytest.xfail("Failed to establish connection (sporadic error)")
            time.sleep(0.2)

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


def test_listen_to_notifications(tmp_path: Path, port: int) -> None:
    with Aria2Server(tmp_path, port, session="2-dls-paused.txt") as server:
        server.api.listen_to_notifications(threaded=True, timeout=1)
    time.sleep(3)
    assert server.api.listener
    assert not server.api.listener.is_alive()


def test_listen_to_notifications_then_stop(port: int) -> None:
    api = API(Client(port=port))
    api.listen_to_notifications(threaded=True, timeout=1)
    api.stop_listening()
    assert api.listener is None


def test_listen_to_notifications_callbacks(tmp_path: Path, port: int, capsys: pytest.CaptureFixture) -> None:
    with Aria2Server(tmp_path, port, session="2-dls-paused.txt") as server:
        server.api.listen_to_notifications(
            on_download_start=lambda api, gid: print("started " + gid),  # noqa: T201
            threaded=True,
            timeout=1,
        )
        time.sleep(1)
        server.api.resume_all()
        time.sleep(3)
        server.api.stop_listening()
    assert capsys.readouterr().out == "started 0000000000000001\nstarted 0000000000000002\n"


def test_listen_to_notifications_no_thread(tmp_path: Path, port: int) -> None:
    with Aria2Server(tmp_path, port, session="2-dls-paused.txt") as server:

        def thread_target() -> None:
            server.api.listen_to_notifications(threaded=False, timeout=1)

        thread = threading.Thread(target=thread_target)
        thread.start()
        time.sleep(1)
        server.client.stop_listening()
        time.sleep(1)
        server.api.stop_listening()


def test_parse_input_file() -> None:
    api = API()

    downloads = api.parse_input_file(INPUT_FILES[0])
    assert len(downloads) == 2

    downloads = api.parse_input_file(INPUT_FILES[1])
    assert len(downloads) == 1

    downloads = api.parse_input_file(INPUT_FILES[2])
    assert len(downloads) == 0
