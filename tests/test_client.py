from responses import mock as responses
import pytest
import json
from copy import deepcopy
from contextlib import contextmanager

from aria2p import JSONRPCClient, JSONRPCError
from aria2p.client import JSONRPC_CODES, JSONRPC_PARSER_ERROR


# callback that return params of a single call as result
def call_params_callback(request):
    payload = json.loads(request.body)
    resp_body = {"result": payload["params"]}
    return 200, {}, json.dumps(resp_body)


# callback that return params of a batch call as result
def batch_call_params_callback(request):
    payload = json.loads(request.body)
    resp_body = [{"result": method["params"]} for method in payload]
    return 200, {}, json.dumps(resp_body)


@responses.activate
def test_call_raises_custom_error():
    client = JSONRPCClient()
    responses.add(responses.POST, client.server, json={"error": {"code": 1, "message": "Custom message"}}, status=200)
    with pytest.raises(JSONRPCError, match=r"Custom message") as e:
        client.call("aria2.method")
        assert e.code == 1


@responses.activate
def test_call_raises_known_error():
    client = JSONRPCClient()
    responses.add(responses.POST, client.server, json={"error": {"code": JSONRPC_PARSER_ERROR, "message": "Custom message"}}, status=200)
    with pytest.raises(JSONRPCError, match=rf"{JSONRPC_CODES[JSONRPC_PARSER_ERROR]}\nCustom message") as e:
        client.call("aria2.method")
        assert e.code == JSONRPC_PARSER_ERROR


@responses.activate
def test_insert_secret_with_aria2_method_call():
    # create client with secret
    secret = "hello"
    client = JSONRPCClient(secret=secret)

    responses.add_callback(responses.POST, client.server, callback=call_params_callback)

    # create params
    params = ["param1", "param2"]
    # copy params and insert secret
    expected_params = deepcopy(params)
    expected_params.insert(0, secret)

    # call function and assert result
    resp = client.call(client.ADD_URI, params, insert_secret=True)
    assert resp == expected_params


@responses.activate
def test_insert_secret_with_system_multicall():
    # create client with secret
    secret = "hello"
    client = JSONRPCClient(secret=secret)

    responses.add_callback(responses.POST, client.server, callback=call_params_callback)

    # create params
    params = [[
        {"methodName": client.ADD_URI, "params": ["param1", "param2"]},
        {"methodName": client.ADD_URI, "params": ["param3", "param4"]},
    ]]
    # copy params and insert secret
    expected_params = deepcopy(params)
    for param in expected_params[0]:
        param["params"].insert(0, secret)

    # call function and assert result
    resp = client.call(client.MULTICALL, params, insert_secret=True)
    assert resp == expected_params


@responses.activate
def test_does_not_insert_secret_with_unknown_method_call():
    # create client with secret
    secret = "hello"
    client = JSONRPCClient(secret=secret)

    responses.add_callback(responses.POST, client.server, callback=call_params_callback)

    # create params
    params = ["param1", "param2"]

    # call function and assert result
    resp = client.call("other.method", params, insert_secret=True)
    assert secret not in resp


@responses.activate
def test_does_not_insert_secret_if_told_so():
    # create client with secret
    secret = "hello"
    client = JSONRPCClient(secret=secret)

    responses.add_callback(responses.POST, client.server, callback=call_params_callback)

    # create params
    params = ["param1", "param2"]

    # call function and assert result
    resp = client.call("other.method", params, insert_secret=False)
    assert secret not in resp


def test_client_str_returns_client_server():
    host = "https://example.com/"
    port = 7100
    client = JSONRPCClient(host, port)
    assert client.server == f"{host.rstrip('/')}:{port}/jsonrpc" == str(client)


@responses.activate
def test_batch_call():
    client = JSONRPCClient()

    responses.add_callback(responses.POST, client.server, callback=batch_call_params_callback)

    # create params
    params_1 = ["param1", "param2"]
    params_2 = ["param3", "param4"]
    # copy params and insert secret
    expected_params = [params_1, params_2]

    # call function and assert result
    resp = client.batch_call([
        (client.ADD_URI, params_1, 0),
        (client.ADD_METALINK, params_2, 1),
    ])
    assert resp == expected_params


@responses.activate
def test_insert_secret_with_batch_call():
    # create client with secret
    secret = "hello"
    client = JSONRPCClient(secret=secret)

    responses.add_callback(responses.POST, client.server, callback=batch_call_params_callback)

    # create params
    params_1 = ["param1", "param2"]
    params_2 = ["param3", "param4"]
    # copy params and insert secret
    expected_params = [deepcopy(params_1), deepcopy(params_2)]
    for p in expected_params:
        p.insert(0, secret)

    # call function and assert result
    resp = client.batch_call([
        (client.ADD_URI, params_1, 0),
        (client.ADD_METALINK, params_2, 1),
    ], insert_secret=True)
    assert resp == expected_params


@responses.activate
def test_multicall2():
    client = JSONRPCClient()

    responses.add_callback(responses.POST, client.server, callback=call_params_callback)

    # create params
    params_1 = ["2089b05ecca3d829"]
    params_2 = ["2fa07b6e85c40205"]
    calls = [
        (client.REMOVE, params_1),
        (client.REMOVE, params_2),
    ]
    # copy params and insert secret
    expected_params = [[
        {"methodName": client.REMOVE, "params": deepcopy(params_1)},
        {"methodName": client.REMOVE, "params": deepcopy(params_2)},
    ]]

    # call function and assert result
    resp = client.multicall2(calls)
    assert resp == expected_params


@responses.activate
def test_insert_secret_with_multicall2():
    # create client with secret
    secret = "hello"
    client = JSONRPCClient(secret=secret)

    responses.add_callback(responses.POST, client.server, callback=call_params_callback)

    # create params
    params_1 = ["2089b05ecca3d829"]
    params_2 = ["2fa07b6e85c40205"]
    calls = [
        (client.REMOVE, params_1),
        (client.REMOVE, params_2),
    ]
    # copy params and insert secret
    expected_params = [[
        {"methodName": client.REMOVE, "params": deepcopy(params_1)},
        {"methodName": client.REMOVE, "params": deepcopy(params_2)},
    ]]
    for param in expected_params[0]:
        param["params"].insert(0, secret)

    # call function and assert result
    resp = client.multicall2(calls, insert_secret=True)
    assert resp == expected_params


class Aria2Server:
    def __init__(self, port, config, session):
        # create the client with port
        self.client = JSONRPCClient(port=port)
        # create the subprocess (pointing to config and session files) and store its PID

    def kill(self):
        pass


@contextmanager
def aria2_server(port, config, session):
    server = Aria2Server(port, config, session)
    yield server
    server.kill()


# def test_add_metalink_method():
#     with aria2_server(port=6810, config="", session="") as server:
#         assert server.client.add_metalink() == "OK"
#
#
# def test_add_torrent_method():
#     with aria2_server(port=6810, config="", session="") as server:
#         assert server.client.add_torrent() == "OK"
#
#
# def test_add_uri_method():
#     with aria2_server(port=6810, config="", session="") as server:
#         assert server.client.add_uri() == "OK"
#
#
# def test_batch_call_method():
#     with aria2_server(port=6810, config="", session="") as server:
#         assert server.client.batch_call() == "OK"
#
#
# def test_call_method():
#     with aria2_server(port=6810, config="", session="") as server:
#         assert server.client.call() == "OK"
#
#
# def test_change_global_option_method():
#     with aria2_server(port=6810, config="", session="") as server:
#         assert server.client.change_global_option() == "OK"
#
#
# def test_change_option_method():
#     with aria2_server(port=6810, config="", session="") as server:
#         assert server.client.change_option() == "OK"
#
#
# def test_change_position_method():
#     with aria2_server(port=6810, config="", session="") as server:
#         assert server.client.change_position() == "OK"
#
#
# def test_change_uri_method():
#     with aria2_server(port=6810, config="", session="") as server:
#         assert server.client.change_uri() == "OK"
#
#
# def test_force_pause_method():
#     with aria2_server(port=6810, config="", session="") as server:
#         assert server.client.force_pause() == "OK"
#
#
# def test_force_pause_all_method():
#     with aria2_server(port=6810, config="", session="") as server:
#         assert server.client.force_pause_all() == "OK"
#
#
# def test_force_remove_method():
#     with aria2_server(port=6810, config="", session="") as server:
#         assert server.client.force_remove() == "OK"
#
#
# def test_force_shutdown_method():
#     with aria2_server(port=6810, config="", session="") as server:
#         assert server.client.force_shutdown() == "OK"
#
#
# def test_get_files_method():
#     with aria2_server(port=6810, config="", session="") as server:
#         assert server.client.get_files() == "OK"
#
#
# def test_get_global_option_method():
#     with aria2_server(port=6810, config="", session="") as server:
#         assert server.client.get_global_option() == "OK"
#
#
# def test_get_global_stat_method():
#     with aria2_server(port=6810, config="", session="") as server:
#         assert server.client.get_global_stat() == "OK"
#
#
# def test_get_option_method():
#     with aria2_server(port=6810, config="", session="") as server:
#         assert server.client.get_option() == "OK"
#
#
# def test_get_peers_method():
#     with aria2_server(port=6810, config="", session="") as server:
#         assert server.client.get_peers() == "OK"
#
#
# def test_get_servers_method():
#     with aria2_server(port=6810, config="", session="") as server:
#         assert server.client.get_servers() == "OK"
#
#
# def test_get_session_info_method():
#     with aria2_server(port=6810, config="", session="") as server:
#         assert server.client.get_session_info() == "OK"
#
#
# def test_get_uris_method():
#     with aria2_server(port=6810, config="", session="") as server:
#         assert server.client.get_uris() == "OK"
#
#
# def test_get_version_method():
#     with aria2_server(port=6810, config="", session="") as server:
#         assert server.client.get_version() == "OK"
#
#
# def test_list_methods_method():
#     with aria2_server(port=6810, config="", session="") as server:
#         assert server.client.list_methods() == "OK"
#
#
# def test_list_notifications_method():
#     with aria2_server(port=6810, config="", session="") as server:
#         assert server.client.list_notifications() == "OK"
#
#
# def test_multicall_method():
#     with aria2_server(port=6810, config="", session="") as server:
#         assert server.client.multicall() == "OK"
#
#
# def test_multicall2_method():
#     with aria2_server(port=6810, config="", session="") as server:
#         assert server.client.multicall2() == "OK"
#
#
# def test_pause_method():
#     with aria2_server(port=6810, config="", session="") as server:
#         assert server.client.pause() == "OK"
#
#
# def test_pause_all_method():
#     with aria2_server(port=6810, config="", session="") as server:
#         assert server.client.pause_all() == "OK"
#
#
# def test_post_method():
#     with aria2_server(port=6810, config="", session="") as server:
#         assert server.client.post() == "OK"
#
#
# def test_purge_download_result_method():
#     with aria2_server(port=6810, config="", session="") as server:
#         assert server.client.purge_download_result() == "OK"
#
#
# def test_remove_method():
#     with aria2_server(port=6810, config="", session="") as server:
#         assert server.client.remove() == "OK"
#
#
# def test_remove_download_result_method():
#     with aria2_server(port=6810, config="", session="") as server:
#         assert server.client.remove_download_result() == "OK"
#
#
# def test_save_session_method():
#     with aria2_server(port=6810, config="", session="") as server:
#         assert server.client.save_session() == "OK"
#
#
# def test_shutdown_method():
#     with aria2_server(port=6810, config="", session="") as server:
#         assert server.client.shutdown() == "OK"
#
#
# def test_tell_active_method():
#     with aria2_server(port=6810, config="", session="") as server:
#         assert server.client.tell_active() == "OK"
#
#
# def test_tell_status_method():
#     with aria2_server(port=6810, config="", session="") as server:
#         assert server.client.tell_status() == "OK"
#
#
# def test_tell_stopped_method():
#     with aria2_server(port=6810, config="", session="") as server:
#         assert server.client.tell_stopped() == "OK"
#
#
# def test_tell_waiting_method():
#     with aria2_server(port=6810, config="", session="") as server:
#         assert server.client.tell_waiting() == "OK"
#
#
# def test_unpause_method():
#     with aria2_server(port=6810, config="", session="") as server:
#         assert server.client.unpause() == "OK"
#
#
# def test_unpause_all_method():
#     with aria2_server(port=6810, config="", session="") as server:
#         assert server.client.unpause_all() == "OK"


