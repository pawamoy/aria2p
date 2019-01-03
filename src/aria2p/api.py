"""
This module defines the API class, which makes use of a JSON-RPC client to provide higher-level methods to
interact easily with a remote aria2c process.
"""
from base64 import b64encode

from .downloads import Download
from .options import Options
from .stats import Stats


class API:
    """
    A class providing high-level methods to interact with a remote aria2c process.

    This class is instantiated with a reference to a :class:`client.JSONRPCClient` instance. It then uses this client
    to call remote procedures, or remote methods. The client methods reflect exactly what aria2c is providing
    through JSON-RPC, while this class's methods allow for easier / faster control of the remote process. It also
    wraps the information the client retrieves in Python object, like  :class:`downloads.Download`, allowing for
    even more Pythonic interactions, without worrying about payloads, responses, JSON, etc..
    """

    def __init__(self, json_rpc_client):
        self.client = json_rpc_client

    def add_magnet(self, magnet_uri, options=None, position=None):
        if options is None:
            options = {}

        if isinstance(options, Options):
            client_options = options.get_struct()
        else:
            client_options = options

        gid = self.client.add_uri([magnet_uri], client_options, position)

        return self.get_download(gid)

    def add_torrent(self, torrent_file_path, uris=None, options=None, position=None):
        if uris is None:
            uris = []

        if options is None:
            options = {}

        if isinstance(options, Options):
            client_options = options.get_struct()
        else:
            client_options = options

        with open(torrent_file_path, "rb") as stream:
            torrent_contents = stream.read()
        encoded_contents = b64encode(torrent_contents).decode("utf8")

        gid = self.client.add_torrent(encoded_contents, uris, client_options, position)

        return self.get_download(gid)

    def add_metalink(self, metalink_file_path, options=None, position=None):
        if options is None:
            options = {}

        if isinstance(options, Options):
            client_options = options.get_struct()
        else:
            client_options = options

        with open(metalink_file_path) as stream:
            metalink_contents = stream.read()
        encoded_contents = b64encode(metalink_contents)

        gids = self.client.add_metalink(encoded_contents, client_options, position)

        return self.get_downloads(gids)

    def add_url(self, urls, options=None, position=None):
        if options is None:
            options = {}

        if isinstance(options, Options):
            client_options = options.get_struct()
        else:
            client_options = options

        gid = self.client.add_uri(urls, client_options, position)

        return self.get_download(gid)

    def search(self, patterns):
        """
        gid
        status
        totalLength
        completedLength
        uploadLength
        bitfield
        downloadSpeed
        uploadSpeed
        infoHash
        numSeeders
        seeder
        pieceLength
        numPieces
        connections
        errorCode
        errorMessage
        followedBy
        following
        belongsTo
        dir
        files
        bittorrent
               announceList
               comment
               creationDate
               mode
               info
                      name
        verifiedLength
        verifyIntegrityPending
        """

    def get_download(self, gid):
        return Download(self, self.client.tell_status(gid))

    def get_downloads(self, gids=None):
        downloads = []

        if gids:
            for gid in gids:
                downloads.append(Download(self, self.client.tell_status(gid)))
        else:
            downloads.extend(self.client.tell_active())
            downloads.extend(self.client.tell_waiting(0, 1000))
            downloads.extend(self.client.tell_stopped(0, 1000))
            downloads = [Download(self, d) for d in downloads]

        return downloads

    def move(self, download, pos):
        return self.client.change_position(download.gid, pos, "POS_CUR")

    def move_to(self, download, pos):
        return self.client.change_position(download.gid, pos, "POS_SET")

    def move_up(self, download, pos=1):
        return self.client.change_position(download.gid, -pos, "POS_CUR")

    def move_down(self, download, pos=1):
        return self.client.change_position(download.gid, pos, "POS_CUR")

    def move_to_top(self, download):
        return self.client.change_position(download.gid, 0, "POS_SET")

    def move_to_bottom(self, download):
        return self.client.change_position(download.gid, -1, "POS_SET")

    def remove(self, downloads):
        return [self.client.remove(d.gid) for d in downloads]

    def pause(self, downloads=None):
        if not downloads:
            return self.client.pause_all()
        return [self.client.pause(d.gid) for d in downloads]

    def resume(self, downloads=None):
        if not downloads:
            return self.client.unpause_all()
        return [self.client.unpause(d.gid) for d in downloads]

    def purge(self):
        return self.client.purge_download_result()

    def get_options(self, gids=None):
        if not gids:
            return Options(self, self.client.get_global_option())

        options = {}
        for gid in gids:
            options[gid] = Options(self, self.client.get_option(gid), gid)
        return options

    def set_options(self, options, gids=None):
        if isinstance(options, Options):
            client_options = options.get_struct()
        else:
            client_options = options

        if not gids:
            return self.client.change_global_option(client_options)

        results = {}
        for gid in gids:
            results[gid] = self.client.change_option(gid, client_options)
        return results

    def get_stats(self):
        return Stats(self.client.get_global_stat())
