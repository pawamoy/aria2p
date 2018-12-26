"""
This module defines the API class, which makes use of a JSON-RPC client to provide higher-level methods to
interact easily with a remote aria2c process.
"""


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
        self.downloads = {}
        self.options = None
        self.stats = None

    def fetch(self):
        self.fetch_downloads()
        self.fetch_stats()

    def fetch_downloads(self):
        self.downloads.clear()
        self.downloads = {d.gid: d for d in self.get_downloads()}

    def fetch_options(self):
        self.options = Options(self, self.client.get_global_option)

    def fetch_stats(self):
        self.stats = Stats(self.client.get_global_stat())

    def add_magnet(self, magnet_uri):
        pass

    def add_torrent(self, torrent_file):
        pass

    def add_metalink(self, metalink):
        pass

    def add_url(self, url):
        pass

    def add_download(self, download):
        pass

    def find(self, patterns):
        pass

    def get_gid(self, filter):
        pass

    def get_gids(self, filters=None):
        gids = []
        gids.extend(self.client.tell_active(keys=["gid"]))
        gids.extend(self.client.tell_waiting(0, 1000, keys=["gid"]))
        gids.extend(self.client.tell_stopped(0, 1000, keys=["gid"]))
        return gids

    def get_download(self, gid):
        if gid in self.downloads:
            return self.downloads[gid]
        return Download(self, self.client.tell_status(gid))

    def get_downloads(self, gids=None):
        downloads = []

        if gids:
            for gid in gids:
                if gid in self.downloads:
                    downloads.append(self.downloads[gid])
                else:
                    downloads.append(Download(self, self.client.tell_status(gid)))
        else:
            downloads.extend(self.client.tell_active())
            downloads.extend(self.client.tell_waiting(0, 1000))
            downloads.extend(self.client.tell_stopped(0, 1000))
            downloads = [Download(self, d) for d in downloads]

        return downloads

    def move(self, download, pos):
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

    def get_options(self, gids=None):
        if not gids:
            return Options(self, self.client.get_global_option())

        options = {}
        for gid in gids:
            options[gid] = Options(self, self.client.get_option(gid), gid)
        return options

    def set_options(self, options, gids=None):
        if not gids:
            return self.client.change_global_option(options)

        results = {}
        for gid in gids:
            results[gid] = self.client.change_option(gid, options)
        return results
