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

    This class is instantiated with a reference to a :class:`aria2p.JSONRPCClient` instance. It then uses this client
    to call remote procedures, or remote methods. The client methods reflect exactly what aria2c is providing
    through JSON-RPC, while this class's methods allow for easier / faster control of the remote process. It also
    wraps the information the client retrieves in Python object, like  :class:`downloads.Download`, allowing for
    even more Pythonic interactions, without worrying about payloads, responses, JSON, etc..
    """

    def __init__(self, json_rpc_client):
        """
        Initialization method.

        Args:
            json_rpc_client (:class:`aria2p.JSONRPCClient`): an instance of the ``JSONRPCClient`` class.
        """
        self.client = json_rpc_client

    def add_magnet(self, magnet_uri, options=None, position=None):
        """
        Add a download with a Magnet URI.

        Args:
            magnet_uri (str): the Magnet URI.
            options (:class:`aria2p.Options` or dict): an instance of the ``Options`` class or a dictionary
              containing Aria2c options to create the download with.
            position (int): the position where to insert the new download in the queue. Start at 0 (top).

        Returns:
            :class:`aria2p.Download` instance: the newly created download object.
        """
        if options is None:
            options = {}

        if isinstance(options, Options):
            client_options = options.get_struct()
        else:
            client_options = options

        gid = self.client.add_uri([magnet_uri], client_options, position)

        return self.get_download(gid)

    def add_torrent(self, torrent_file_path, uris=None, options=None, position=None):
        """
        Add a download with a Torrent file (usually .torrent extension).

        Args:
            torrent_file_path (str/Path): the path to the Torrent file.
            uris (list of str): a list of URIs used for Web-seeding.
            options (:class:`aria2p.Options` or dict): an instance of the ``Options`` class or a dictionary
              containing Aria2c options to create the download with.
            position (int): the position where to insert the new download in the queue. Start at 0 (top).

        Returns:
            :class:`aria2p.Download` instance: the newly created download object.
        """
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
        """
        Add a download with a Metalink file.

        Args:
            metalink_file_path (str/Path): the path to the Metalink file.
            options (:class:`aria2p.Options` or dict): an instance of the ``Options`` class or a dictionary
              containing Aria2c options to create the download with.
            position (int): the position where to insert the new download in the queue. Start at 0 (top).

        Returns:
            :class:`aria2p.Download` instance: the newly created download object.
        """
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
        """
        Add a download with a URL (or more).

        Args:
            urls (list of str): the list of URLs that point to the same resource.
            options (:class:`aria2p.Options` or dict): an instance of the ``Options`` class or a dictionary
              containing Aria2c options to create the download with.
            position (int): the position where to insert the new download in the queue. Start at 0 (top).

        Returns:
            :class:`aria2p.Download` instance: the newly created download object.

        """
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
        Not implemented.

        Search and return :class:`aria2p.Download` object based on multiple patterns.

        Args:
            patterns (list of dict): the patterns used to filter the download list.

        Returns:
            list of :class:`aria2p.Download` instances: the download objects matching the patterns.

        """
        # gid
        # status
        # totalLength
        # completedLength
        # uploadLength
        # bitfield
        # downloadSpeed
        # uploadSpeed
        # infoHash
        # numSeeders
        # seeder
        # pieceLength
        # numPieces
        # connections
        # errorCode
        # errorMessage
        # followedBy
        # following
        # belongsTo
        # dir
        # files
        # bittorrent
        #        announceList
        #        comment
        #        creationDate
        #        mode
        #        info
        #               name
        # verifiedLength
        # verifyIntegrityPending

    def get_download(self, gid):
        """
        Get a :class:`aria2p.Download` object thanks to its GID.

        Args:
            gid (str): the GID of the download to get.

        Returns:
            :class:`aria2p.Download` instance: the retrieved download object.
        """
        return Download(self, self.client.tell_status(gid))

    def get_downloads(self, gids=None):
        """
        Get a list :class:`aria2p.Download` object thanks to their GIDs.

        Args:
            gids (list of str): the GIDs of the downloads to get. If None, return all the downloads.

        Returns:
            list of :class:`aria2p.Download` instances: the retrieved download objects.
        """
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
        """
        Move a download in the queue, relatively to its current position.

        Args:
            download (:class:`aria2p.Download`): the download object to move.
            pos (int): the relative position (1 to move down, -1 to move up, -2 to move up two times, etc.).

        Returns:
            bool: Success or failure of the operation.
        """
        return self.client.change_position(download.gid, pos, "POS_CUR")

    def move_to(self, download, pos):
        """
        Move a download in the queue, with absolute positioning.

        Args:
            download (:class:`aria2p.Download`): the download object to move.
            pos (int): the absolute position in the queue where to move the download. 0 for top, -1 for bottom.

        Returns:
            bool: Success or failure of the operation.
        """
        return self.client.change_position(download.gid, pos, "POS_SET")

    def move_up(self, download, pos=1):
        """
        Move a download up in the queue.

        Args:
            download (:class:`aria2p.Download`): the download object to move.
            pos (int): number of times to move up. With negative values, will move down (use move or move_down instead).

        Returns:
            bool: Success or failure of the operation.
        """
        return self.client.change_position(download.gid, -pos, "POS_CUR")

    def move_down(self, download, pos=1):
        """
        Move a download down in the queue.

        Args:
            download (:class:`aria2p.Download`): the download object to move.
            pos (int): number of times to move down. With negative values, will move up (use move or move_up instead).

        Returns:
            bool: Success or failure of the operation.
        """
        return self.client.change_position(download.gid, pos, "POS_CUR")

    def move_to_top(self, download):
        """
        Move a download to the top of the queue.

        Args:
            download (:class:`aria2p.Download`): the download object to move.

        Returns:
            bool: Success or failure of the operation.
        """
        return self.client.change_position(download.gid, 0, "POS_SET")

    def move_to_bottom(self, download):
        """
        Move a download to the bottom of the queue.

        Args:
            download (:class:`aria2p.Download`): the download object to move.

        Returns:
            bool: Success or failure of the operation.
        """
        return self.client.change_position(download.gid, -1, "POS_SET")

    def remove(self, downloads):
        """
        Remove the given downloads from the list.

        Args:
            downloads (list of :class:`aria2p.Download`): the list of downloads to remove.

        Returns:
            list of bool: Success or failure of the operation for each given download.
        """
        return [self.client.remove(d.gid) for d in downloads]

    def pause(self, downloads=None):
        """
        Remove the given downloads from the list.

        Args:
            downloads (list of :class:`aria2p.Download`): the list of downloads to remove. If None, pause all downloads.

        Returns:
            bool or list of bool: Success or failure of the operation, respectively
              for all downloads or for each given download.
        """
        if not downloads:
            return self.client.pause_all()
        return [self.client.pause(d.gid) for d in downloads]

    def resume(self, downloads=None):
        """
        Resume (unpause) the given downloads.

        Args:
            downloads (list of :class:`aria2p.Download`): the list of downloads to resume. If None, resume all downloads.

        Returns:
            bool or list of bool: Success or failure of the operation, respectively
              for all downloads or for each given download.
        """
        if not downloads:
            return self.client.unpause_all()
        return [self.client.unpause(d.gid) for d in downloads]

    def purge(self):
        """
        Delete completed, removed or failed downloads from the queue.

        Returns:
            bool: Success or failure of the operation.
        """
        return self.client.purge_download_result()

    def get_options(self, downloads=None):
        if not downloads:
            return Options(self, self.client.get_global_option())

        options = {}
        for download in downloads:
            options[download.gid] = Options(self, self.client.get_option(download.gid), download.gid)
        return options

    def set_options(self, options, downloads=None):
        if isinstance(options, Options):
            client_options = options.get_struct()
        else:
            client_options = options

        if not downloads:
            return self.client.change_global_option(client_options)

        results = {}
        for download in downloads:
            results[download.gid] = self.client.change_option(download.gid, client_options)
        return results

    def get_stats(self):
        return Stats(self.client.get_global_stat())
