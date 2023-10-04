"""Tests for the `downloads` module."""

from __future__ import annotations

import datetime
from datetime import timezone
from pathlib import Path

import pytest

from aria2p import API, BitTorrent, ClientException, Download, File
from tests.conftest import Aria2Server


class TestBitTorrentClass:
    def setup_method(self) -> None:
        self.bittorrent = BitTorrent(
            {"announceList": [], "comment": "", "creationDate": 10, "mode": "single", "info": {"name": ""}},
        )

    def test_init_method(self) -> None:
        assert BitTorrent(self.bittorrent._struct)

    def test_str_method(self) -> None:
        assert str(self.bittorrent) == self.bittorrent.info["name"]

    def test_announce_list_property(self) -> None:
        assert self.bittorrent.announce_list == []

    def test_comment_property(self) -> None:
        assert self.bittorrent.comment == ""

    def test_creation_date_property(self) -> None:
        assert self.bittorrent.creation_date == datetime.datetime.fromtimestamp(10, tz=timezone.utc)

    def test_mode_property(self) -> None:
        assert self.bittorrent.mode == "single"

    def test_info_property(self) -> None:
        assert self.bittorrent.info == {"name": ""}


class TestDownloadClass:
    def setup_method(self) -> None:
        self.bitfield = (
            "9e7ef5fbdefdffffdfffffffffffffdf7fff5dfefff7feffefffdff7fffffffbfeffbffddf7de9f7eefffffffeffe77bb"
            "f8fdbdcffef7fffffbefad7ffffffbf55bff7edfedfeff7ffff7ffffff3ffff7d3ffbfffddddffe7ffffffffffdedf7fd"
            "fef62fbdfffffbffbffdcfaffffafebeff3ebff7d5fffbbb2bafef77ffaffe7d37fbffffffb6dfffffffedfebbecbbffe"
            "bdefffffffff977f7ffdffee7fffffffdfeb3f67dddffeedfffffbfffffdaffbfeedfadef6dfd9d2df9fb7f689ffcff3f"
            "fbfebbfdbd7fcddfa77dfddffdfe327fdcbf77fad87ffff6ff7ffebfefdfbbffdefdafeefed7fefffe7ffad9ffdcffefc"
            "ffbbf3c07ef7fc0"
        )
        self.download = Download(
            API(),
            {
                "bitfield": self.bitfield,
                "bittorrent": {},
                "completedLength": "889592532",
                "connections": "44",
                "dir": "/home/pawamoy/Downloads/torrents/tmp",
                "downloadSpeed": "745509",
                "files": [
                    {
                        "completedLength": "58132",
                        "index": "1",
                        "length": "58132",
                        "path": "/home/pawamoy/Downloads/torrents/tmp/dl/logo.jpg",
                        "selected": "true",
                        "uris": [],
                    },
                    {
                        "completedLength": "885864384",
                        "index": "2",
                        "length": "1045247936",
                        "path": "/home/pawamoy/Downloads/torrents/tmp/dl/video.mp4",
                        "selected": "true",
                        "uris": [],
                    },
                ],
                "following": "a89a9c5ac990e6ef",
                "gid": "0a6635c602761000",
                "infoHash": "4f1da018803b65f61ed76612af9ad00d4373a771",
                "numPieces": "1994",
                "numSeeders": "12",
                "pieceLength": "524288",
                "seeder": "false",
                "status": "active",
                "totalLength": "1045306068",
                "uploadLength": "97207027",
                "uploadSpeed": "11032",
            },
        )

    def test_eq_method(self) -> None:
        assert self.download == Download(API(), {"gid": "0a6635c602761000"})

    def test_init_method(self) -> None:
        assert Download(API(), {})

    def test_str_method(self) -> None:
        assert str(self.download) == self.download.name

    def test_update_method(self, tmp_path: Path, port: int) -> None:
        with Aria2Server(tmp_path, port, session="1-dl-paused.txt") as server:
            download = server.api.get_download("0000000000000001")
            download.update()

    def test_belongs_to(self, server: Aria2Server) -> None:
        self.download.api = server.api
        assert self.download.belongs_to is None

    def test_belongs_to_id(self) -> None:
        assert self.download.belongs_to_id is None

    def test_bitfield(self) -> None:
        assert self.download.bitfield == self.bitfield

    def test_bittorrent(self) -> None:
        assert self.download.bittorrent

        # assert value was cached
        self.download._struct["bittorrent"] = {"mode": "single"}
        assert self.download.bittorrent.mode is None

        # assert is None when "bittorrent" key is not in struct
        del self.download._struct["bittorrent"]
        self.download._bittorrent = None
        assert self.download.bittorrent is None

    def test_completed_length(self) -> None:
        assert self.download.completed_length == 889_592_532

    def test_completed_length_string(self) -> None:
        assert self.download.completed_length_string() == "848.38 MiB"
        assert self.download.completed_length_string(human_readable=False) == "889592532 B"

    def test_connections(self) -> None:
        assert self.download.connections == 44

    def test_dir(self) -> None:
        assert self.download.dir == Path("/home/pawamoy/Downloads/torrents/tmp")

    def test_download_speed(self) -> None:
        assert self.download.download_speed == 745_509

    def test_download_speed_string(self) -> None:
        assert self.download.download_speed_string() == "728.04 KiB/s"
        assert self.download.download_speed_string(human_readable=False) == "745509 B/s"

    def test_error_code(self) -> None:
        assert self.download.error_code is None

    def test_error_message(self) -> None:
        assert self.download.error_message is None

    def test_eta(self) -> None:
        assert isinstance(self.download.eta, datetime.timedelta)
        self.download._struct["downloadSpeed"] = "0"
        assert self.download.eta == datetime.timedelta.max

    def test_eta_string(self) -> None:
        assert self.download.eta_string() == "3m28s"
        self.download._struct["downloadSpeed"] = "0"
        assert self.download.eta_string() == "-"

    def test_files(self) -> None:
        assert len(self.download.files) == 2

        # assert value was cached
        self.download._struct["files"] = []
        assert len(self.download.files) == 2

    def test_followed_by(self, server: Aria2Server) -> None:
        self.download.api = server.api
        assert self.download.followed_by == []

    def test_followed_by_ids(self, server: Aria2Server) -> None:
        self.download.api = server.api
        assert self.download.followed_by_ids == []

    def test_following(self, server: Aria2Server) -> None:
        self.download.api = server.api
        assert self.download.following is None

    def test_following_id(self) -> None:
        assert self.download.following_id == "a89a9c5ac990e6ef"

    def test_gid(self) -> None:
        assert self.download.gid == "0a6635c602761000"

    def test_has_failed(self) -> None:
        assert self.download.has_failed is False

    def test_info_hash(self) -> None:
        assert self.download.info_hash == "4f1da018803b65f61ed76612af9ad00d4373a771"

    def test_is_active(self) -> None:
        assert self.download.is_active is True

    def test_is_complete(self) -> None:
        assert self.download.is_complete is False

    def test_is_paused(self) -> None:
        assert self.download.is_paused is False

    def test_is_removed(self) -> None:
        assert self.download.is_removed is False

    def test_is_waiting(self) -> None:
        assert self.download.is_waiting is False

    def test_move(self, server: Aria2Server) -> None:
        self.download.api = server.api
        with pytest.raises(ClientException):
            self.download.move(2)

    def test_move_down(self, server: Aria2Server) -> None:
        self.download.api = server.api
        with pytest.raises(ClientException):
            self.download.move_down(1)

    def test_move_to(self, server: Aria2Server) -> None:
        self.download.api = server.api
        with pytest.raises(ClientException):
            self.download.move_to(10)

    def test_move_to_bottom(self, server: Aria2Server) -> None:
        self.download.api = server.api
        with pytest.raises(ClientException):
            self.download.move_to_bottom()

    def test_move_to_top(self, server: Aria2Server) -> None:
        self.download.api = server.api
        with pytest.raises(ClientException):
            self.download.move_to_top()

    def test_move_up(self, server: Aria2Server) -> None:
        self.download.api = server.api
        with pytest.raises(ClientException):
            self.download.move_up()

    def test_name(self) -> None:
        assert self.download.name == "dl"

    def test_name_bittorrent(self) -> None:
        # TODO
        pass

    def test_name_metadata(self) -> None:
        # TODO
        pass

    def test_name_filepath(self) -> None:
        # TODO
        pass

    def test_name_uri(self) -> None:
        # TODO
        pass

    def test_num_pieces(self) -> None:
        assert self.download.num_pieces == 1994

    def test_num_seeders(self) -> None:
        assert self.download.num_seeders == 12

    def test_options(self, server: Aria2Server) -> None:
        self.download.api = server.api
        with pytest.raises(ClientException):
            print(self.download.options)  # noqa: T201

    def test_options2(self) -> None:
        witness = []

        def mocked() -> None:
            witness.append(0)
            self.download._options = True

        self.download.update_options = mocked
        assert self.download.options is True
        assert witness == [0]
        assert self.download.options is True
        assert witness == [0]

    def test_set_options(self) -> None:
        self.download.options = "options"
        assert self.download.options == "options"

    def test_pause(self, server: Aria2Server) -> None:
        self.download.api = server.api
        with pytest.raises(ClientException):
            self.download.pause()

    def test_piece_length(self) -> None:
        assert self.download.piece_length == 524_288

    def test_piece_length_string(self) -> None:
        assert self.download.piece_length_string() == "512.00 KiB"
        assert self.download.piece_length_string(human_readable=False) == "524288 B"

    def test_progress(self) -> None:
        assert self.download.progress == self.download.completed_length / self.download.total_length * 100
        self.download._struct["totalLength"] = 0
        assert self.download.progress == 0.0

    def test_progress_string(self) -> None:
        progress = self.download.completed_length / self.download.total_length * 100
        assert self.download.progress_string() == f"{progress:.2f}%"
        self.download._struct["totalLength"] = 0
        assert self.download.progress_string() == "0.00%"

    def test_remove(self, server: Aria2Server) -> None:
        self.download.api = server.api
        with pytest.raises(ClientException):
            self.download.remove()

    def test_resume(self, server: Aria2Server) -> None:
        self.download.api = server.api
        with pytest.raises(ClientException):
            self.download.resume()

    def test_seeder(self) -> None:
        assert self.download.seeder is False

    def test_status(self) -> None:
        assert self.download.status == "active"

    def test_total_length(self) -> None:
        assert self.download.total_length == 1_045_306_068

    def test_total_length_string(self) -> None:
        assert self.download.total_length_string() == "996.88 MiB"
        assert self.download.total_length_string(human_readable=False) == "1045306068 B"

    def test_update(self, server: Aria2Server) -> None:
        self.download.api = server.api
        with pytest.raises(ClientException):
            self.download.update()

    def test_update_options(self, server: Aria2Server) -> None:
        self.download.api = server.api
        with pytest.raises(ClientException):
            self.download.update_options()

    def test_upload_length(self) -> None:
        assert self.download.upload_length == 97_207_027

    def test_upload_length_string(self) -> None:
        assert self.download.upload_length_string() == "92.70 MiB"
        assert self.download.upload_length_string(human_readable=False) == "97207027 B"

    def test_upload_speed(self) -> None:
        assert self.download.upload_speed == 11032

    def test_upload_speed_string(self) -> None:
        assert self.download.upload_speed_string() == "10.77 KiB/s"
        assert self.download.upload_speed_string(human_readable=False) == "11032 B/s"

    def test_verified_length(self) -> None:
        assert self.download.verified_length == 0

    def test_verified_length_string(self) -> None:
        assert self.download.verified_length_string() == "0.00 B"
        assert self.download.verified_length_string(human_readable=False) == "0 B"

    def test_verify_integrity_pending(self) -> None:
        assert self.download.verify_integrity_pending is None

    def test_is_torrent(self) -> None:
        assert self.download.is_torrent
        del self.download._struct["bittorrent"]
        assert not self.download.is_torrent


class TestFileClass:
    def setup_method(self) -> None:
        self.file = File(
            {
                "index": "1",
                "path": "/some/file/path.txt",
                "length": "2097152",
                "completedLength": "2048",
                "selected": "true",
                "uris": [{"uri": "some uri", "status": "used"}, {"uri": "some other uri", "status": "waiting"}],
            },
        )

    def test_eq_method(self) -> None:
        assert self.file == File({"path": "/some/file/path.txt"})

    def test_init_method(self) -> None:
        assert File({})

    def test_str_method(self) -> None:
        assert str(self.file) == str(self.file.path)

    def test_completed_length(self) -> None:
        assert self.file.completed_length == 2048

    def test_completed_length_string(self) -> None:
        assert self.file.completed_length_string() == "2.00 KiB"
        assert self.file.completed_length_string(human_readable=False) == "2048 B"

    def test_index(self) -> None:
        assert self.file.index == 1

    def test_length(self) -> None:
        assert self.file.length == 2_097_152

    def test_length_string(self) -> None:
        assert self.file.length_string() == "2.00 MiB"
        assert self.file.length_string(human_readable=False) == "2097152 B"

    def test_path(self) -> None:
        assert self.file.path == Path("/some/file/path.txt")

    def test_selected(self) -> None:
        assert self.file.selected is True

    def test_uris(self) -> None:
        assert self.file.uris == [{"uri": "some uri", "status": "used"}, {"uri": "some other uri", "status": "waiting"}]
