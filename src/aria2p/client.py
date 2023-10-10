"""Client module.

This module defines the ClientException and Client classes, which are used to communicate with a remote aria2c
process through the JSON-RPC protocol.
"""

from __future__ import annotations

import json
from typing import Any, Callable, ClassVar, List, Tuple, Union

import requests
import websocket
from loguru import logger

from aria2p.utils import SignalHandler

DEFAULT_ID = -1
DEFAULT_HOST = "http://localhost"
DEFAULT_PORT = 6800
DEFAULT_TIMEOUT: float = 60.0

JSONRPC_PARSER_ERROR = -32700
JSONRPC_INVALID_REQUEST = -32600
JSONRPC_METHOD_NOT_FOUND = -32601
JSONRPC_INVALID_PARAMS = -32602
JSONRPC_INTERNAL_ERROR = -32603

JSONRPC_CODES = {
    JSONRPC_PARSER_ERROR: "Invalid JSON was received by the server.",
    JSONRPC_INVALID_REQUEST: "The JSON sent is not a valid Request object.",
    JSONRPC_METHOD_NOT_FOUND: "The method does not exist / is not available.",
    JSONRPC_INVALID_PARAMS: "Invalid method parameter(s).",
    JSONRPC_INTERNAL_ERROR: "Internal JSON-RPC error.",
}

NOTIFICATION_START = "aria2.onDownloadStart"
NOTIFICATION_PAUSE = "aria2.onDownloadPause"
NOTIFICATION_STOP = "aria2.onDownloadStop"
NOTIFICATION_COMPLETE = "aria2.onDownloadComplete"
NOTIFICATION_ERROR = "aria2.onDownloadError"
NOTIFICATION_BT_COMPLETE = "aria2.onBtDownloadComplete"

NOTIFICATION_TYPES = [
    NOTIFICATION_START,
    NOTIFICATION_PAUSE,
    NOTIFICATION_STOP,
    NOTIFICATION_COMPLETE,
    NOTIFICATION_ERROR,
    NOTIFICATION_BT_COMPLETE,
]

CallsType = List[Tuple[str, List[str], Union[str, int]]]
Multicalls2Type = List[Tuple[str, List[str]]]
CallReturnType = Union[dict, list, str, int]


class ClientException(Exception):  # noqa: N818
    """An exception specific to JSON-RPC errors."""

    def __init__(self, code: int, message: str) -> None:
        """Initialize the exception.

        Parameters:
            code: The error code.
            message: The error message.
        """
        super().__init__()
        if code in JSONRPC_CODES:
            message = f"{JSONRPC_CODES[code]}\n{message}"

        self.code = code
        self.message = message

    def __str__(self):
        return self.message

    def __bool__(self):
        return False


class Client:
    """The JSON-RPC client class.

    In this documentation, all the following terms refer to the same entity, the remote aria2c process:
    remote process, remote server, server, daemon process, background process, remote.

    This class implements method to communicate with a daemon aria2c process through the JSON-RPC protocol.
    Each method offered by the aria2c process is implemented in this class, in snake_case instead of camelCase
    (example: add_uri instead of addUri).

    The class defines a `METHODS` variable which contains the names of the available methods.

    The class is instantiated using an address and port, and optionally a secret token. The token is never passed
    as a method argument.

    The class provides utility methods:

    - `call`, which performs a JSON-RPC call for a single method;
    - `batch_call`, which performs a JSON-RPC call for a list of methods;
    - `multicall2`, which is an equivalent of multicall, but easier to use;
    - `post`, which is responsible for actually sending a payload to the remote process using a POST request;
    - `get_payload`, which is used to build payloads;
    - `get_params`, which is used to build list of parameters.
    """

    ADD_URI = "aria2.addUri"
    ADD_TORRENT = "aria2.addTorrent"
    ADD_METALINK = "aria2.addMetalink"
    REMOVE = "aria2.remove"
    FORCE_REMOVE = "aria2.forceRemove"
    PAUSE = "aria2.pause"
    PAUSE_ALL = "aria2.pauseAll"
    FORCE_PAUSE = "aria2.forcePause"
    FORCE_PAUSE_ALL = "aria2.forcePauseAll"
    UNPAUSE = "aria2.unpause"
    UNPAUSE_ALL = "aria2.unpauseAll"
    TELL_STATUS = "aria2.tellStatus"
    GET_URIS = "aria2.getUris"
    GET_FILES = "aria2.getFiles"
    GET_PEERS = "aria2.getPeers"
    GET_SERVERS = "aria2.getServers"
    TELL_ACTIVE = "aria2.tellActive"
    TELL_WAITING = "aria2.tellWaiting"
    TELL_STOPPED = "aria2.tellStopped"
    CHANGE_POSITION = "aria2.changePosition"
    CHANGE_URI = "aria2.changeUri"
    GET_OPTION = "aria2.getOption"
    CHANGE_OPTION = "aria2.changeOption"
    GET_GLOBAL_OPTION = "aria2.getGlobalOption"
    CHANGE_GLOBAL_OPTION = "aria2.changeGlobalOption"
    GET_GLOBAL_STAT = "aria2.getGlobalStat"
    PURGE_DOWNLOAD_RESULT = "aria2.purgeDownloadResult"
    REMOVE_DOWNLOAD_RESULT = "aria2.removeDownloadResult"
    GET_VERSION = "aria2.getVersion"
    GET_SESSION_INFO = "aria2.getSessionInfo"
    SHUTDOWN = "aria2.shutdown"
    FORCE_SHUTDOWN = "aria2.forceShutdown"
    SAVE_SESSION = "aria2.saveSession"
    MULTICALL = "system.multicall"
    LIST_METHODS = "system.listMethods"
    LIST_NOTIFICATIONS = "system.listNotifications"

    METHODS: ClassVar[list[str]] = [
        ADD_URI,
        ADD_TORRENT,
        ADD_METALINK,
        REMOVE,
        FORCE_REMOVE,
        PAUSE,
        PAUSE_ALL,
        FORCE_PAUSE,
        FORCE_PAUSE_ALL,
        UNPAUSE,
        UNPAUSE_ALL,
        TELL_STATUS,
        GET_URIS,
        GET_FILES,
        GET_PEERS,
        GET_SERVERS,
        TELL_ACTIVE,
        TELL_WAITING,
        TELL_STOPPED,
        CHANGE_POSITION,
        CHANGE_URI,
        GET_OPTION,
        CHANGE_OPTION,
        GET_GLOBAL_OPTION,
        CHANGE_GLOBAL_OPTION,
        GET_GLOBAL_STAT,
        PURGE_DOWNLOAD_RESULT,
        REMOVE_DOWNLOAD_RESULT,
        GET_VERSION,
        GET_SESSION_INFO,
        SHUTDOWN,
        FORCE_SHUTDOWN,
        SAVE_SESSION,
        MULTICALL,
        LIST_METHODS,
        LIST_NOTIFICATIONS,
    ]

    def __init__(
        self,
        host: str = DEFAULT_HOST,
        port: int = DEFAULT_PORT,
        secret: str = "",
        timeout: float = DEFAULT_TIMEOUT,
    ) -> None:
        """Initialize the object.

        Parameters:
            host: The remote process address.
            port: The remote process port.
            secret: The secret token.
            timeout: The timeout to use for requests towards the remote server.
        """
        host = host.rstrip("/")

        self.host = host
        self.port = port
        self.secret = secret
        self.timeout = timeout
        self.listening = False

    def __str__(self):
        return self.server

    def __repr__(self):
        return f"Client(host='{self.host}', port={self.port}, secret='********')"

    @property
    def server(self) -> str:
        """Return the full remote process / server address.

        Returns:
            The server address.
        """
        return f"{self.host}:{self.port}/jsonrpc"

    @property
    def ws_server(self) -> str:
        """Return the full WebSocket remote server address.

        Returns:
            The WebSocket server address.
        """
        return f"ws{self.host[4:]}:{self.port}/jsonrpc"

    def call(
        self,
        method: str,
        params: list[Any] | None = None,
        msg_id: int | str | None = None,
        insert_secret: bool = True,  # noqa: FBT001,FBT002
    ) -> CallReturnType:
        """Call a single JSON-RPC method.

        Parameters:
            method: The method name. You can use the constant defined in [`Client`][aria2p.client.Client].
            params: A list of parameters.
            msg_id: The ID of the call, sent back with the server's answer.
            insert_secret: Whether to insert the secret token in the parameters or not.

        Returns:
            The answer from the server, as a Python object.
        """
        params = self.get_params(*(params or []))

        if insert_secret and self.secret:
            if method.startswith("aria2."):
                params.insert(0, f"token:{self.secret}")
            elif method == self.MULTICALL:
                for param in params[0]:
                    param["params"].insert(0, f"token:{self.secret}")

        payload: str = self.get_payload(method, params, msg_id=msg_id)  # type: ignore
        return self.res_or_raise(self.post(payload))

    def batch_call(
        self,
        calls: CallsType,
        insert_secret: bool = True,  # noqa: FBT001,FBT002
    ) -> list[CallReturnType]:
        """Call multiple methods in one request.

        A batch call is simply a list of full payloads, sent at once to the remote process. The differences with a
        multicall are:

        - multicall is a special "system" method, whereas batch_call is simply the concatenation of several methods
        - multicall payloads define the "jsonrpc" and "id" keys only once, whereas these keys are repeated in
          each part of the batch_call payload
        - as a result of the previous line, you must pass different IDs to the batch_call methods, whereas the
          ID in multicall is optional

        Parameters:
            calls: A list of tuples composed of method name, parameters and ID.
            insert_secret: Whether to insert the secret token in the parameters or not.

        Returns:
            The results for each call in the batch.
        """
        payloads = []

        for method, params, msg_id in calls:
            params = self.get_params(*params)  # noqa: PLW2901
            if insert_secret and self.secret and method.startswith("aria2."):
                params.insert(0, f"token:{self.secret}")
            payloads.append(self.get_payload(method, params, msg_id, as_json=False))

        payload: str = json.dumps(payloads)
        responses = self.post(payload)
        return [self.res_or_raise(resp) for resp in responses]

    def multicall2(self, calls: Multicalls2Type, insert_secret: bool = True) -> CallReturnType:  # noqa: FBT001,FBT002
        """Call multiple methods in one request.

        A method equivalent to multicall, but with a simplified usage.

        Instead of providing dictionaries with "methodName" and "params" keys and values, this method allows you
        to provide the values only, in tuples of length 2.

        With a classic multicall, you would write your params like:

            [
                {"methodName": client.REMOVE, "params": ["0000000000000001"]},
                {"methodName": client.REMOVE, "params": ["2fa07b6e85c40205"]},
            ]

        With multicall2, you can reduce the verbosity:

            [
                (client.REMOVE, ["0000000000000001"]),
                (client.REMOVE, ["2fa07b6e85c40205"]),
            ]

        Note:
            multicall2 is not part of the JSON-RPC protocol specification.
            It is implemented here as a simple convenience method.

        Parameters:
            calls: List of tuples composed of method name and parameters.
            insert_secret: Whether to insert the secret token in the parameters or not.

        Returns:
            The answer from the server, as a Python object (dict / list / str / int).
        """
        multicall_params = []

        for method, params in calls:
            params = self.get_params(*params)  # noqa: PLW2901
            if insert_secret and self.secret and method.startswith("aria2."):
                params.insert(0, f"token:{self.secret}")
            multicall_params.append({"methodName": method, "params": params})

        payload: str = self.get_payload(self.MULTICALL, [multicall_params])  # type: ignore
        return self.res_or_raise(self.post(payload))

    def post(self, payload: str) -> dict:
        """Send a POST request to the server.

        The response is a JSON string, which we then load as a Python object.

        Parameters:
            payload: The payload / data to send to the remote process. It contains the following key-value pairs:
                "jsonrpc": "2.0", "method": method, "id": id, "params": params (optional).

        Returns:
            The answer from the server, as a Python dictionary.
        """
        return requests.post(self.server, data=payload, timeout=self.timeout).json()

    @staticmethod
    def response_as_exception(response: dict) -> ClientException:
        """Transform the response as a [`ClientException`][aria2p.client.ClientException] instance and return it.

        Parameters:
            response: A response sent by the server.

        Returns:
            An instance of the [`ClientException`][aria2p.client.ClientException] class.
        """
        return ClientException(response["error"]["code"], response["error"]["message"])

    @staticmethod
    def res_or_raise(response: dict) -> CallReturnType:
        """Return the result of the response, or raise an error with code and message.

        Parameters:
            response: A response sent by the server.

        Returns:
            The "result" value of the response.

        Raises:
            ClientException: When the response contains an error (client/server error).
                See the [`ClientException`][aria2p.client.ClientException] class.
        """
        if "error" in response:
            raise Client.response_as_exception(response)
        return response["result"]

    @staticmethod
    def get_payload(
        method: str,
        params: list[Any] | None = None,
        msg_id: int | str | None = None,
        as_json: bool = True,  # noqa: FBT001,FBT002
    ) -> str | dict:
        """Build a payload.

        Parameters:
            method: The method name. You can use the constant defined in [`Client`][aria2p.client.Client].
            params: The list of parameters.
            msg_id: The ID of the call, sent back with the server's answer.
            as_json: Whether to return the payload as a JSON-string or Python dictionary.

        Returns:
            The payload as a JSON string or as Python dictionary.
        """
        payload: dict[str, Any] = {"jsonrpc": "2.0", "method": method}

        if msg_id is None:
            payload["id"] = DEFAULT_ID
        else:
            payload["id"] = msg_id

        if params:
            payload["params"] = params

        return json.dumps(payload) if as_json else payload

    @staticmethod
    def get_params(*args: Any) -> list:
        """Build the list of parameters.

        This method simply removes the `None` values from the given arguments.

        Parameters:
            *args: List of parameters.

        Returns:
            A new list, with `None` values filtered out.
        """
        return [_ for _ in args if _ is not None]

    def add_uri(
        self,
        uris: list[str],
        options: dict | None = None,
        position: int | None = None,
    ) -> str:
        """Add a new download.

        This method adds a new download and returns the GID of the newly registered download.

        Original signature:

            aria2.addUri([secret], uris[, options[, position]])

        Parameters:
            uris: `uris` is an array of HTTP/FTP/SFTP/BitTorrent URIs (strings) pointing to the same resource.
                If you mix URIs pointing to different resources,
                then the download may fail or be corrupted without aria2 complaining.
                When adding BitTorrent Magnet URIs,
                uris must have only one element and it should be BitTorrent Magnet URI.
            options: `options` is a struct and its members are pairs of option name and value.
                See [Options][aria2p.options.Options] for more details.
            position: If `position` is given, it must be an integer starting from 0.
                The new download will be inserted at `position` in the waiting queue.
                If `position` is omitted or `position` is larger than the current size of the queue,
                the new download is appended to the end of the queue.

        Returns:
            The GID of the created download.

        Examples:
            **Original JSON-RPC Example**

            The following example adds http://example.org/file:

            >>> import urllib2, json
            >>> jsonreq = json.dumps({'jsonrpc':'2.0', 'id':'qwer',
            ...                       'method':'aria2.addUri',
            ...                       'params':[['http://example.org/file']]})
            >>> c = urllib2.urlopen('http://localhost:6800/jsonrpc', jsonreq)
            >>> c.read()
            '{"id":"qwer","jsonrpc":"2.0","result":"0000000000000001"}'
        """
        return self.call(self.ADD_URI, params=[uris, options, position])  # type: ignore

    def add_torrent(
        self,
        torrent: str,
        uris: list[str],
        options: dict | None = None,
        position: int | None = None,
    ) -> str:
        """Add a BitTorrent download.

        This method adds a BitTorrent download by uploading a ".torrent" file and returns the GID of the
        newly registered download.

        Original signature:

            aria2.addTorrent([secret], torrent[, uris[, options[, position]]])

        If you want to add a BitTorrent Magnet URI, use the [`add_uri()`][aria2p.client.Client.add_uri] method instead.

        If [`--rpc-save-upload-metadata`][aria2p.options.Options.rpc_save_upload_metadata] is true,
        the uploaded data is saved as a file named as the hex string of SHA-1 hash of data plus ".torrent"
        in the directory specified by [`--dir`][aria2p.options.Options.dir] option.
        E.g. a file name might be 0a3893293e27ac0490424c06de4d09242215f0a6.torrent.
        If a file with the same name already exists, it is overwritten!
        If the file cannot be saved successfully
        or [`--rpc-save-upload-metadata`][aria2p.options.Options.rpc_save_upload_metadata] is false,
        the downloads added by this method are not saved by [`--save-session`][aria2p.options.Options.save_session].

        Parameters:
            torrent: `torrent` must be a base64-encoded string containing the contents of the ".torrent" file.
            uris: `uris` is an array of URIs (string). `uris` is used for Web-seeding.
                For single file torrents, the URI can be a complete URI pointing to the resource; if URI ends with /,
                name in torrent file is added. For multi-file torrents, name and path in torrent are added to form a URI
                for each file.
            options: `options` is a struct and its members are pairs of option name and value.
                See [Options][aria2p.options.Options] for more details.
            position: If `position` is given, it must be an integer starting from 0.
                The new download will be inserted at `position` in the waiting queue.
                If `position` is omitted or `position` is larger than the current size of the queue,
                the new download is appended to the end of the queue.

        Returns:
            The GID of the created download.

        Examples:
            **Original JSON-RPC Example**

            The following examples add local file file.torrent.

            >>> import urllib2, json, base64
            >>> torrent = base64.b64encode(open('file.torrent').read())
            >>> jsonreq = json.dumps({'jsonrpc':'2.0', 'id':'asdf',
            ...                       'method':'aria2.addTorrent', 'params':[torrent]})
            >>> c = urllib2.urlopen('http://localhost:6800/jsonrpc', jsonreq)
            >>> c.read()
            '{"id":"asdf","jsonrpc":"2.0","result":"0000000000000001"}'
        """
        return self.call(self.ADD_TORRENT, [torrent, uris, options, position])  # type: ignore

    def add_metalink(
        self,
        metalink: str,
        options: dict | None = None,
        position: int | None = None,
    ) -> list[str]:
        """Add a Metalink download.

        This method adds a Metalink download by uploading a ".metalink" file
        and returns an array of GIDs of newly registered downloads.

        Original signature:

            aria2.addMetalink([secret], metalink[, options[, position]])

        If [`--rpc-save-upload-metadata`][aria2p.options.Options.rpc_save_upload_metadata] is true,
        the uploaded data is saved as a file named hex string of SHA-1 hash of data plus ".metalink"
        in the directory specified by [`--dir`][aria2p.options.Options.dir] option.
        E.g. a file name might be 0a3893293e27ac0490424c06de4d09242215f0a6.metalink.
        If a file with the same name already exists, it is overwritten!
        If the file cannot be saved successfully
        or [`--rpc-save-upload-metadata`][aria2p.options.Options.rpc_save_upload_metadata] is false,
        the downloads added by this method are not saved by [`--save-session`][aria2p.options.Options.save_session].

        Parameters:
            metalink: `metalink` is a base64-encoded string which contains the contents of the ".metalink" file.
            options: `options` is a struct and its members are pairs of option name and value.
                See [Options][aria2p.options.Options] for more details.
            position: If `position` is given, it must be an integer starting from 0.
                The new download will be inserted at `position` in the waiting queue.
                If `position` is omitted or `position` is larger than the current size of the queue,
                the new download is appended to the end of the queue.

        Returns:
            The GID of the created download.

        Examples:
            **Original JSON-RPC Example**

            The following examples add local file file.meta4.

            >>> import urllib2, json, base64
            >>> metalink = base64.b64encode(open('file.meta4').read())
            >>> jsonreq = json.dumps({'jsonrpc':'2.0', 'id':'qwer',
            ...                       'method':'aria2.addMetalink',
            ...                       'params':[metalink]})
            >>> c = urllib2.urlopen('http://localhost:6800/jsonrpc', jsonreq)
            >>> c.read()
            '{"id":"qwer","jsonrpc":"2.0","result":["0000000000000001"]}'
        """
        return self.call(self.ADD_METALINK, [metalink, options, position])  # type: ignore

    def remove(self, gid: str) -> str:
        """Remove a download.

        This method removes the download denoted by gid (string). If the specified download is in progress,
        it is first stopped. The status of the removed download becomes removed. This method returns GID of
        removed download.

        Original signature:

            aria2.remove([secret], gid)

        Parameters:
            gid: The download to remove.

        Returns:
            The GID of the removed download.

        Examples:
            **Original JSON-RPC Example**

            The following examples remove a download with GID#0000000000000001.

            >>> import urllib2, json
            >>> jsonreq = json.dumps({'jsonrpc':'2.0', 'id':'qwer',
            ...                       'method':'aria2.remove',
            ...                       'params':['0000000000000001']})
            >>> c = urllib2.urlopen('http://localhost:6800/jsonrpc', jsonreq)
            >>> c.read()
            '{"id":"qwer","jsonrpc":"2.0","result":"0000000000000001"}'
        """
        return self.call(self.REMOVE, [gid])  # type: ignore[return-value]

    def force_remove(self, gid: str) -> str:
        """Force remove a download.

        This method removes the download denoted by gid.
        This method behaves just like [`remove()`][aria2p.client.Client.remove] except
        that this method removes the download without performing any actions which take time, such as contacting
        BitTorrent trackers to unregister the download first.

        Original signature:

            aria2.forceRemove([secret], gid)

        Parameters:
            gid: The download to force remove.

        Returns:
            The GID of the removed download.
        """
        return self.call(self.FORCE_REMOVE, [gid])  # type: ignore

    def pause(self, gid: str) -> str:
        """Pause a download.

        This method pauses the download denoted by gid (string).
        The status of paused download becomes paused.
        If the download was active, the download is placed in the front of waiting queue.
        While the status is paused, the download is not started.
        To change status to waiting, use the [`unpause()`][aria2p.client.Client.unpause] method.

        Original signature:

            aria2.pause([secret], gid)

        Parameters:
            gid: The download to pause.

        Returns:
            The GID of the paused download.
        """
        return self.call(self.PAUSE, [gid])  # type: ignore

    def pause_all(self) -> str:
        """Pause all active/waiting downloads.

        This method is equal to calling [`pause()`][aria2p.client.Client.pause] for every active/waiting download.

        Original signature:

            aria2.pauseAll([secret])

        Returns:
            `"OK"`.
        """
        return self.call(self.PAUSE_ALL)  # type: ignore

    def force_pause(self, gid: str) -> str:
        """Force pause a download.

        This method pauses the download denoted by gid.
        This method behaves just like [`pause()`][aria2p.client.Client.pause] except that
        this method pauses downloads without performing any actions which take time,
        such as contacting BitTorrent trackers to unregister the download first.

        Original signature:

            aria2.forcePause([secret], gid)

        Parameters:
            gid: The download to force pause.

        Returns:
            The GID of the paused download.
        """
        return self.call(self.FORCE_PAUSE, [gid])  # type: ignore

    def force_pause_all(self) -> str:
        """Force pause all active/waiting downloads.

        This method is equal to calling [`force_pause()`][aria2p.client.Client.force_pause] for every active/waiting download.

        Original signature:

            aria2.forcePauseAll([secret])

        Returns:
            `"OK"`.
        """
        return self.call(self.FORCE_PAUSE_ALL)  # type: ignore

    def unpause(self, gid: str) -> str:
        """Resume a download.

        This method changes the status of the download denoted by gid (string) from paused to waiting,
        making the download eligible to be restarted. This method returns the GID of the unpaused download.

        Original signature:

            aria2.unpause([secret], gid)

        Parameters:
            gid: The download to resume.

        Returns:
            The GID of the resumed download.
        """
        return self.call(self.UNPAUSE, [gid])  # type: ignore

    def unpause_all(self) -> str:
        """Resume all downloads.

        This method is equal to calling [`unpause()`][aria2p.client.Client.unpause] for every active/waiting download.

        Original signature:

            aria2.unpauseAll([secret])

        Returns:
            `"OK"`.
        """
        return self.call(self.UNPAUSE_ALL)  # type: ignore

    def tell_status(self, gid: str, keys: list[str] | None = None) -> dict:
        """Tell status of a download.

        This method returns the progress of the download denoted by gid (string). keys is an array of strings. If
        specified, the response contains only keys in the keys array. If keys is empty or omitted, the response
        contains all keys. This is useful when you just want specific keys and avoid unnecessary transfers. For
        example, `tell_status("0000000000000001", ["gid", "status"])` returns the gid and status keys only. The
        response is a struct and contains following keys. Values are strings.

        - `gid`: GID of the download.
        - `status`: active for currently downloading/seeding downloads. waiting for downloads in the queue; download is
          not started. paused for paused downloads. error for downloads that were stopped because of error.
          complete for stopped and completed downloads. removed for the downloads removed by user.
        - `totalLength`: Total length of the download in bytes.
        - `completedLength`: Completed length of the download in bytes.
        - `uploadLength`: Uploaded length of the download in bytes.
        - `bitfield`: Hexadecimal representation of the download progress. The highest bit corresponds to the piece at
          index 0. Any set bits indicate loaded pieces, while unset bits indicate not yet loaded and/or missing
          pieces. Any overflow bits at the end are set to zero. When the download was not started yet, this key
          will not be included in the response.
        - `downloadSpeed`: Download speed of this download measured in bytes/sec.
        - `uploadSpeed`: Upload speed of this download measured in bytes/sec.
        - `infoHash`: InfoHash. BitTorrent only.
        - `numSeeders`: The number of seeders aria2 has connected to. BitTorrent only.
        - `seeder` true if the local endpoint is a seeder. Otherwise false. BitTorrent only.
        - `pieceLength`: Piece length in bytes.
        - `numPieces`: The number of pieces.
        - `connections`: The number of peers/servers aria2 has connected to.
        - `errorCode`: The code of the last error for this item, if any. The value is a string. The error codes are defined
          in the EXIT STATUS section. This value is only available for stopped/completed downloads.
        - `errorMessage`: The (hopefully) human readable error message associated to errorCode.
        - `followedBy`: List of GIDs which are generated as the result of this download. For example, when aria2 downloads a
          Metalink file, it generates downloads described in the Metalink
          (see the [`--follow-metalink`][aria2p.options.Options.follow_metalink] option).
          This value is useful to track auto-generated downloads. If there are no such downloads,
          this key will not be included in the response.
        - `following`: The reverse link for followedBy.
          A download included in followedBy has this object's GID in its following value.
        - `belongsTo`: GID of a parent download. Some downloads are a part of another download. For example, if a file in a
          Metalink has BitTorrent resources, the downloads of ".torrent" files are parts of that parent. If
          this download has no parent, this key will not be included in the response.
        - `dir`:Directory to save files.
        - `files`: Return the list of files.
          The elements of this list are the same structs used in [`get_files()`][aria2p.client.Client.get_files] method.
        - `bittorrent`: Struct which contains information retrieved from the .torrent (file). BitTorrent only.
          It contains the following keys:
            - `announceList`: List of lists of announce URIs. If the torrent contains announce and no announce-list, announce
              is converted to the announce-list format.
            - `comment`: The comment of the torrent. comment.utf-8 is used if available.
            - `creationDate`: The creation time of the torrent. The value is an integer since the epoch, measured in seconds.
            - `mode`: File mode of the torrent. The value is either single or multi.
            - `info`: Struct which contains data from Info dictionary. It contains following keys.
                - `name`: name in info dictionary. name.utf-8 is used if available.
        - `verifiedLength`: The number of verified number of bytes while the files are being hash checked. This key exists only
          when this download is being hash checked.
        - `verifyIntegrityPending`: true if this download is waiting for the hash check in a queue.
          This key exists only when this download is in the queue.

        Original signature:

            aria2.tellStatus([secret], gid[, keys])

        Parameters:
            gid: The download to tell status of.
            keys: The keys to return.

        Returns:
            The details of a download.

        Examples:
            **Original JSON-RPC Example**

            The following example gets information about a download with GID#0000000000000001:

            >>> import urllib2, json
            >>> from pprint import pprint
            >>> jsonreq = json.dumps({'jsonrpc':'2.0', 'id':'qwer',
            ...                       'method':'aria2.tellStatus',
            ...                       'params':['0000000000000001']})
            >>> c = urllib2.urlopen('http://localhost:6800/jsonrpc', jsonreq)
            >>> pprint(json.loads(c.read()))
            {u'id': u'qwer',
             u'jsonrpc': u'2.0',
             u'result': {u'bitfield': u'0000000000',
                         u'completedLength': u'901120',
                         u'connections': u'1',
                         u'dir': u'/downloads',
                         u'downloadSpeed': u'15158',
                         u'files': [{u'index': u'1',
                                     u'length': u'34896138',
                                     u'completedLength': u'34896138',
                                     u'path': u'/downloads/file',
                                     u'selected': u'true',
                                     u'uris': [{u'status': u'used',
                                                u'uri': u'http://example.org/file'}]}],
                         u'gid': u'0000000000000001',
                         u'numPieces': u'34',
                         u'pieceLength': u'1048576',
                         u'status': u'active',
                         u'totalLength': u'34896138',
                         u'uploadLength': u'0',
                         u'uploadSpeed': u'0'}}

            The following example gets only specific keys:

            >>> jsonreq = json.dumps({'jsonrpc':'2.0', 'id':'qwer',
            ...                       'method':'aria2.tellStatus',
            ...                       'params':['0000000000000001',
            ...                                 ['gid',
            ...                                  'totalLength',
            ...                                  'completedLength']]})
            >>> c = urllib2.urlopen('http://localhost:6800/jsonrpc', jsonreq)
            >>> pprint(json.loads(c.read()))
            {u'id': u'qwer',
             u'jsonrpc': u'2.0',
             u'result': {u'completedLength': u'5701632',
                         u'gid': u'0000000000000001',
                         u'totalLength': u'34896138'}}
        """
        return self.call(self.TELL_STATUS, [gid, keys])  # type: ignore

    def get_uris(self, gid: str) -> dict:
        """Return URIs used in a download.

        This method returns the URIs used in the download denoted by gid (string). The response is an array of
        structs and it contains following keys. Values are string.

        - `uri`: URI
        - `status`: 'used' if the URI is in use. 'waiting' if the URI is still waiting in the queue.

        Original signature:

            aria2.getUris([secret], gid)

        Parameters:
            gid: The download to list URIs of.

        Returns:
            The URIs used in a download.

        Examples:
            **Original JSON-RPC Example**

            >>> import urllib2, json
            >>> from pprint import pprint
            >>> jsonreq = json.dumps({'jsonrpc':'2.0', 'id':'qwer',
            ...                       'method':'aria2.getUris',
            ...                       'params':['0000000000000001']})
            >>> c = urllib2.urlopen('http://localhost:6800/jsonrpc', jsonreq)
            >>> pprint(json.loads(c.read()))
            {u'id': u'qwer',
             u'jsonrpc': u'2.0',
             u'result': [{u'status': u'used',
                          u'uri': u'http://example.org/file'}]}
        """
        return self.call(self.GET_URIS, [gid])  # type: ignore

    def get_files(self, gid: str) -> dict:
        """Return file list of a download.

        This method returns the file list of the download denoted by gid (string). The response is an array of
        structs which contain following keys. Values are strings.

        - `index`: Index of the file, starting at 1, in the same order as files appear in the multi-file torrent.
        - `path`: File path.
        - `length`: File size in bytes.
        - `completedLength`: Completed length of this file in bytes.
          Please note that it is possible that sum of `completedLength`
          is less than the `completedLength` returned by the [`tell_status()`][aria2p.client.Client.tell_status] method.
          This is because `completedLength` in [`get_files()`][aria2p.client.Client.get_files] only includes completed pieces.
          On the other hand, `completedLength` in [`tell_status()`][aria2p.client.Client.tell_status]
          also includes partially completed pieces.
        - `selected`: true if this file is selected by [`--select-file`][aria2p.options.Options.select_file] option.
          If [`--select-file`][aria2p.options.Options.select_file] is not specified
          or this is single-file torrent or not a torrent download at all, this value is always true. Otherwise false.
        - `uris` Returns a list of URIs for this file.
          The element type is the same struct used in the [`get_uris()`][aria2p.client.Client.get_uris] method.

        Original signature:

            aria2.getFiles([secret], gid)

        Parameters:
            gid: The download to list files of.

        Returns:
            The file list of a download.

        Examples:
            **Original JSON-RPC Example**

            >>> import urllib2, json
            >>> from pprint import pprint
            >>> jsonreq = json.dumps({'jsonrpc':'2.0', 'id':'qwer',
            ...                       'method':'aria2.getFiles',
            ...                       'params':['0000000000000001']})
            >>> c = urllib2.urlopen('http://localhost:6800/jsonrpc', jsonreq)
            >>> pprint(json.loads(c.read()))
            {u'id': u'qwer',
             u'jsonrpc': u'2.0',
             u'result': [{u'index': u'1',
                          u'length': u'34896138',
                          u'completedLength': u'34896138',
                          u'path': u'/downloads/file',
                          u'selected': u'true',
                          u'uris': [{u'status': u'used',
                                     u'uri': u'http://example.org/file'}]}]}
        """
        return self.call(self.GET_FILES, [gid])  # type: ignore

    def get_peers(self, gid: str) -> dict:
        """Return peers list of a download.

        This method returns the list of peers of the download denoted by gid (string). This method is for BitTorrent
        only. The response is an array of structs and contains the following keys. Values are strings.

        - `peerId`: Percent-encoded peer ID.
        - `ip`: IP address of the peer.
        - `port`: Port number of the peer.
        - `bitfield`: Hexadecimal representation of the download progress of the peer. The highest bit corresponds to
          the piece at index 0. Set bits indicate the piece is available and unset bits indicate the piece is
          missing. Any spare bits at the end are set to zero.
        - `amChoking`: true if aria2 is choking the peer. Otherwise false.
        - `peerChoking`: true if the peer is choking aria2. Otherwise false.
        - `downloadSpeed`: Download speed (byte/sec) that this client obtains from the peer.
        - `uploadSpeed`: Upload speed(byte/sec) that this client uploads to the peer.
        - `seeder`: true if this peer is a seeder. Otherwise false.

        Original signature:

            aria2.getPeers([secret], gid)

        Parameters:
            gid: The download to get peers from.

        Returns:
            The peers connected to a download.

        Examples:
            **Original JSON-RPC Example**

            >>> import urllib2, json
            >>> from pprint import pprint
            >>> jsonreq = json.dumps({'jsonrpc':'2.0', 'id':'qwer',
            ...                       'method':'aria2.getPeers',
            ...                       'params':['0000000000000001']})
            >>> c = urllib2.urlopen('http://localhost:6800/jsonrpc', jsonreq)
            >>> pprint(json.loads(c.read()))
            {u'id': u'qwer',
             u'jsonrpc': u'2.0',
             u'result': [{u'amChoking': u'true',
                          u'bitfield': u'ffffffffffffffffffffffffffffffffffffffff',
                          u'downloadSpeed': u'10602',
                          u'ip': u'10.0.0.9',
                          u'peerChoking': u'false',
                          u'peerId': u'aria2%2F1%2E10%2E5%2D%87%2A%EDz%2F%F7%E6',
                          u'port': u'6881',
                          u'seeder': u'true',
                          u'uploadSpeed': u'0'},
                         {u'amChoking': u'false',
                          u'bitfield': u'ffffeff0fffffffbfffffff9fffffcfff7f4ffff',
                          u'downloadSpeed': u'8654',
                          u'ip': u'10.0.0.30',
                          u'peerChoking': u'false',
                          u'peerId': u'bittorrent client758',
                          u'port': u'37842',
                          u'seeder': u'false',
                          u'uploadSpeed': u'6890'}]}
        """
        return self.call(self.GET_PEERS, [gid])  # type: ignore

    def get_servers(self, gid: str) -> dict:
        """Return servers currently connected for a download.

        This method returns currently connected HTTP(S)/FTP/SFTP servers of the download denoted by gid (string). The
        response is an array of structs and contains the following keys. Values are strings.

        - `index`: Index of the file, starting at 1, in the same order as files appear in the multi-file metalink.
        - `servers`: A list of structs which contain the following keys.
            - `uri`: Original URI.
            - `currentUri`: This is the URI currently used for downloading.
              If redirection is involved, currentUri and uri may differ.
            - `downloadSpeed`: Download speed (byte/sec).

        Original signature:

            aria2.getServers([secret], gid)

        Parameters:
            gid: The download to get servers from.

        Returns:
            The servers connected to a download.

        Examples:
            **Original JSON-RPC Example**

            >>> import urllib2, json
            >>> from pprint import pprint
            >>> jsonreq = json.dumps({'jsonrpc':'2.0', 'id':'qwer',
            ...                       'method':'aria2.getServers',
            ...                       'params':['0000000000000001']})
            >>> c = urllib2.urlopen('http://localhost:6800/jsonrpc', jsonreq)
            >>> pprint(json.loads(c.read()))
            {u'id': u'qwer',
             u'jsonrpc': u'2.0',
             u'result': [{u'index': u'1',
                          u'servers': [{u'currentUri': u'http://example.org/file',
                                        u'downloadSpeed': u'10467',
                                        u'uri': u'http://example.org/file'}]}]}
        """
        return self.call(self.GET_SERVERS, [gid])  # type: ignore

    def tell_active(self, keys: list[str] | None = None) -> list[dict]:
        """Return the list of active downloads.

        Original signature:

            aria2.tellActive([secret][, keys])

        Parameters:
            keys: The keys to return. Please refer to the [`tell_status()`][aria2p.client.Client.tell_status] method.

        Returns:
            An array of the same structs as returned by the [`tell_status()`][aria2p.client.Client.tell_status] method.
        """
        return self.call(self.TELL_ACTIVE, [keys])  # type: ignore

    def tell_waiting(self, offset: int, num: int, keys: list[str] | None = None) -> list[dict]:
        """Return the list of waiting downloads.

        This method returns a list of waiting downloads, including paused ones.

        Original signature:

            aria2.tellWaiting([secret], offset, num[, keys])

        Parameters:
            offset: An integer to specify the offset from the download waiting at the front.
                If `offset` is a positive integer, this method returns downloads in the range of [`offset`, `offset` + `num`).
                `offset` can be a negative integer. `offset == -1` points last download in the waiting queue and `offset == -2`
                points the download before the last download, and so on. Downloads in the response are in reversed order then.
                For example, imagine three downloads "A","B" and "C" are waiting in this order. `tell_waiting(0, 1)`
                returns `["A"]`. `tell_waiting(1, 2)` returns `["B", "C"]`. `tell_waiting(-1, 2)` returns `["C", "B"]`.
            num: An integer to specify the maximum number of downloads to be returned.
            keys: The keys to return. Please refer to the [`tell_status()`][aria2p.client.Client.tell_status] method.

        Returns:
            An array of the same structs as returned by [`tell_status()`][aria2p.client.Client.tell_status] method.
        """
        return self.call(self.TELL_WAITING, [offset, num, keys])  # type: ignore

    def tell_stopped(self, offset: int, num: int, keys: list[str] | None = None) -> list[dict]:
        """Return the list of stopped downloads.

        This method returns a list of stopped downloads. offset is an integer and specifies the offset from the
        least recently stopped download.

        Original signature:

            aria2.tellStopped([secret], offset, num[, keys])

        Parameters:
            offset: Same semantics as described in the [`tell_waiting()`][aria2p.client.Client.tell_waiting] method.
            num: An integer to specify the maximum number of downloads to be returned.
            keys: The keys to return. Please refer to the [`tell_status()`][aria2p.client.Client.tell_status] method.

        Returns:
            An array of the same structs as returned by the [`tell_status()`][aria2p.client.Client.tell_status] method.
        """
        return self.call(self.TELL_STOPPED, [offset, num, keys])  # type: ignore

    def change_position(self, gid: str, pos: int, how: str) -> int:
        """Change position of a download.

        This method changes the position of the download denoted by `gid` in the queue.

        Original signature:

            aria2.changePosition([secret], gid, pos, how)

        Parameters:
            gid: The download to change the position of.
            pos: An integer.
            how: `POS_SET`, `POS_CUR` or `POS_END`.

                - If `how` is `POS_SET`, it moves the download to a position relative to the beginning of the queue.
                - If `how` is `POS_CUR`, it moves the download to a position relative to the current position.
                - If `how` is `POS_END`, it moves the download to a position relative to the end of the queue.
                - If the destination position is less than 0 or beyond the end of the queue,
                  it moves the download to the beginning or the end of the queue respectively.

                For example, if GID#0000000000000001 is currently in position 3,
                `change_position('0000000000000001', -1, 'POS_CUR')` will change its position to 2. Additionally
                `change_position('0000000000000001', 0, 'POS_SET')` will change its position to 0 (the beginning of the queue).

        Returns:
            An integer denoting the resulting position.

        Examples:
            **Original JSON-RPC Example**

            The following examples move the download GID#0000000000000001 to the front of the queue.

            >>> import urllib2, json
            >>> from pprint import pprint
            >>> jsonreq = json.dumps({'jsonrpc':'2.0', 'id':'qwer',
            ...                       'method':'aria2.changePosition',
            ...                       'params':['0000000000000001', 0, 'POS_SET']})
            >>> c = urllib2.urlopen('http://localhost:6800/jsonrpc', jsonreq)
            >>> pprint(json.loads(c.read()))
            {u'id': u'qwer', u'jsonrpc': u'2.0', u'result': 0}
        """
        return self.call(self.CHANGE_POSITION, [gid, pos, how])  # type: ignore

    def change_uri(
        self,
        gid: str,
        file_index: int,
        del_uris: list[str],
        add_uris: list[str],
        position: int | None = None,
    ) -> list[int]:
        """Remove the URIs in `del_uris` from and appends the URIs in `add_uris` to download denoted by gid.

        Original signature:

            aria2.changeUri([secret], gid, fileIndex, delUris, addUris[, position])

        Parameters:
            gid: The download to change URIs of.
            file_index: Used to select which file to remove/attach given URIs. `file_index` is 1-based.
            del_uris: List of strings.
            add_uris: List of strings.
            position: Used to specify where URIs are inserted in the existing waiting URI list. `position` is 0-based.
                When position is omitted, URIs are appended to the back of the list.
                This method first executes the removal and then the addition.
                `position` is the position after URIs are removed, not the position when this
                method is called.

        A download can contain multiple files and URIs are attached to each file.
        When removing an URI, if the same URIs exist in download, only one of them is removed for
        each URI in `del_uris`. In other words, if there are three URIs http://example.org/aria2 and you want
        remove them all, you have to specify (at least) 3 http://example.org/aria2 in `del_uris`.

        Returns:
            A list which contains two integers.
            The first integer is the number of URIs deleted.
            The second integer is the number of URIs added.

        Examples:
            **Original JSON-RPC Example**

            The following examples add the URI http://example.org/file to the file whose index is 1 and belongs to the
            download GID#0000000000000001.

            >>> import urllib2, json
            >>> from pprint import pprint
            >>> jsonreq = json.dumps({'jsonrpc':'2.0', 'id':'qwer',
            ...                       'method':'aria2.changeUri',
            ...                       'params':['0000000000000001', 1, [],
                                               ['http://example.org/file']]})
            >>> c = urllib2.urlopen('http://localhost:6800/jsonrpc', jsonreq)
            >>> pprint(json.loads(c.read()))
            {u'id': u'qwer', u'jsonrpc': u'2.0', u'result': [0, 1]}
        """
        return self.call(self.CHANGE_URI, [gid, file_index, del_uris, add_uris, position])  # type: ignore

    def get_option(self, gid: str) -> dict:
        """Return options of a download.

        Original signature:

            aria2.getOption([secret], gid)

        Parameters:
            gid: The download to get the options of.

        Returns:
            A struct where keys are the names of options. The values are strings.
            Note that this method does not return options which have
            no default value and have not been set on the command-line, in configuration files or RPC methods.

        Examples:
            **Original JSON-RPC Example**

            The following examples get options of the download GID#0000000000000001.

            >>> import urllib2, json
            >>> from pprint import pprint
            >>> jsonreq = json.dumps({'jsonrpc':'2.0', 'id':'qwer',
            ...                       'method':'aria2.getOption',
            ...                       'params':['0000000000000001']})
            >>> c = urllib2.urlopen('http://localhost:6800/jsonrpc', jsonreq)
            >>> pprint(json.loads(c.read()))
            {u'id': u'qwer',
             u'jsonrpc': u'2.0',
             u'result': {u'allow-overwrite': u'false',
                         u'allow-piece-length-change': u'false',
                         u'always-resume': u'true',
                         u'async-dns': u'true',
             ...
        """
        return self.call(self.GET_OPTION, [gid])  # type: ignore

    def change_option(self, gid: str, options: dict) -> str:
        """Change a download options dynamically.

        Original signature:

            aria2.changeOption([secret], gid, options)

        Parameters:
            gid: The download to change options of.
            options: The options listed in Input File subsection are available, except for following options:

                - `dry-run`
                - `metalink-base-uri`
                - `parameterized-uri`
                - `pause`
                - `piece-length`
                - `rpc-save-upload-metadata`

                Except for the following options, changing the other options of active download makes it restart (restart
                itself is managed by aria2, and no user intervention is required):

                - `bt-max-peers`
                - `bt-request-peer-speed-limit`
                - `bt-remove-unselected-file`
                - `force-save`
                - `max-download-limit`
                - `max-upload-limit`

        Returns:
            `"OK"` for success.

        Examples:
            **Original JSON-RPC Example**

            The following examples set the max-download-limit option to 20K for the download GID#0000000000000001.

            >>> import urllib2, json
            >>> from pprint import pprint
            >>> jsonreq = json.dumps({'jsonrpc':'2.0', 'id':'qwer',
            ...                       'method':'aria2.changeOption',
            ...                       'params':['0000000000000001',
            ...                                 {'max-download-limit':'10K'}]})
            >>> c = urllib2.urlopen('http://localhost:6800/jsonrpc', jsonreq)
            >>> pprint(json.loads(c.read()))
            {u'id': u'qwer', u'jsonrpc': u'2.0', u'result': u'OK'}
        """
        return self.call(self.CHANGE_OPTION, [gid, options])  # type: ignore

    def get_global_option(self) -> dict:
        """Return the global options.

        Note that this method does not return options which have no default value and have not
        been set on the command-line, in configuration files or RPC methods. Because global options are used as a
        template for the options of newly added downloads, the response contains keys returned by the
        [`get_option()`][aria2p.client.Client.get_option] method.

        Original signature:

            aria2.getGlobalOption([secret])

        Returns:
            The global options. The response is a struct. Its keys are the names of options.
            Values are strings.
        """
        return self.call(self.GET_GLOBAL_OPTION)  # type: ignore

    def change_global_option(self, options: dict) -> str:
        """Change the global options dynamically.

        Original signature:

            aria2.changeGlobalOption([secret], options)

        Parameters:
            options: The following options are available:

                - `bt-max-open-files`
                - `download-result`
                - `keep-unfinished-download-result`
                - `log`
                - `log-level`
                - `max-concurrent-downloads`
                - `max-download-result`
                - `max-overall-download-limit`
                - `max-overall-upload-limit`
                - `optimize-concurrent-downloads`
                - `save-cookies`
                - `save-session`
                - `server-stat-of`

                In addition, options listed in the Input File subsection are available, except for following options:
                `checksum`, `index-out`, `out`, `pause` and `select-file`.

                With the log option, you can dynamically start logging or change log file. To stop logging, specify an
                empty string ("") as the parameter value. Note that log file is always opened in append mode.

        Returns:
            `"OK"` for success.
        """
        return self.call(self.CHANGE_GLOBAL_OPTION, [options])  # type: ignore

    def get_global_stat(self) -> dict:
        """Return global statistics such as the overall download and upload speeds.

        Original signature:

            aria2.getGlobalStat([secret])

        Returns:
            A struct that contains the following keys (values are strings):

            - `downloadSpeed`: Overall download speed (byte/sec).
            - `uploadSpeed`: Overall upload speed(byte/sec).
            - `numActive`: The number of active downloads.
            - `numWaiting`: The number of waiting downloads.
            - `numStopped`: The number of stopped downloads in the current session. This value is capped by the
                [`--max-download-result`][aria2p.options.Options.max_download_result] option.
            - `numStoppedTotal`: The number of stopped downloads in the current session and not capped by the
                [`--max-download-result`][aria2p.options.Options.max_download_result] option.

        Examples:
            **Original JSON-RPC Example**

            >>> import urllib2, json
            >>> from pprint import pprint
            >>> jsonreq = json.dumps({'jsonrpc':'2.0', 'id':'qwer',
            ...                       'method':'aria2.getGlobalStat'})
            >>> c = urllib2.urlopen('http://localhost:6800/jsonrpc', jsonreq)
            >>> pprint(json.loads(c.read()))
            {u'id': u'qwer',
             u'jsonrpc': u'2.0',
             u'result': {u'downloadSpeed': u'21846',
                         u'numActive': u'2',
                         u'numStopped': u'0',
                         u'numWaiting': u'0',
                         u'uploadSpeed': u'0'}}
        """
        return self.call(self.GET_GLOBAL_STAT)  # type: ignore

    def purge_download_result(self) -> str:
        """Purge completed/error/removed downloads from memory.

        Original signature:

            aria2.purgeDownloadResult([secret])

        Returns:
            `"OK"`.
        """
        return self.call(self.PURGE_DOWNLOAD_RESULT)  # type: ignore

    def remove_download_result(self, gid: str) -> str:
        """Remove a completed/error/removed download from memory.

        Original signature:

            aria2.removeDownloadResult([secret], gid)

        Parameters:
            gid: The download result to remove.

        Returns:
            `"OK"` for success.

        Examples:
            **Original JSON-RPC Example**

            The following examples remove the download result of the download GID#0000000000000001.

            >>> import urllib2, json
            >>> from pprint import pprint
            >>> jsonreq = json.dumps({'jsonrpc':'2.0', 'id':'qwer',
            ...                       'method':'aria2.removeDownloadResult',
            ...                       'params':['0000000000000001']})
            >>> c = urllib2.urlopen('http://localhost:6800/jsonrpc', jsonreq)
            >>> pprint(json.loads(c.read()))
            {u'id': u'qwer', u'jsonrpc': u'2.0', u'result': u'OK'}
        """
        return self.call(self.REMOVE_DOWNLOAD_RESULT, [gid])  # type: ignore

    def get_version(self) -> str:
        """Return aria2 version and the list of enabled features.

        Original signature:

            aria2.getVersion([secret])

        Returns:
            A struct that contains the following keys:

            - `version`: Version number of aria2 as a string.
            - `enabledFeatures`: List of enabled features. Each feature is given as a string.

        Examples:
            **Original JSON-RPC Example**

            >>> import urllib2, json
            >>> from pprint import pprint
            >>> jsonreq = json.dumps({'jsonrpc':'2.0', 'id':'qwer',
            ...                       'method':'aria2.getVersion'})
            >>> c = urllib2.urlopen('http://localhost:6800/jsonrpc', jsonreq)
            >>> pprint(json.loads(c.read()))
            {u'id': u'qwer',
             u'jsonrpc': u'2.0',
             u'result': {u'enabledFeatures': [u'Async DNS',
                                              u'BitTorrent',
                                              u'Firefox3 Cookie',
                                              u'GZip',
                                              u'HTTPS',
                                              u'Message Digest',
                                              u'Metalink',
                                              u'XML-RPC'],
                         u'version': u'1.11.0'}}
        """
        return self.call(self.GET_VERSION)  # type: ignore

    def get_session_info(self) -> dict:
        """Return session information.

        Returns:
            A struct that contains the `sessionId` key, which is generated each time aria2 is invoked.

        Original signature:

            aria2.getSessionInfo([secret])

        Examples:
            **Original JSON-RPC Example**

            >>> import urllib2, json
            >>> from pprint import pprint
            >>> jsonreq = json.dumps({'jsonrpc':'2.0', 'id':'qwer',
            ...                       'method':'aria2.getSessionInfo'})
            >>> c = urllib2.urlopen('http://localhost:6800/jsonrpc', jsonreq)
            >>> pprint(json.loads(c.read()))
            {u'id': u'qwer',
             u'jsonrpc': u'2.0',
             u'result': {u'sessionId': u'cd6a3bc6a1de28eb5bfa181e5f6b916d44af31a9'}}
        """
        return self.call(self.GET_SESSION_INFO)  # type: ignore

    def shutdown(self) -> str:
        """Shutdown aria2.

        Original signature:

            aria2.shutdown([secret])

        Returns:
            `"OK"`.
        """
        return self.call(self.SHUTDOWN)  # type: ignore

    def force_shutdown(self) -> str:
        """Force shutdown aria2.

        This method shuts down aria2. This method behaves like [`shutdown()`][aria2p.client.Client.shutdown] without performing any
        actions which take time, such as contacting BitTorrent trackers to unregister downloads first.

        Original signature:

            aria2.forceShutdown([secret])

        Returns:
            `"OK"`.
        """
        return self.call(self.FORCE_SHUTDOWN)  # type: ignore

    def save_session(self) -> str:
        """Save the current session to a file.

        This method saves the current session to a file specified
        by the [`--save-session`][aria2p.options.Options.save_session] option.

        Original signature:

            aria2.saveSession([secret])

        Returns:
            `"OK"` if it succeeds.
        """
        return self.call(self.SAVE_SESSION)  # type: ignore

    # system
    def multicall(self, methods: list[dict]) -> list[CallReturnType]:
        """Call multiple methods in a single request.

        This methods encapsulates multiple method calls in a single request.

        Original signature:

            system.multicall(methods)

        Parameters:
            methods: An array of structs. The structs contain two keys: `methodName` and `params`.
                - `methodName` is the method name to call and
                - `params` is array containing parameters to the method call.

        Returns:
            An array of responses.
            The elements will be either a one-item array containing the return value of the method call or a struct of fault
            element if an encapsulated method call fails.

        Examples:
            **Original JSON-RPC Example**

            In the following examples, we add 2 downloads. The first one is http://example.org/file and the second one is
            file.torrent.

            >>> import urllib2, json, base64
            >>> from pprint import pprint
            >>> jsonreq = json.dumps({'jsonrpc':'2.0', 'id':'qwer',
            ...                       'method':'system.multicall',
            ...                       'params':[[{'methodName':'aria2.addUri',
            ...                                   'params':[['http://example.org']]},
            ...                                  {'methodName':'aria2.addTorrent',
            ...                                   'params':[base64.b64encode(open('file.torrent').read())]}]]})
            >>> c = urllib2.urlopen('http://localhost:6800/jsonrpc', jsonreq)
            >>> pprint(json.loads(c.read()))
            {u'id': u'qwer', u'jsonrpc': u'2.0', u'result': [[u'0000000000000001'], [u'd2703803b52216d1']]}

            JSON-RPC additionally supports Batch requests as described in the JSON-RPC 2.0 Specification:

            >>> jsonreq = json.dumps([{'jsonrpc':'2.0', 'id':'qwer',
            ...                        'method':'aria2.addUri',
            ...                        'params':[['http://example.org']]},
            ...                       {'jsonrpc':'2.0', 'id':'asdf',
            ...                        'method':'aria2.addTorrent',
            ...                        'params':[base64.b64encode(open('file.torrent').read())]}])
            >>> c = urllib2.urlopen('http://localhost:6800/jsonrpc', jsonreq)
            >>> pprint(json.loads(c.read()))
            [{u'id': u'qwer', u'jsonrpc': u'2.0', u'result': u'0000000000000001'},
             {u'id': u'asdf', u'jsonrpc': u'2.0', u'result': u'd2703803b52216d1'}]
        """
        return self.call(self.MULTICALL, [methods])  # type: ignore

    def list_methods(self) -> list[str]:
        """Return the available RPC methods.

        This method returns all the available RPC methods in an array of string. Unlike other methods,
        this method does not require secret token. This is safe because this method just returns the available
        method names.

        Original signature:

            system.listMethods()

        Returns:
            The list of available RPC methods.

        Examples:
            **Original JSON-RPC Example**

            >>> import urllib2, json
            >>> from pprint import pprint
            >>> jsonreq = json.dumps({'jsonrpc':'2.0', 'id':'qwer',
            ...                       'method':'system.listMethods'})
            >>> c = urllib2.urlopen('http://localhost:6800/jsonrpc', jsonreq)
            >>> pprint(json.loads(c.read()))
            {u'id': u'qwer',
             u'jsonrpc': u'2.0',
             u'result': [u'aria2.addUri',
                         u'aria2.addTorrent',
             ...
        """
        return self.call(self.LIST_METHODS)  # type: ignore

    def list_notifications(self) -> list[str]:
        """Return all the available RPC notifications.

        This method returns all the available RPC notifications in an array of string. Unlike other methods,
        this method does not require secret token. This is safe because this method just returns the available
        notifications names.

        Original signature:

            system.listNotifications()

        Returns:
            The list of available RPC notifications.

        Examples:
            **Original JSON-RPC Example**

            >>> import urllib2, json
            >>> from pprint import pprint
            >>> jsonreq = json.dumps({'jsonrpc':'2.0', 'id':'qwer',
            ...                       'method':'system.listNotifications'})
            >>> c = urllib2.urlopen('http://localhost:6800/jsonrpc', jsonreq)
            >>> pprint(json.loads(c.read()))
            {u'id': u'qwer',
             u'jsonrpc': u'2.0',
             u'result': [u'aria2.onDownloadStart',
                         u'aria2.onDownloadPause',
             ...
        """
        return self.call(self.LIST_NOTIFICATIONS)  # type: ignore

    # notifications
    def listen_to_notifications(
        self,
        on_download_start: Callable | None = None,
        on_download_pause: Callable | None = None,
        on_download_stop: Callable | None = None,
        on_download_complete: Callable | None = None,
        on_download_error: Callable | None = None,
        on_bt_download_complete: Callable | None = None,
        timeout: int = 5,
        handle_signals: bool = True,  # noqa: FBT001,FBT002
    ) -> None:
        """Start listening to aria2 notifications via WebSocket.

        This method opens a WebSocket connection to the server and wait for notifications (or events) to be received.
        It accepts callbacks as arguments, which are functions accepting one parameter called "gid", for each type
        of notification.

        Stop listening to notifications with the [`stop_listening`][aria2p.client.Client.stop_listening] method.

        Parameters:
            on_download_start: Callback for the `onDownloadStart` event.
            on_download_pause: Callback for the `onDownloadPause` event.
            on_download_stop: Callback for the `onDownloadStop` event.
            on_download_complete: Callback for the `onDownloadComplete` event.
            on_download_error: Callback for the `onDownloadError` event.
            on_bt_download_complete: Callback for the `onBtDownloadComplete` event.
            timeout: Timeout when waiting for data to be received. Use a small value for faster reactivity
                when stopping to listen. Default is 5 seconds.
            handle_signals: Whether to add signal handlers to gracefully stop the loop on SIGTERM and SIGINT.
        """
        self.listening = True
        ws_server = self.ws_server
        log_prefix = f"Notifications ({ws_server})"

        logger.debug(f"{log_prefix}: opening WebSocket with timeout={timeout}")
        try:
            socket = websocket.create_connection(ws_server, timeout=timeout)
        except (ConnectionRefusedError, ConnectionResetError):
            logger.error(f"{log_prefix}: connection refused. Is the server running?")
            return

        callbacks = {
            NOTIFICATION_START: on_download_start,
            NOTIFICATION_PAUSE: on_download_pause,
            NOTIFICATION_STOP: on_download_stop,
            NOTIFICATION_COMPLETE: on_download_complete,
            NOTIFICATION_ERROR: on_download_error,
            NOTIFICATION_BT_COMPLETE: on_bt_download_complete,
        }

        stopped = SignalHandler(["SIGTERM", "SIGINT"]) if handle_signals else False

        while not stopped:
            logger.debug(f"{log_prefix}: waiting for data over WebSocket")
            try:
                message = socket.recv()
            except websocket.WebSocketConnectionClosedException:
                logger.error(f"{log_prefix}: connection to server was closed. Is the server running?")
                break
            except websocket.WebSocketTimeoutException:
                logger.debug(f"{log_prefix}: reached timeout ({timeout}s)")
            else:
                notification = Notification.get_or_raise(json.loads(message))
                logger.info(
                    f"{log_prefix}: received {notification.type} with gid={notification.gid}",
                )
                callback = callbacks.get(notification.type)
                if callable(callback):
                    logger.debug(f"{log_prefix}: calling {callback} with gid={notification.gid}")
                    callback(notification.gid)
                else:
                    logger.debug(f"{log_prefix}: no callback given for type " + notification.type)

            if not self.listening:
                logger.debug(f"{log_prefix}: stopped listening")
                break

        if stopped:
            logger.debug(f"{log_prefix}: stopped listening after receiving a signal")
            self.listening = False

        logger.debug(f"{log_prefix}: closing WebSocket")
        socket.close()

    def stop_listening(self) -> None:
        """Stop listening to notifications.

        Although this method returns instantly, the actual listening loop can take some time to break out,
        depending on the timeout that was given to [`Client.listen_to_notifications`][aria2p.client.Client.listen_to_notifications].
        """
        self.listening = False


class Notification:
    """A helper class for notifications.

    You should not need to use this class. It simply provides methods to instantiate a notification with a
    message received from the server through a WebSocket, or to raise a ClientException if the message is invalid.
    """

    def __init__(self, event_type: str, gid: str) -> None:
        """Initialize the object.

        Parameters:
            event_type: The notification type. Possible types are available in the NOTIFICATION_TYPES variable.
            gid: The GID of the download related to the notification.
        """
        self.type = event_type
        self.gid = gid

    @staticmethod
    def get_or_raise(message: dict) -> Notification:
        """Raise a ClientException when the message is invalid or return a Notification instance.

        Parameters:
            message: The JSON-loaded message received over WebSocket.

        Returns:
            A Notification instance if the message is valid.

        Raises:
            ClientException: When the message contains an error.
        """
        if "error" in message:
            raise Client.response_as_exception(message)
        return Notification.from_message(message)

    @staticmethod
    def from_message(message: dict) -> Notification:
        """Return an instance of Notification.

        This method expects a valid message (not containing errors).

        Parameters:
            message: A valid message received over WebSocket.

        Returns:
            A Notification instance.
        """
        return Notification(event_type=message["method"], gid=message["params"][0]["gid"])
