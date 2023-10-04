"""Tests for the `client` module."""

from __future__ import annotations

import json
import os
import signal
import threading
import time
from base64 import b64encode
from copy import deepcopy
from typing import TYPE_CHECKING

import pytest
import requests
from responses import mock as responses

from aria2p import Client, ClientException
from aria2p.client import JSONRPC_CODES, JSONRPC_PARSER_ERROR, Notification
from tests import BUNSENLABS_MAGNET, BUNSENLABS_TORRENT, CONFIGS_DIR, DEBIAN_METALINK, SESSIONS_DIR, XUBUNTU_MIRRORS
from tests.conftest import Aria2Server

if TYPE_CHECKING:
    from pathlib import Path


class TestParameters:
    # callback that return params of a single call as result
    @staticmethod
    def call_params_callback(request: pytest.RequestFixture) -> tuple[int, dict, list]:
        payload = json.loads(request.body)
        resp_body = {"result": payload["params"]}
        return 200, {}, json.dumps(resp_body)

    # callback that return params of a batch call as result
    @staticmethod
    def batch_call_params_callback(request: pytest.RequestFixture) -> tuple[int, dict, list]:
        payload = json.loads(request.body)
        resp_body = [{"result": method["params"]} for method in payload]
        return 200, {}, json.dumps(resp_body)

    @responses.activate
    def test_insert_secret_with_aria2_method_call(self) -> None:
        # create client with secret
        secret = "hello"  # noqa: S105
        client = Client(secret=secret)

        responses.add_callback(responses.POST, client.server, callback=self.call_params_callback)

        # create params
        params = ["param1", "param2"]
        # copy params and insert secret
        expected_params = deepcopy(params)
        expected_params.insert(0, f"token:{secret}")

        # call function and assert result
        resp = client.call(client.ADD_URI, params, insert_secret=True)
        assert resp == expected_params

    @responses.activate
    def test_insert_secret_with_system_multicall(self) -> None:
        # create client with secret
        secret = "hello"  # noqa: S105
        client = Client(secret=secret)

        responses.add_callback(responses.POST, client.server, callback=self.call_params_callback)

        # create params
        params = [
            [
                {"methodName": client.ADD_URI, "params": ["param1", "param2"]},
                {"methodName": client.ADD_URI, "params": ["param3", "param4"]},
            ],
        ]
        # copy params and insert secret
        expected_params = deepcopy(params)
        for param in expected_params[0]:
            param["params"].insert(0, f"token:{secret}")

        # call function and assert result
        resp = client.call(client.MULTICALL, params, insert_secret=True)
        assert resp == expected_params

    @responses.activate
    def test_does_not_insert_secret_with_unknown_method_call(self) -> None:
        # create client with secret
        secret = "hello"  # noqa: S105
        client = Client(secret=secret)

        responses.add_callback(responses.POST, client.server, callback=self.call_params_callback)

        # create params
        params = ["param1", "param2"]

        # call function and assert result
        resp = client.call("other.method", params, insert_secret=True)
        assert secret not in resp

    @responses.activate
    def test_does_not_insert_secret_if_told_so(self) -> None:
        # create client with secret
        secret = "hello"  # noqa: S105
        client = Client(secret=secret)

        responses.add_callback(responses.POST, client.server, callback=self.call_params_callback)

        # create params
        params = ["param1", "param2"]

        # call function and assert result
        resp = client.call("other.method", params, insert_secret=False)
        assert secret not in resp

    def test_client_str_returns_client_server(self) -> None:
        host = "https://localhost:8779/"
        port = 7100
        client = Client(host, port)
        assert client.server == f"{host.rstrip('/')}:{port}/jsonrpc" == str(client)

    @responses.activate
    def test_batch_call(self) -> None:
        client = Client()

        responses.add_callback(responses.POST, client.server, callback=self.batch_call_params_callback)

        # create params
        params_1 = ["param1", "param2"]
        params_2 = ["param3", "param4"]
        # copy params and insert secret
        expected_params = [params_1, params_2]

        # call function and assert result
        resp = client.batch_call([(client.ADD_URI, params_1, 0), (client.ADD_METALINK, params_2, 1)])
        assert resp == expected_params

    @responses.activate
    def test_insert_secret_with_batch_call(self) -> None:
        # create client with secret
        secret = "hello"  # noqa: S105
        client = Client(secret=secret)

        responses.add_callback(responses.POST, client.server, callback=self.batch_call_params_callback)

        # create params
        params_1 = ["param1", "param2"]
        params_2 = ["param3", "param4"]
        # copy params and insert secret
        expected_params = [deepcopy(params_1), deepcopy(params_2)]
        for p in expected_params:
            p.insert(0, f"token:{secret}")

        # call function and assert result
        resp = client.batch_call(
            [(client.ADD_URI, params_1, 0), (client.ADD_METALINK, params_2, 1)],
            insert_secret=True,
        )
        assert resp == expected_params

    @responses.activate
    def test_multicall2(self) -> None:
        client = Client()

        responses.add_callback(responses.POST, client.server, callback=self.call_params_callback)

        # create params
        params_1 = ["0000000000000001"]
        params_2 = ["2fa07b6e85c40205"]
        calls = [(client.REMOVE, params_1), (client.REMOVE, params_2)]
        # copy params and insert secret
        expected_params = [
            [
                {"methodName": client.REMOVE, "params": deepcopy(params_1)},
                {"methodName": client.REMOVE, "params": deepcopy(params_2)},
            ],
        ]

        # call function and assert result
        resp = client.multicall2(calls)
        assert resp == expected_params

    @responses.activate
    def test_insert_secret_with_multicall2(self) -> None:
        # create client with secret
        secret = "hello"  # noqa: S105
        client = Client(secret=secret)

        responses.add_callback(responses.POST, client.server, callback=self.call_params_callback)

        # create params
        params_1 = ["0000000000000001"]
        params_2 = ["2fa07b6e85c40205"]
        calls = [(client.REMOVE, params_1), (client.REMOVE, params_2)]
        # copy params and insert secret
        expected_params = [
            [
                {"methodName": client.REMOVE, "params": deepcopy(params_1)},
                {"methodName": client.REMOVE, "params": deepcopy(params_2)},
            ],
        ]
        for param in expected_params[0]:
            param["params"].insert(0, f"token:{secret}")

        # call function and assert result
        resp = client.multicall2(calls, insert_secret=True)
        assert resp == expected_params


class TestClientExceptionClass:
    @responses.activate
    def test_call_raises_custom_error(self) -> None:
        client = Client()
        responses.add(
            responses.POST,
            client.server,
            json={"error": {"code": 1, "message": "Custom message"}},
            status=200,
        )
        with pytest.raises(ClientException, match=r"Custom message") as e:  # noqa: PT012
            client.call("aria2.method")
            assert e.code == 1

    @responses.activate
    def test_call_raises_known_error(self) -> None:
        client = Client()
        responses.add(
            responses.POST,
            client.server,
            json={"error": {"code": JSONRPC_PARSER_ERROR, "message": "Custom message"}},
            status=200,
        )
        with pytest.raises(  # noqa: PT012
            ClientException,
            match=rf"{JSONRPC_CODES[JSONRPC_PARSER_ERROR]}\nCustom message",
        ) as e:
            client.call("aria2.method")
            assert e.code == JSONRPC_PARSER_ERROR


class TestClientClass:
    def test_add_metalink_method(self, server: Aria2Server) -> None:
        # get file contents
        with open(DEBIAN_METALINK, "rb") as stream:
            metalink_contents = stream.read()
        encoded_contents = b64encode(metalink_contents).decode("utf-8")

        assert server.client.add_metalink(encoded_contents)

    def test_add_torrent_method(self, server: Aria2Server) -> None:
        # get file contents
        with open(BUNSENLABS_TORRENT, "rb") as stream:
            torrent_contents = stream.read()
        encoded_contents = b64encode(torrent_contents).decode("utf-8")

        assert server.client.add_torrent(encoded_contents, [])

    def test_add_uri_method(self, server: Aria2Server) -> None:
        assert server.client.add_uri([BUNSENLABS_MAGNET])
        assert server.client.add_uri(XUBUNTU_MIRRORS)

    def test_global_option_methods(self, tmp_path: Path, port: int) -> None:
        with Aria2Server(tmp_path, port, config=CONFIGS_DIR / "max-5-dls.conf") as server:
            max_concurrent_downloads = server.client.get_global_option()["max-concurrent-downloads"]
            assert max_concurrent_downloads == "5"

            assert server.client.change_global_option({"max-concurrent-downloads": "10"}) == "OK"

            max_concurrent_downloads = server.client.get_global_option()["max-concurrent-downloads"]
            assert max_concurrent_downloads == "10"

    def test_option_methods(self, tmp_path: Path, port: int) -> None:
        with Aria2Server(tmp_path, port, session="max-dl-limit-10000.txt") as server:
            time.sleep(0.1)
            try:
                gid = server.client.tell_active(keys=["gid"])[0]["gid"]
            except IndexError:
                pytest.xfail("Failed to establish connection (sporadic error)")
            max_download_limit = server.client.get_option(gid=gid)["max-download-limit"]
            assert max_download_limit == "10000"

            assert server.client.change_option(gid, {"max-download-limit": "20000"}) == "OK"

            max_download_limit = server.client.get_option(gid)["max-download-limit"]
            assert max_download_limit == "20000"

    def test_position_method(self, tmp_path: Path, port: int) -> None:
        with Aria2Server(tmp_path, port, session="2-dls-paused.txt") as server:
            gids = server.client.tell_waiting(0, 5, keys=["gid"])
            first, second = (r["gid"] for r in gids)
            assert server.client.change_position(second, 0, "POS_SET") == 0
            assert server.client.change_position(second, 5, "POS_CUR") == 1

    def test_change_uri_method(self, tmp_path: Path, port: int) -> None:
        with Aria2Server(tmp_path, port, session="1-dl-2-uris.txt") as server:
            gid = server.client.tell_waiting(0, 1, keys=["gid"])[0]["gid"]
            assert server.client.change_uri(gid, 1, ["http://localhost:8779/1024"], ["http://localhost:8779/1k"]) == [
                1,
                1,
            ]
            assert server.client.change_uri(gid, 1, ["http://localhost:8779/1k"], []) == [1, 0]

    def test_force_pause_method(self, tmp_path: Path, port: int) -> None:
        with Aria2Server(tmp_path, port, session="big-download.txt") as server:
            time.sleep(0.1)
            try:
                gid = server.client.tell_active(keys=["gid"])[0]["gid"]
            except IndexError:
                pytest.xfail("Failed to establish connection (sporadic error)")
            assert server.client.force_pause(gid) == gid

    def test_force_pause_all_method(self, tmp_path: Path, port: int) -> None:
        with Aria2Server(tmp_path, port, session="2-dls.txt") as server:
            assert server.client.force_pause_all() == "OK"

    def test_force_remove_method(self, tmp_path: Path, port: int) -> None:
        with Aria2Server(tmp_path, port, session="big-download.txt") as server:
            try:
                gid = server.client.tell_active(keys=["gid"])[0]["gid"]
            except IndexError:
                pytest.xfail("Failed to establish connection (sporadic error)")
            assert server.client.force_remove(gid)
            assert server.client.tell_status(gid, keys=["status"])["status"] == "removed"

    def test_force_shutdown_method(self, server: Aria2Server) -> None:
        assert server.client.force_shutdown() == "OK"
        with pytest.raises(requests.ConnectionError):  # noqa: PT012
            for _retry in range(10):
                server.client.list_methods()
                time.sleep(1)

    def test_get_files_method(self, tmp_path: Path, port: int) -> None:
        with Aria2Server(tmp_path, port, session="1-dl.txt") as server:
            gid = server.client.tell_active(keys=["gid"])[0]["gid"]
            assert len(server.client.get_files(gid)) == 1

    def test_get_global_stat_method(self, server: Aria2Server) -> None:
        assert server.client.get_global_stat()

    def test_get_peers_method(self, tmp_path: Path, port: int) -> None:
        with Aria2Server(tmp_path, port, session="max-dl-limit-10000.txt") as server:
            time.sleep(0.1)
            try:
                gid = server.client.tell_active(keys=["gid"])[0]["gid"]
            except IndexError:
                pytest.xfail("Failed to establish connection (sporadic error)")
            assert not server.client.get_peers(gid)

    def test_get_servers_method(self, tmp_path: Path, port: int) -> None:
        with Aria2Server(tmp_path, port, session="max-dl-limit-10000.txt") as server:
            time.sleep(0.1)
            try:
                gid = server.client.tell_active(keys=["gid"])[0]["gid"]
            except IndexError:
                pytest.xfail("Failed to establish connection (sporadic error)")
            assert server.client.get_servers(gid)

    def test_get_session_info_method(self, server: Aria2Server) -> None:
        assert server.client.get_session_info()

    def test_get_uris_method(self, tmp_path: Path, port: int) -> None:
        with Aria2Server(tmp_path, port, session="1-dl-2-uris.txt") as server:
            gid = server.client.tell_waiting(0, 1, keys=["gid"])[0]["gid"]
            assert server.client.get_uris(gid) == [
                {"status": "waiting", "uri": "http://localhost:8779/1024"},
                {"status": "waiting", "uri": "http://localhost:8779/1k"},
            ]

    def test_get_version_method(self, server: Aria2Server) -> None:
        assert server.client.get_version()

    def test_list_methods_method(self, server: Aria2Server) -> None:
        assert server.client.list_methods()

    def test_list_notifications_method(self, server: Aria2Server) -> None:
        assert server.client.list_notifications()

    def test_multicall_method(self, server: Aria2Server) -> None:
        assert server.client.multicall(
            [[{"methodName": server.client.LIST_METHODS}, {"methodName": server.client.LIST_NOTIFICATIONS}]],
        )

    def test_multicall2_method(self, server: Aria2Server) -> None:
        assert server.client.multicall2([(server.client.LIST_METHODS, []), (server.client.LIST_NOTIFICATIONS, [])])

    def test_pause_method(self, tmp_path: Path, port: int) -> None:
        with Aria2Server(tmp_path, port, session="1-dl.txt") as server:
            time.sleep(0.1)
            try:
                gid = server.client.tell_active(keys=["gid"])[0]["gid"]
            except IndexError:
                pytest.xfail("Failed to establish connection (sporadic error)")
            assert server.client.pause(gid) == gid

    def test_pause_all_method(self, tmp_path: Path, port: int) -> None:
        with Aria2Server(tmp_path, port, session="2-dls.txt") as server:
            assert server.client.pause_all() == "OK"

    def test_purge_download_result_method(self, server: Aria2Server) -> None:
        assert server.client.purge_download_result() == "OK"

    def test_remove_method(self, tmp_path: Path, port: int) -> None:
        with Aria2Server(tmp_path, port, session="1-dl.txt") as server:
            time.sleep(0.1)
            try:
                gid = server.client.tell_active(keys=["gid"])[0]["gid"]
            except IndexError:
                pytest.xfail("Failed to establish connection (sporadic error)")
            assert server.client.remove(gid)
            assert server.client.tell_status(gid, keys=["status"])["status"] == "removed"

    def test_remove_download_result_method(self, tmp_path: Path, port: int) -> None:
        with Aria2Server(tmp_path, port, session="1-dl.txt") as server:
            time.sleep(0.1)
            try:
                gid = server.client.tell_active(keys=["gid"])[0]["gid"]
            except IndexError:
                pytest.xfail("Failed to establish connection (sporadic error)")
            server.client.remove(gid)
            assert server.client.remove_download_result(gid) == "OK"
            assert len(server.client.tell_stopped(0, 1)) == 0

    def test_save_session_method(self, tmp_path: Path, port: int) -> None:
        session_input = SESSIONS_DIR / "1-dl.txt"
        with Aria2Server(tmp_path, port, session=session_input) as server:
            session_output = server.tmp_dir / "_session.txt"
            server.client.change_global_option({"save-session": str(session_output)})
            assert server.client.save_session() == "OK"
            with open(session_input) as stream:
                input_contents = stream.read()
            with open(session_output) as stream:
                output_contents = stream.read()
            for line in input_contents.split("\n"):
                assert line in output_contents

    def test_shutdown_method(self, server: Aria2Server) -> None:
        assert server.client.shutdown() == "OK"
        with pytest.raises(requests.ConnectionError):  # noqa: PT012
            for _retry in range(10):
                server.client.list_methods()
                time.sleep(1)

    def test_tell_active_method(self, tmp_path: Path, port: int) -> None:
        with Aria2Server(tmp_path, port, session="big-download.txt") as server:
            time.sleep(0.1)
            if server.api.get_download("0000000000000001").has_failed:
                pytest.xfail("Failed to establish connection (sporadic error)")
            assert len(server.client.tell_active(keys=["gid"])) > 0

    def test_tell_status_method(self, tmp_path: Path, port: int) -> None:
        with Aria2Server(tmp_path, port, session="1-dl-paused.txt") as server:
            gid = server.client.tell_waiting(0, 1, keys=["gid"])[0]["gid"]
            assert server.client.tell_status(gid)

    def test_tell_stopped_method(self, tmp_path: Path, port: int) -> None:
        with Aria2Server(tmp_path, port, session="very-small-download.txt") as server:
            download = server.api.get_download("0000000000000001")
            while not download.live.is_complete:
                if download.has_failed:
                    pytest.xfail("Failed to establish connection (sporadic error)")
                time.sleep(0.1)
            assert len(server.client.tell_stopped(0, 1, keys=["gid"])) > 0

    def test_tell_waiting_method(self, tmp_path: Path, port: int) -> None:
        with Aria2Server(tmp_path, port, session="2-dls-paused.txt") as server:
            assert server.client.tell_waiting(0, 5, keys=["gid"]) == [
                {"gid": "0000000000000001"},
                {"gid": "0000000000000002"},
            ]

    def test_unpause_method(self, tmp_path: Path, port: int) -> None:
        with Aria2Server(tmp_path, port, session="1-dl-paused.txt") as server:
            gid = server.client.tell_waiting(0, 1, keys=["gid"])[0]["gid"]
            assert server.client.unpause(gid) == gid

    def test_unpause_all_method(self, tmp_path: Path, port: int) -> None:
        with Aria2Server(tmp_path, port, session="2-dls-paused.txt") as server:
            assert server.client.unpause_all() == "OK"

    def test_listen_to_notifications_no_server(self) -> None:
        client = Client(port=7035)
        client.listen_to_notifications(timeout=1)

    def test_listen_to_notifications_no_callbacks(self, tmp_path: Path, port: int) -> None:
        with Aria2Server(tmp_path, port, session="2-dls-paused.txt") as server:

            def thread_target() -> None:
                server.client.listen_to_notifications(timeout=1, handle_signals=False)

            thread = threading.Thread(target=thread_target)
            thread.start()
            server.client.unpause("0000000000000001")
            time.sleep(3)
        thread.join()

    def test_listen_to_notifications_callbacks(self, tmp_path: Path, port: int, capsys: pytest.CaptureFixture) -> None:
        with Aria2Server(tmp_path, port, session="2-dls-paused.txt") as server:

            def thread_target() -> None:
                server.client.listen_to_notifications(
                    on_download_start=lambda gid: print("started " + gid),  # noqa: T201
                    timeout=1,
                    handle_signals=False,
                )

            thread = threading.Thread(target=thread_target)
            thread.start()
            time.sleep(1)
            server.client.unpause("0000000000000001")
            time.sleep(3)
        thread.join()
        assert capsys.readouterr().out == "started 0000000000000001\n"

    def test_listen_to_notifications_then_stop(self, tmp_path: Path, port: int) -> None:
        with Aria2Server(tmp_path, port, session="2-dls-paused.txt") as server:

            def thread_target() -> None:
                server.client.listen_to_notifications(timeout=1, handle_signals=False)

            thread = threading.Thread(target=thread_target)
            thread.start()
            server.client.stop_listening()
            thread.join()

    def test_listen_to_notifications_then_stop_with_signal(self, tmp_path: Path, port: int) -> None:
        with Aria2Server(tmp_path, port, session="2-dls-paused.txt") as server:

            def thread_target() -> None:
                time.sleep(2)
                os.kill(os.getpid(), signal.SIGTERM)

            thread = threading.Thread(target=thread_target)
            thread.start()
            server.client.listen_to_notifications(timeout=1, handle_signals=True)
            thread.join()


class TestNotificationClass:
    def test_init(self) -> None:
        notification = Notification("random", "random")
        assert notification

    def test_get(self) -> None:
        message = {"method": "random_event", "params": [{"gid": "random_gid"}]}
        assert Notification.get_or_raise(message)

    def test_raise(self) -> None:
        message = {"error": {"code": 9000, "message": "it's over 9000"}}
        with pytest.raises(ClientException):
            Notification.get_or_raise(message)


class TestSecretToken:
    def test_works_correctly_with_secret_set(self, tmp_path: Path, port: int) -> None:
        with Aria2Server(tmp_path, port, secret="this secret token") as server:  # noqa: S106
            assert server.client.get_version()

    def test_does_not_authorize_with_invalid_secret(self, tmp_path: Path, port: int) -> None:
        with Aria2Server(tmp_path, port, secret="this secret token") as server:  # noqa: S106
            server.client.secret = "invalid secret token"  # noqa: S105
            with pytest.raises(ClientException):
                server.client.get_version()
