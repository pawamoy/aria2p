import json
import requests


DEFAULT_MSG_ID = -1


class JSONRPCError(Exception):
    def __init__(self, code, message):
        self.code = code
        self.message = message


class JSONRPCClient:
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

    METHODS = [
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

    def __init__(self, host="http://localhost", port=6800, secret=None):
        host = host.rstrip("/")

        self.host = host
        self.port = port
        self.secret = secret

    def __str__(self):
        return self.server

    @property
    def server(self):
        return f"{self.host}:{self.port}/jsonrpc"

    # utils
    def call(self, method, params=None, msg_id=None, insert_secret=True):
        params = self.get_params(*(params or []))

        if insert_secret and self.secret:
            if method.startswith("aria2."):
                params.insert(0, self.secret)
            elif method == self.MULTICALL:
                for param in params[0]:
                    param["params"].insert(0, self.secret)

        return self.post(self.get_payload(method, params, msg_id=msg_id))

    def batch_call(self, calls, insert_secret=True):
        payloads = []

        for method, params, msg_id in calls:
            params = self.get_params(*params)
            if insert_secret and self.secret and method.startswith("aria2."):
                params.insert(0, self.secret)
            payloads.append(self.get_payload(method, params, msg_id, as_json=False))

        payload = json.dumps(payloads)

        return self.post(payload)

    def multicall2(self, calls, insert_secret=True):
        multicall_params = []

        for method, params in calls:
            params = self.get_params(*params)
            if insert_secret and self.secret and method.startswith("aria2."):
                params.insert(0, self.secret)
            multicall_params.append({"methodName": method, "params": params})

        payload = self.get_payload(self.MULTICALL, multicall_params)

        return self.post(payload)

    def post(self, payload):
        response = requests.post(self.server, data=payload).json()
        if "result" in response:
            return response["result"]
        raise JSONRPCError(response["code"], response["message"])

    @staticmethod
    def get_payload(method, params=None, msg_id=None, as_json=True):
        payload = {"jsonrpc": "2.0", "method": method}

        if msg_id is not None:
            payload["id"] = msg_id
        else:
            payload["id"] = DEFAULT_MSG_ID

        if params:
            payload["params"] = params

        return json.dumps(payload) if as_json else payload

    @staticmethod
    def get_params(*args):
        return [p for p in args if p is not None]

    # aria2
    def add_uri(self, uris, options=None, position=None):
        """
        aria2.addUri([secret], uris[, options[, position]])

        This method adds a new download. uris is an array of HTTP/FTP/SFTP/BitTorrent URIs (strings) pointing to
        the same resource. If you mix URIs pointing to different resources, then the download may fail or be
        corrupted without aria2 complaining. When adding BitTorrent Magnet URIs, uris must have only one element
        and it should be BitTorrent Magnet URI. options is a struct and its members are pairs of option name and
        value. See Options below for more details. If position is given, it must be an integer starting from 0. The
        new download will be inserted at position in the waiting queue. If position is omitted or position
        is larger than the current size of the queue, the new download is appended to the end of the queue. This
        method returns the GID of the newly registered download.

        JSON-RPC Example

        The following example adds http://example.org/file:

            >>> import urllib2, json
            >>> jsonreq = json.dumps({'jsonrpc':'2.0', 'id':'qwer',
            ...                       'method':'aria2.addUri',
            ...                       'params':[['http://example.org/file']]})
            >>> c = urllib2.urlopen('http://localhost:6800/jsonrpc', jsonreq)
            >>> c.read()
            '{"id":"qwer","jsonrpc":"2.0","result":"2089b05ecca3d829"}'

        XML-RPC Example

        The following example adds http://example.org/file:

            >>> import xmlrpclib
            >>> s = xmlrpclib.ServerProxy('http://localhost:6800/rpc')
            >>> s.aria2.addUri(['http://example.org/file'])
            '2089b05ecca3d829'

        The following example adds a new download with two sources and some options:

            >>> s.aria2.addUri(['http://example.org/file', 'http://mirror/file'], dict(dir="/tmp"))
            'd2703803b52216d1'

        The following example adds a download and inserts it to the front of the queue:

            >>> s.aria2.addUri(['http://example.org/file'], {}, 0)
            'ca3d829cee549a4d'
        """
        return self.call(self.ADD_URI, params=[uris, options, position])

    def add_torrent(self, torrent, uris, options=None, position=None):
        """
        aria2.addTorrent([secret], torrent[, uris[, options[, position]]])

        This method adds a BitTorrent download by uploading a ".torrent" file. If you want to add a BitTorrent
        Magnet URI, use the aria2.addUri()  method instead. torrent must be a base64-encoded string containing
        the contents of the ".torrent" file. uris is an array of URIs (string). uris is used for Web-seeding. For
        single file torrents, the URI can be a complete URI pointing to the resource; if URI ends with /,
        name in torrent file is added. For multi-file torrents, name and path in torrent are added to form a URI
        for each file. options is a struct and its members are pairs of option name and value. See Options below
        for more details. If position is given, it must be an integer starting from 0. The new download will be
        inserted at position in the waiting queue. If position is omitted or position is larger than the current
        size of the queue, the new download is appended to the end of the queue. This method returns the GID of the
        newly registered download. If --rpc-save-upload-metadata is true, the uploaded data is saved as a file
        named as the hex string of SHA-1 hash of data plus ".torrent"  in the directory specified by
        --dir option. E.g. a file name might be 0a3893293e27ac0490424c06de4d09242215f0a6.torrent. If a file with
        the same name already exists, it is overwritten!  If the file cannot be saved successfully or
        --rpc-save-upload-metadata is false, the downloads added by this method are not saved by --save-session.

        The following examples add local file file.torrent.

        JSON-RPC Example

            >>> import urllib2, json, base64
            >>> torrent = base64.b64encode(open('file.torrent').read())
            >>> jsonreq = json.dumps({'jsonrpc':'2.0', 'id':'asdf',
            ...                       'method':'aria2.addTorrent', 'params':[torrent]})
            >>> c = urllib2.urlopen('http://localhost:6800/jsonrpc', jsonreq)
            >>> c.read()
            '{"id":"asdf","jsonrpc":"2.0","result":"2089b05ecca3d829"}'

        XML-RPC Example

            >>> import xmlrpclib
            >>> s = xmlrpclib.ServerProxy('http://localhost:6800/rpc')
            >>> s.aria2.addTorrent(xmlrpclib.Binary(open('file.torrent', mode='rb').read()))
            '2089b05ecca3d829'
        """
        return self.call(self.ADD_TORRENT, [torrent, uris, options, position])

    def add_metalink(self, metalink, options=None, position=None):
        """
        aria2.addMetalink([secret], metalink[, options[, position]])

        This method adds a Metalink download by uploading a ".metalink" file. metalink is a base64-encoded string
        which contains the contents of the ".metalink" file. options is a struct and its members are pairs of
        option name and value. See Options below for more details. If position is given, it must be an
        integer starting from 0. The new download will be inserted at position in the waiting queue. If position is
        omitted or position is larger than the current size of the queue, the new download is appended to the end of
        the queue. This method returns an array of GIDs of newly registered downloads. If
        --rpc-save-upload-metadata is true, the uploaded data is saved as a file named hex string of SHA-1 hash of
        data plus ".metalink" in the directory specified by --dir option. E.g. a file name might be
        0a3893293e27ac0490424c06de4d09242215f0a6.metalink. If a file with the same name already exists,
        it is overwritten!  If the file cannot be saved successfully or --rpc-save-upload-metadata is false,
        the downloads added by this method are not saved by --save-session.

        The following examples add local file file.meta4.

        JSON-RPC Example

            >>> import urllib2, json, base64
            >>> metalink = base64.b64encode(open('file.meta4').read())
            >>> jsonreq = json.dumps({'jsonrpc':'2.0', 'id':'qwer',
            ...                       'method':'aria2.addMetalink',
            ...                       'params':[metalink]})
            >>> c = urllib2.urlopen('http://localhost:6800/jsonrpc', jsonreq)
            >>> c.read()
            '{"id":"qwer","jsonrpc":"2.0","result":["2089b05ecca3d829"]}'

        XML-RPC Example

            >>> import xmlrpclib
            >>> s = xmlrpclib.ServerProxy('http://localhost:6800/rpc')
            >>> s.aria2.addMetalink(xmlrpclib.Binary(open('file.meta4', mode='rb').read()))
            ['2089b05ecca3d829']
        """
        return self.call(self.ADD_METALINK, [metalink, options, position])

    def remove(self, gid):
        """
        aria2.remove([secret], gid)

        This method removes the download denoted by gid (string). If the specified download is in progress,
        it is first stopped. The status of the removed download becomes removed. This method returns GID of
        removed download.

        The following examples remove a download with GID#2089b05ecca3d829.

        JSON-RPC Example

            >>> import urllib2, json
            >>> jsonreq = json.dumps({'jsonrpc':'2.0', 'id':'qwer',
            ...                       'method':'aria2.remove',
            ...                       'params':['2089b05ecca3d829']})
            >>> c = urllib2.urlopen('http://localhost:6800/jsonrpc', jsonreq)
            >>> c.read()
            '{"id":"qwer","jsonrpc":"2.0","result":"2089b05ecca3d829"}'

        XML-RPC Example

            >>> import xmlrpclib
            >>> s = xmlrpclib.ServerProxy('http://localhost:6800/rpc')
            >>> s.aria2.remove('2089b05ecca3d829')
            '2089b05ecca3d829'
        """
        return self.call(self.REMOVE, [gid])

    def force_remove(self, gid):
        """
        aria2.forceRemove([secret], gid)

        This method removes the download denoted by gid. This method behaves just like aria2.remove() except
        that this method removes the download without performing any actions which take time, such as contacting
        BitTorrent trackers to unregister the download first.
        """
        return self.call(self.FORCE_REMOVE, [gid])

    def pause(self, gid):
        """
        aria2.pause([secret], gid)

        This method pauses the download denoted by gid (string). The status of paused download becomes paused. If
        the download was active, the download is placed in the front of waiting queue. While the status is
        paused, the download is not started. To change status to waiting, use the aria2.unpause() method. This
        method returns GID of paused download.
        """
        return self.call(self.PAUSE, [gid])

    def pause_all(self):
        """
        aria2.pauseAll([secret])

        This method is equal to calling aria2.pause() for every active/waiting download. This methods returns OK.
        """
        return self.call(self.PAUSE_ALL)

    def force_pause(self, gid):
        """
        aria2.forcePause([secret], gid)

        This method pauses the download denoted by gid. This method behaves just like aria2.pause() except that this
        method pauses downloads without performing any actions which take time, such as contacting BitTorrent
        trackers to unregister the download first.
        """
        return self.call(self.FORCE_PAUSE, [gid])

    def force_pause_all(self):
        """
        aria2.forcePauseAll([secret])

        This method is equal to calling aria2.forcePause() for every active/waiting download. This methods returns OK.
        """
        return self.call(self.FORCE_PAUSE_ALL)

    def unpause(self, gid):
        """
        aria2.unpause([secret], gid)

        This method changes the status of the download denoted by gid (string) from paused to waiting,
        making the download eligible to be restarted. This method returns the GID of the unpaused download.
        """
        return self.call(self.UNPAUSE, [gid])

    def unpause_all(self):
        """
        aria2.unpauseAll([secret])

        This method is equal to calling aria2.unpause() for every active/waiting download. This methods returns OK.
        """
        return self.call(self.UNPAUSE_ALL)

    def tell_status(self, gid, keys=None):
        """
        aria2.tellStatus([secret], gid[, keys])

        This method returns the progress of the download denoted by gid (string). keys is an array of strings. If
        specified, the response contains only keys in the keys array. If keys is empty or omitted, the response
        contains all keys. This is useful when you just want specific keys and avoid unnecessary transfers. For
        example, aria2.tellStatus("2089b05ecca3d829", ["gid", "status"]) returns the gid and status keys only. The
        response is a struct and contains following keys. Values are strings.

        gid    GID of the download.

        status
            active for currently downloading/seeding downloads. waiting for downloads in the queue; download is
            not started. paused for paused downloads. error for downloads that were stopped because of error.
            complete for stopped and completed downloads. removed for the downloads removed by user.

        totalLength
               Total length of the download in bytes.

        completedLength
               Completed length of the download in bytes.

        uploadLength
               Uploaded length of the download in bytes.

        bitfield
               Hexadecimal representation of the download progress. The highest bit corresponds to the piece at
               index 0. Any set bits indicate loaded pieces, while unset bits indicate not yet loaded and/or missing
               pieces. Any overflow bits at the end are set to zero. When the download was not started yet, this key
               will not be included in the response.

        downloadSpeed
               Download speed of this download measured in bytes/sec.

        uploadSpeed
               Upload speed of this download measured in bytes/sec.

        infoHash
               InfoHash. BitTorrent only.

        numSeeders
               The number of seeders aria2 has connected to. BitTorrent only.

        seeder true if the local endpoint is a seeder. Otherwise false. BitTorrent only.

        pieceLength
               Piece length in bytes.

        numPieces
               The number of pieces.

        connections
               The number of peers/servers aria2 has connected to.

        errorCode
               The code of the last error for this item, if any. The value is a string. The error codes are defined
               in the EXIT STATUS section. This value is only available for stopped/completed downloads.

        errorMessage
               The (hopefully) human readable error message associated to errorCode.

        followedBy
               List of GIDs which are generated as the result of this download. For example, when aria2 downloads a
               Metalink file, it generates downloads described in the Metalink (see the --follow-metalink
               option). This value is useful to track auto-generated downloads. If there are no such downloads,
               this key will not be included in the response.

        following
               The reverse link for followedBy. A download included in followedBy has this object's GID in its
               following value.

        belongsTo
               GID of a parent download. Some downloads are a part of another download. For example, if a file in a
               Metalink has BitTorrent resources, the downloads of ".torrent" files are parts of that parent. If
               this download has no parent, this key will not be included in the response.

        dir    Directory to save files.

        files Return the list of files. The elements of this list are the same structs used in aria2.getFiles() method.

        bittorrent
               Struct which contains information retrieved from the .torrent (file). BitTorrent only.
               It contains following keys.

               announceList
                      List of lists of announce URIs. If the torrent contains announce and no announce-list, announce
                      is converted to the announce-list format.

               comment
                      The comment of the torrent. comment.utf-8 is used if available.

               creationDate
                      The creation time of the torrent. The value is an integer since the epoch, measured in seconds.

               mode   File mode of the torrent. The value is either single or multi.

               info   Struct which contains data from Info dictionary. It contains following keys.

                      name   name in info dictionary. name.utf-8 is used if available.

        verifiedLength
               The number of verified number of bytes while the files are being hash checked. This key exists only
               when this download is being hash checked.

        verifyIntegrityPending
               true if this download is waiting for the hash check in a queue.
               This key exists only when this download is in the queue.

        JSON-RPC Example

        The following example gets information about a download with GID#2089b05ecca3d829:

            >>> import urllib2, json
            >>> from pprint import pprint
            >>> jsonreq = json.dumps({'jsonrpc':'2.0', 'id':'qwer',
            ...                       'method':'aria2.tellStatus',
            ...                       'params':['2089b05ecca3d829']})
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
                         u'gid': u'2089b05ecca3d829',
                         u'numPieces': u'34',
                         u'pieceLength': u'1048576',
                         u'status': u'active',
                         u'totalLength': u'34896138',
                         u'uploadLength': u'0',
                         u'uploadSpeed': u'0'}}

        The following example gets only specific keys:

            >>> jsonreq = json.dumps({'jsonrpc':'2.0', 'id':'qwer',
            ...                       'method':'aria2.tellStatus',
            ...                       'params':['2089b05ecca3d829',
            ...                                 ['gid',
            ...                                  'totalLength',
            ...                                  'completedLength']]})
            >>> c = urllib2.urlopen('http://localhost:6800/jsonrpc', jsonreq)
            >>> pprint(json.loads(c.read()))
            {u'id': u'qwer',
             u'jsonrpc': u'2.0',
             u'result': {u'completedLength': u'5701632',
                         u'gid': u'2089b05ecca3d829',
                         u'totalLength': u'34896138'}}

        XML-RPC Example

        The following example gets information about a download with GID#2089b05ecca3d829:

            >>> import xmlrpclib
            >>> from pprint import pprint
            >>> s = xmlrpclib.ServerProxy('http://localhost:6800/rpc')
            >>> r = s.aria2.tellStatus('2089b05ecca3d829')
            >>> pprint(r)
            {'bitfield': 'ffff80',
             'completedLength': '34896138',
             'connections': '0',
             'dir': '/downloads',
             'downloadSpeed': '0',
             'errorCode': '0',
             'files': [{'index': '1',
                        'length': '34896138',
                        'completedLength': '34896138',
                        'path': '/downloads/file',
                        'selected': 'true',
                        'uris': [{'status': 'used',
                                  'uri': 'http://example.org/file'}]}],
             'gid': '2089b05ecca3d829',
             'numPieces': '17',
             'pieceLength': '2097152',
             'status': 'complete',
             'totalLength': '34896138',
             'uploadLength': '0',
             'uploadSpeed': '0'}

        The following example gets only specific keys:

            >>> r = s.aria2.tellStatus('2089b05ecca3d829', ['gid', 'totalLength', 'completedLength'])
            >>> pprint(r)
            {'completedLength': '34896138', 'gid': '2089b05ecca3d829', 'totalLength': '34896138'}
        """
        return self.call(self.TELL_STATUS, [gid, keys])

    def get_uris(self, gid):
        """
        aria2.getUris([secret], gid)

        This method returns the URIs used in the download denoted by gid (string). The response is an array of
        structs and it contains following keys. Values are string.

        uri    URI

        status 'used' if the URI is in use. 'waiting' if the URI is still waiting in the queue.

        JSON-RPC Example

            >>> import urllib2, json
            >>> from pprint import pprint
            >>> jsonreq = json.dumps({'jsonrpc':'2.0', 'id':'qwer',
            ...                       'method':'aria2.getUris',
            ...                       'params':['2089b05ecca3d829']})
            >>> c = urllib2.urlopen('http://localhost:6800/jsonrpc', jsonreq)
            >>> pprint(json.loads(c.read()))
            {u'id': u'qwer',
             u'jsonrpc': u'2.0',
             u'result': [{u'status': u'used',
                          u'uri': u'http://example.org/file'}]}

        XML-RPC Example

            >>> import xmlrpclib
            >>> from pprint import pprint
            >>> s = xmlrpclib.ServerProxy('http://localhost:6800/rpc')
            >>> r = s.aria2.getUris('2089b05ecca3d829')
            >>> pprint(r)
            [{'status': 'used', 'uri': 'http://example.org/file'}]
        """
        return self.call(self.GET_URIS, [gid])

    def get_files(self, gid):
        """
        aria2.getFiles([secret], gid)

        This method returns the file list of the download denoted by gid (string). The response is an array of
        structs which contain following keys. Values are strings.

        index Index of the file, starting at 1, in the same order as files appear in the multi-file torrent.

        path File path.

        length File size in bytes.

        completedLength
               Completed length of this file in bytes. Please note that it is possible that sum of completedLength
               is less than the completedLength returned by the aria2.tellStatus() method. This is because
               completedLength in aria2.getFiles() only includes completed pieces. On the other hand,
               completedLength in aria2.tellStatus() also includes partially completed pieces.

        selected
               true if this file is selected by --select-file option. If --select-file is not specified or this is
               single-file torrent or not a torrent download at all, this value is always true. Otherwise false.

        uris Returns a list of URIs for this file. The element type is the same struct used in the aria2.getUris()
               method.

        JSON-RPC Example

            >>> import urllib2, json
            >>> from pprint import pprint
            >>> jsonreq = json.dumps({'jsonrpc':'2.0', 'id':'qwer',
            ...                       'method':'aria2.getFiles',
            ...                       'params':['2089b05ecca3d829']})
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

        XML-RPC Example

            >>> import xmlrpclib
            >>> from pprint import pprint
            >>> s = xmlrpclib.ServerProxy('http://localhost:6800/rpc')
            >>> r = s.aria2.getFiles('2089b05ecca3d829')
            >>> pprint(r)
            [{'index': '1',
              'length': '34896138',
              'completedLength': '34896138',
              'path': '/downloads/file',
              'selected': 'true',
              'uris': [{'status': 'used',
                        'uri': 'http://example.org/file'}]}]
        """
        return self.call(self.GET_FILES, [gid])

    def get_peers(self, gid):
        """
        aria2.getPeers([secret], gid)

        This method returns a list peers of the download denoted by gid (string). This method is for BitTorrent
        only. The response is an array of structs and contains the following keys. Values are strings.

        peerId Percent-encoded peer ID.

        ip     IP address of the peer.

        port   Port number of the peer.

        bitfield
               Hexadecimal representation of the download progress of the peer. The highest bit corresponds to
               the piece at index 0. Set bits indicate the piece is available and unset bits indicate the piece is
               missing. Any spare bits at the end are set to zero.

        amChoking
               true if aria2 is choking the peer. Otherwise false.

        peerChoking
               true if the peer is choking aria2. Otherwise false.

        downloadSpeed
               Download speed (byte/sec) that this client obtains from the peer.

        uploadSpeed
               Upload speed(byte/sec) that this client uploads to the peer.

        seeder true if this peer is a seeder. Otherwise false.

        JSON-RPC Example

            >>> import urllib2, json
            >>> from pprint import pprint
            >>> jsonreq = json.dumps({'jsonrpc':'2.0', 'id':'qwer',
            ...                       'method':'aria2.getPeers',
            ...                       'params':['2089b05ecca3d829']})
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

        XML-RPC Example

            >>> import xmlrpclib
            >>> from pprint import pprint
            >>> s = xmlrpclib.ServerProxy('http://localhost:6800/rpc')
            >>> r = s.aria2.getPeers('2089b05ecca3d829')
            >>> pprint(r)
            [{'amChoking': 'true',
              'bitfield': 'ffffffffffffffffffffffffffffffffffffffff',
              'downloadSpeed': '10602',
              'ip': '10.0.0.9',
              'peerChoking': 'false',
              'peerId': 'aria2%2F1%2E10%2E5%2D%87%2A%EDz%2F%F7%E6',
              'port': '6881',
              'seeder': 'true',
              'uploadSpeed': '0'},
             {'amChoking': 'false',
              'bitfield': 'ffffeff0fffffffbfffffff9fffffcfff7f4ffff',
              'downloadSpeed': '8654',
              'ip': '10.0.0.30',
              'peerChoking': 'false',
              'peerId': 'bittorrent client758',
              'port': '37842',
              'seeder': 'false,
              'uploadSpeed': '6890'}]
        """
        return self.call(self.GET_PEERS, [gid])

    def get_servers(self, gid):
        """
        aria2.getServers([secret], gid)

        This method returns currently connected HTTP(S)/FTP/SFTP servers of the download denoted by gid (string). The
        response is an array of structs and contains the following keys. Values are strings.

        index Index of the file, starting at 1, in the same order as files appear in the multi-file metalink.

        servers
               A list of structs which contain the following keys.

               uri    Original URI.

               currentUri
                      This is the URI currently used for downloading. If redirection is involved, currentUri and uri
                      may differ.

               downloadSpeed
                      Download speed (byte/sec)

        JSON-RPC Example

            >>> import urllib2, json
            >>> from pprint import pprint
            >>> jsonreq = json.dumps({'jsonrpc':'2.0', 'id':'qwer',
            ...                       'method':'aria2.getServers',
            ...                       'params':['2089b05ecca3d829']})
            >>> c = urllib2.urlopen('http://localhost:6800/jsonrpc', jsonreq)
            >>> pprint(json.loads(c.read()))
            {u'id': u'qwer',
             u'jsonrpc': u'2.0',
             u'result': [{u'index': u'1',
                          u'servers': [{u'currentUri': u'http://example.org/file',
                                        u'downloadSpeed': u'10467',
                                        u'uri': u'http://example.org/file'}]}]}

        XML-RPC Example

            >>> import xmlrpclib
            >>> from pprint import pprint
            >>> s = xmlrpclib.ServerProxy('http://localhost:6800/rpc')
            >>> r = s.aria2.getServers('2089b05ecca3d829')
            >>> pprint(r)
            [{'index': '1',
              'servers': [{'currentUri': 'http://example.org/dl/file',
                           'downloadSpeed': '20285',
                           'uri': 'http://example.org/file'}]}]
        """
        return self.call(self.GET_SERVERS, [gid])

    def tell_active(self, keys=None):
        """
        aria2.tellActive([secret][, keys])

        This method returns a list of active downloads. The response is an array of the same structs as returned
        by the aria2.tellStatus() method. For the keys parameter, please refer to the aria2.tellStatus() method.
        """
        return self.call(self.TELL_ACTIVE, [keys])

    def tell_waiting(self, offset, num, keys=None):
        """
        aria2.tellWaiting([secret], offset, num[, keys])

        This method returns a list of waiting downloads, including paused ones. offset is an integer and specifies
        the offset from the download waiting at the front. num is an integer and specifies the max. number of
        downloads to be returned. For the keys parameter, please refer to the aria2.tellStatus() method.

        If offset is a positive integer, this method returns downloads in the range of [offset, offset + num).

        offset can be a negative integer. offset == -1 points last download in the waiting queue and offset == -2
        points the download before the last download, and so on. Downloads in the response are in reversed order then.

        For example, imagine three downloads "A","B" and "C" are waiting in this order. aria2.tellWaiting(0,
        1) returns ["A"]. aria2.tellWaiting(1, 2) returns ["B", "C"]. aria2.tellWaiting(-1, 2) returns ["C", "B"].

        The response is an array of the same structs as returned by aria2.tellStatus() method.
        """
        return self.call(self.TELL_WAITING, [offset, num, keys])

    def tell_stopped(self, offset, num, keys=None):
        """
        aria2.tellStopped([secret], offset, num[, keys])

        This method returns a list of stopped downloads. offset is an integer and specifies the offset from the
        least recently stopped download. num is an integer and specifies the max. number of downloads to be
        returned. For the keys parameter, please refer to the aria2.tellStatus() method.

        offset and num have the same semantics as described in the aria2.tellWaiting() method.

        The response is an array of the same structs as returned by the aria2.tellStatus() method.
        """
        return self.call(self.TELL_STOPPED, [offset, num, keys])

    def change_position(self, gid, pos, how):
        """
        aria2.changePosition([secret], gid, pos, how)

        This method changes the position of the download denoted by gid in the queue. pos is an integer. how is
        a string. If how is POS_SET, it moves the download to a position relative to the beginning of the queue. If
        how is POS_CUR, it moves the download to a position relative to the current position. If how is POS_END,
        it moves the download to a position relative to the end of the queue. If the destination position is less
        than 0 or beyond the end of the queue, it moves the download to the beginning or the end of the queue
        respectively. The response is an integer denoting the resulting position.

        For example, if GID#2089b05ecca3d829 is currently in position 3, aria2.changePosition('2089b05ecca3d829', -1,
        'POS_CUR') will change its position to 2. Additionally aria2.changePosition('2089b05ecca3d829', 0,
        'POS_SET') will change its position to 0 (the beginning of the queue).

        The following examples move the download GID#2089b05ecca3d829 to the front of the queue.

        JSON-RPC Example

            >>> import urllib2, json
            >>> from pprint import pprint
            >>> jsonreq = json.dumps({'jsonrpc':'2.0', 'id':'qwer',
            ...                       'method':'aria2.changePosition',
            ...                       'params':['2089b05ecca3d829', 0, 'POS_SET']})
            >>> c = urllib2.urlopen('http://localhost:6800/jsonrpc', jsonreq)
            >>> pprint(json.loads(c.read()))
            {u'id': u'qwer', u'jsonrpc': u'2.0', u'result': 0}

        XML-RPC Example

            >>> import xmlrpclib
            >>> s = xmlrpclib.ServerProxy('http://localhost:6800/rpc')
            >>> s.aria2.changePosition('2089b05ecca3d829', 0, 'POS_SET')
            0
        """
        return self.call(self.CHANGE_POSITION, [gid, pos, how])

    def change_uri(self, gid, file_index, del_uris, add_uris, position=None):
        """
        aria2.changeUri([secret], gid, fileIndex, delUris, addUris[, position])

        This method removes the URIs in delUris from and appends the URIs in addUris to download denoted by gid.
        delUris and addUris are lists of strings. A download can contain multiple files and URIs are attached to
        each file. fileIndex is used to select which file to remove/attach given URIs. fileIndex is 1-based.
        position is used to specify where URIs are inserted in the existing waiting URI list. position is 0-based.
        When position is omitted, URIs are appended to the back of the list. This method first executes the
        removal and then the addition. position is the position after URIs are removed, not the position when this
        method is called. When removing an URI, if the same URIs exist in download, only one of them is removed for
        each URI in delUris. In other words, if there are three URIs http://example.org/aria2 and you want
        remove them all, you have to specify (at least) 3 http://example.org/aria2 in delUris. This method
        returns a list which contains two integers. The first integer is the number of URIs deleted. The second
        integer is the number of URIs added.

        The following examples add the URI http://example.org/file to the file whose index is 1 and belongs to the
        download GID#2089b05ecca3d829.

        JSON-RPC Example

            >>> import urllib2, json
            >>> from pprint import pprint
            >>> jsonreq = json.dumps({'jsonrpc':'2.0', 'id':'qwer',
            ...                       'method':'aria2.changeUri',
            ...                       'params':['2089b05ecca3d829', 1, [],
                                               ['http://example.org/file']]})
            >>> c = urllib2.urlopen('http://localhost:6800/jsonrpc', jsonreq)
            >>> pprint(json.loads(c.read()))
            {u'id': u'qwer', u'jsonrpc': u'2.0', u'result': [0, 1]}

        XML-RPC Example

            >>> import xmlrpclib
            >>> s = xmlrpclib.ServerProxy('http://localhost:6800/rpc')
            >>> s.aria2.changeUri('2089b05ecca3d829', 1, [], ['http://example.org/file'])
            [0, 1]
        """
        return self.call(self.CHANGE_URI, [gid, file_index, del_uris, add_uris, position])

    def get_option(self, gid):
        """
        aria2.getOption([secret], gid)

        This method returns options of the download denoted by gid. The response is a struct where keys are the
        names of options. The values are strings. Note that this method does not return options which have no
        default value and have not been set on the command-line, in configuration files or RPC methods.

        The following examples get options of the download GID#2089b05ecca3d829.

        JSON-RPC Example

            >>> import urllib2, json
            >>> from pprint import pprint
            >>> jsonreq = json.dumps({'jsonrpc':'2.0', 'id':'qwer',
            ...                       'method':'aria2.getOption',
            ...                       'params':['2089b05ecca3d829']})
            >>> c = urllib2.urlopen('http://localhost:6800/jsonrpc', jsonreq)
            >>> pprint(json.loads(c.read()))
            {u'id': u'qwer',
             u'jsonrpc': u'2.0',
             u'result': {u'allow-overwrite': u'false',
                         u'allow-piece-length-change': u'false',
                         u'always-resume': u'true',
                         u'async-dns': u'true',
             ...

        XML-RPC Example

            >>> import xmlrpclib
            >>> from pprint import pprint
            >>> s = xmlrpclib.ServerProxy('http://localhost:6800/rpc')
            >>> r = s.aria2.getOption('2089b05ecca3d829')
            >>> pprint(r)
            {'allow-overwrite': 'false',
             'allow-piece-length-change': 'false',
             'always-resume': 'true',
             'async-dns': 'true',
             ....
        """
        return self.call(self.GET_OPTION, [gid])

    def change_option(self, gid, options):
        """
        aria2.changeOption([secret], gid, options)

        This method changes options of the download denoted by gid (string) dynamically. options is a struct. The
        options listed in Input File subsection are available, except for following options:

        · dry-run

        · metalink-base-uri

        · parameterized-uri

        · pause

        · piece-length

        · rpc-save-upload-metadata

        Except for the following options, changing the other options of active download makes it restart (restart
        itself is managed by aria2, and no user intervention is required):

        · bt-max-peers

        · bt-request-peer-speed-limit

        · bt-remove-unselected-file

        · force-save

        · max-download-limit

        · max-upload-limit

        This method returns OK for success.

        The following examples set the max-download-limit option to 20K for the download GID#2089b05ecca3d829.

        JSON-RPC Example

            >>> import urllib2, json
            >>> from pprint import pprint
            >>> jsonreq = json.dumps({'jsonrpc':'2.0', 'id':'qwer',
            ...                       'method':'aria2.changeOption',
            ...                       'params':['2089b05ecca3d829',
            ...                                 {'max-download-limit':'10K'}]})
            >>> c = urllib2.urlopen('http://localhost:6800/jsonrpc', jsonreq)
            >>> pprint(json.loads(c.read()))
            {u'id': u'qwer', u'jsonrpc': u'2.0', u'result': u'OK'}

        XML-RPC Example

            >>> import xmlrpclib
            >>> s = xmlrpclib.ServerProxy('http://localhost:6800/rpc')
            >>> s.aria2.changeOption('2089b05ecca3d829', {'max-download-limit':'20K'})
            'OK'
        """
        return self.call(self.CHANGE_OPTION, [gid, options])

    def get_global_option(self):
        """
        aria2.getGlobalOption([secret])

        This method returns the global options. The response is a struct. Its keys are the names of options.
        Values are strings. Note that this method does not return options which have no default value and have not
        been set on the command-line, in configuration files or RPC methods. Because global options are used as a
        template for the options of newly added downloads, the response contains keys returned by the
        aria2.getOption() method.
        """
        return self.call(self.GET_GLOBAL_OPTION)

    def change_global_option(self, options):
        """
        aria2.changeGlobalOption([secret], options)

        This method changes global options dynamically. options is a struct. The following options are available:

        · bt-max-open-files

        · download-result

        · keep-unfinished-download-result

        · log

        · log-level

        · max-concurrent-downloads

        · max-download-result

        · max-overall-download-limit

        · max-overall-upload-limit

        · optimize-concurrent-downloads

        · save-cookies

        · save-session

        · server-stat-of

        In addition, options listed in the Input File subsection are available, except for following options:
        checksum, index-out, out, pause and select-file.

        With the log option, you can dynamically start logging or change log file. To stop logging, specify an
        empty string("") as the parameter value. Note that log file is always opened in append mode. This method
        returns OK for success.
        """
        return self.call(self.CHANGE_GLOBAL_OPTION, [options])

    def get_global_stat(self):
        """
        aria2.getGlobalStat([secret])

        This method returns global statistics such as the overall download and upload speeds. The response is a
        struct and contains the following keys. Values are strings.

        downloadSpeed
               Overall download speed (byte/sec).

        uploadSpeed
               Overall upload speed(byte/sec).

        numActive
               The number of active downloads.

        numWaiting
               The number of waiting downloads.

        numStopped
               The number of stopped downloads in the current session. This value is capped by the
               --max-download-result option.

        numStoppedTotal
                The number of stopped downloads in the current session and not capped by the
                --max-download-result option.

        JSON-RPC Example

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

        XML-RPC Example

            >>> import xmlrpclib
            >>> from pprint import pprint
            >>> s = xmlrpclib.ServerProxy('http://localhost:6800/rpc')
            >>> r = s.aria2.getGlobalStat()
            >>> pprint(r)
            {'downloadSpeed': '23136',
             'numActive': '2',
             'numStopped': '0',
             'numWaiting': '0',
             'uploadSpeed': '0'}
        """
        return self.call(self.GET_GLOBAL_STAT)

    def purge_download_result(self):
        """
        aria2.purgeDownloadResult([secret])

        This method purges completed/error/removed downloads to free memory. This method returns OK.
        """
        return self.call(self.PURGE_DOWNLOAD_RESULT)

    def remove_download_result(self, gid):
        """
        aria2.removeDownloadResult([secret], gid)

        This method removes a completed/error/removed download denoted by gid from memory. This method returns OK for
        success.

        The following examples remove the download result of the download GID#2089b05ecca3d829.

        JSON-RPC Example

            >>> import urllib2, json
            >>> from pprint import pprint
            >>> jsonreq = json.dumps({'jsonrpc':'2.0', 'id':'qwer',
            ...                       'method':'aria2.removeDownloadResult',
            ...                       'params':['2089b05ecca3d829']})
            >>> c = urllib2.urlopen('http://localhost:6800/jsonrpc', jsonreq)
            >>> pprint(json.loads(c.read()))
            {u'id': u'qwer', u'jsonrpc': u'2.0', u'result': u'OK'}

        XML-RPC Example

            >>> import xmlrpclib
            >>> s = xmlrpclib.ServerProxy('http://localhost:6800/rpc')
            >>> s.aria2.removeDownloadResult('2089b05ecca3d829')
            'OK'
        """
        return self.call(self.REMOVE_DOWNLOAD_RESULT, [gid])

    def get_version(self):
        """
        aria2.getVersion([secret])

        This method returns the version of aria2 and the list of enabled features. The response is a struct and
        contains following keys.

        version
               Version number of aria2 as a string.

        enabledFeatures
               List of enabled features. Each feature is given as a string.

        JSON-RPC Example

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

        XML-RPC Example

            >>> import xmlrpclib
            >>> from pprint import pprint
            >>> s = xmlrpclib.ServerProxy('http://localhost:6800/rpc')
            >>> r = s.aria2.getVersion()
            >>> pprint(r)
            {'enabledFeatures': ['Async DNS',
                                 'BitTorrent',
                                 'Firefox3 Cookie',
                                 'GZip',
                                 'HTTPS',
                                 'Message Digest',
                                 'Metalink',
                                 'XML-RPC'],
             'version': '1.11.0'}
        """
        return self.call(self.GET_VERSION)

    def get_session_info(self):
        """
        aria2.getSessionInfo([secret])

        This method returns session information. The response is a struct and contains following key.

        sessionId
               Session ID, which is generated each time when aria2 is invoked.

        JSON-RPC Example

            >>> import urllib2, json
            >>> from pprint import pprint
            >>> jsonreq = json.dumps({'jsonrpc':'2.0', 'id':'qwer',
            ...                       'method':'aria2.getSessionInfo'})
            >>> c = urllib2.urlopen('http://localhost:6800/jsonrpc', jsonreq)
            >>> pprint(json.loads(c.read()))
            {u'id': u'qwer',
             u'jsonrpc': u'2.0',
             u'result': {u'sessionId': u'cd6a3bc6a1de28eb5bfa181e5f6b916d44af31a9'}}

        XML-RPC Example

            >>> import xmlrpclib
            >>> s = xmlrpclib.ServerProxy('http://localhost:6800/rpc')
            >>> s.aria2.getSessionInfo()
            {'sessionId': 'cd6a3bc6a1de28eb5bfa181e5f6b916d44af31a9'}
        """
        return self.call(self.GET_SESSION_INFO)

    def shutdown(self):
        """
        aria2.shutdown([secret])

        This method shuts down aria2. This method returns OK.
        """
        return self.call(self.SHUTDOWN)

    def force_shutdown(self):
        """
        aria2.forceShutdown([secret])

        This method shuts down aria2(). This method behaves like :func:'aria2.shutdown` without performing any
        actions which take time, such as contacting BitTorrent trackers to unregister downloads first. This method
        returns OK.
        """
        return self.call(self.FORCE_SHUTDOWN)

    def save_session(self):
        """
        aria2.saveSession([secret])

        This method saves the current session to a file specified by the --save-session option. This method returns
        OK if it succeeds.
        """
        return self.call(self.SAVE_SESSION)

    # system
    def multicall(self, methods):
        """
        system.multicall(methods)

        This methods encapsulates multiple method calls in a single request. methods is an array of structs. The
        structs contain two keys:  methodName and params. methodName is the method name to call and
        params is array containing parameters to the method call. This method returns an array of responses. The
        elements will be either a one-item array containing the return value of the method call or a struct of fault
        element if an encapsulated method call fails.

        In the following examples, we add 2 downloads. The first one is http://example.org/file and the second one is
        file.torrent.

        JSON-RPC Example

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
            {u'id': u'qwer', u'jsonrpc': u'2.0', u'result': [[u'2089b05ecca3d829'], [u'd2703803b52216d1']]}

        JSON-RPC additionally supports Batch requests as described in the JSON-RPC 2.0 Specification:

            >>> jsonreq = json.dumps([{'jsonrpc':'2.0', 'id':'qwer',
            ...                        'method':'aria2.addUri',
            ...                        'params':[['http://example.org']]},
            ...                       {'jsonrpc':'2.0', 'id':'asdf',
            ...                        'method':'aria2.addTorrent',
            ...                        'params':[base64.b64encode(open('file.torrent').read())]}])
            >>> c = urllib2.urlopen('http://localhost:6800/jsonrpc', jsonreq)
            >>> pprint(json.loads(c.read()))
            [{u'id': u'qwer', u'jsonrpc': u'2.0', u'result': u'2089b05ecca3d829'},
             {u'id': u'asdf', u'jsonrpc': u'2.0', u'result': u'd2703803b52216d1'}]

        XML-RPC Example

            >>> import xmlrpclib
            >>> s = xmlrpclib.ServerProxy('http://localhost:6800/rpc')
            >>> mc = xmlrpclib.MultiCall(s)
            >>> mc.aria2.addUri(['http://example.org/file'])
            >>> mc.aria2.addTorrent(xmlrpclib.Binary(open('file.torrent', mode='rb').read()))
            >>> r = mc()
            >>> tuple(r)
            ('2089b05ecca3d829', 'd2703803b52216d1')
        """
        return self.call(self.MULTICALL, [methods])

    def list_methods(self):
        """
        system.listMethods()

        This method returns all the available RPC methods in an array of string. Unlike other methods,
        this method does not require secret token. This is safe because this method just returns the available
        method names.

        JSON-RPC Example

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

        XML-RPC Example

            >>> import xmlrpclib
            >>> s = xmlrpclib.ServerProxy('http://localhost:6800/rpc')
            >>> s.system.listMethods()
            ['aria2.addUri', 'aria2.addTorrent', ...
        """
        return self.call(self.LIST_METHODS)

    def list_notifications(self):
        """
        system.listNotifications()

        This method returns all the available RPC notifications in an array of string. Unlike other methods,
        this method does not require secret token. This is safe because this method just returns the available
        notifications names.

        JSON-RPC Example

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

        XML-RPC Example

            >>> import xmlrpclib
            >>> s = xmlrpclib.ServerProxy('http://localhost:6800/rpc')
            >>> s.system.listNotifications()
            ['aria2.onDownloadStart', 'aria2.onDownloadPause', ...
        """
        return self.call(self.LIST_NOTIFICATIONS)
