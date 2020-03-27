"""
This module defines the API class, which makes use of a JSON-RPC client to provide higher-level methods to
interact easily with a remote aria2c process.
"""
import shutil
import threading
from base64 import b64encode
from pathlib import Path
from typing import Any, List, Optional, Union

from loguru import logger

from .client import Client, ClientException
from .downloads import Download
from .options import Options
from .stats import Stats
from .utils import get_version


class API:
    """
    A class providing high-level methods to interact with a remote aria2c process.

    This class is instantiated with a reference to a [`Client`][aria2p.client.Client] instance. It then uses this client
    to call remote procedures, or remote methods. While the client methods reflect exactly what aria2c is providing
    through JSON-RPC, this class's methods allow for easier / faster control of the remote process. It also
    wraps the information the client retrieves in Python object, like [`Download`][aria2p.downloads.Download],
    allowing for even more Pythonic interactions, without worrying about payloads, responses, JSON, etc..
    """

    def __init__(self, client=None) -> None:
        """
        Initialization method.

        Parameters:
            client: an instance of the [aria2p.client.Client][] class.
        """
        if client is None:
            client = Client()
        self.client = client
        self.listener = None

    def __repr__(self):
        return f"API({self.client!r})"

    def add_magnet(self, magnet_uri: str, options: Union[Options, dict] = None, position: int = None) -> Download:
        """
        Add a download with a Magnet URI.

        Parameters:
            magnet_uri: the Magnet URI.
            options: an instance of the [`Options`][aria2p.options.Options] class or a dictionary
              containing aria2c options to create the download with.
            position: the position where to insert the new download in the queue. Start at 0 (top).

        Returns:
            The newly created download object.
        """
        if options is None:
            options = {}

        if isinstance(options, Options):
            client_options = options.get_struct()
        else:
            client_options = options

        gid = self.client.add_uri([magnet_uri], client_options, position)

        return self.get_download(gid)

    def add_torrent(
        self,
        torrent_file_path: Union[str, Path],
        uris: List[str] = None,
        options: Union[Options, dict] = None,
        position: int = None,
    ) -> Download:
        """
        Add a download with a torrent file (usually .torrent extension).

        Parameters:
            torrent_file_path: the path to the torrent file.
            uris: a list of URIs used for Web-seeding.
            options: an instance of the [`Options`][aria2p.options.Options] class or a dictionary
              containing aria2c options to create the download with.
            position: the position where to insert the new download in the queue. Start at 0 (top).

        Returns:
            The newly created download object.
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

    def add_metalink(
        self, metalink_file_path: Union[str, Path], options: Union[Options, dict] = None, position: int = None
    ) -> List[Download]:
        """
        Add a download with a Metalink file.

        Parameters:
            metalink_file_path: the path to the Metalink file.
            options: an instance of the [`Options`][aria2p.options.Options] class or a dictionary
              containing aria2c options to create the download with.
            position: the position where to insert the new download in the queue. Start at 0 (top).

        Returns:
            The newly created download objects.
        """
        if options is None:
            options = {}

        if isinstance(options, Options):
            client_options = options.get_struct()
        else:
            client_options = options

        with open(metalink_file_path, "rb") as stream:
            metalink_contents = stream.read()
        encoded_contents = b64encode(metalink_contents).decode("utf8")

        gids = self.client.add_metalink(encoded_contents, client_options, position)

        return self.get_downloads(gids)

    def add_uris(
        self, uris: List[str], options: Optional[Union[Options, dict]] = None, position: Optional[int] = None
    ) -> Download:
        """
        Add a download with a URL (or more).

        Parameters:
            uris: a list of URIs that point to the same resource.
            options: an instance of the ``Options`` class or a dictionary
              containing aria2c options to create the download with.
            position: the position where to insert the new download in the queue. Start at 0 (top).

        Returns:
            The newly created download object.

        """
        if options is None:
            options = {}

        if isinstance(options, Options):
            client_options = options.get_struct()
        else:
            client_options = options

        gid = self.client.add_uri(uris, client_options, position)

        return self.get_download(gid)

    def search(self, patterns: List[str]) -> List[Download]:
        """
        Not implemented.

        Search and return [`Download`][aria2p.downloads.Download] objects based on multiple patterns.

        Parameters:
            patterns: the patterns used to filter the download list.

        Returns:
            The download objects matching the patterns.

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
        raise NotImplementedError

    def get_download(self, gid: str) -> Download:
        """
        Get a [`Download`][aria2p.downloads.Download] object thanks to its GID.

        Parameters:
            gid: the GID of the download to get.

        Returns:
            The retrieved download object.
        """
        return Download(self, self.client.tell_status(gid))

    def get_downloads(self, gids: List[str] = None) -> List[Download]:
        """
        Get a list of [`Download`][aria2p.downloads.Download] object thanks to their GIDs.

        Parameters:
            gids: the GIDs of the downloads to get. If None, return all the downloads.

        Returns:
            The retrieved download objects.
        """
        downloads = []

        if gids:
            for gid in gids:
                downloads.append(Download(self, self.client.tell_status(gid)))
        else:
            structs = []
            structs.extend(self.client.tell_active())
            structs.extend(self.client.tell_waiting(0, 1000))
            structs.extend(self.client.tell_stopped(0, 1000))
            downloads = [Download(self, struct) for struct in structs]

        return downloads

    def move(self, download: Download, pos: int) -> int:
        """
        Move a download in the queue, relatively to its current position.

        Parameters:
            download: the download object to move.
            pos: the relative position (1 to move down, -1 to move up, -2 to move up two times, etc.).

        Returns:
            The new position of the download.
        """
        return self.client.change_position(download.gid, pos, "POS_CUR")

    def move_to(self, download: Download, pos: int) -> int:
        """
        Move a download in the queue, with absolute positioning.

        Parameters:
            download: the download object to move.
            pos: the absolute position in the queue where to move the download. 0 for top, -1 for bottom.

        Returns:
            The new position of the download.
        """
        if pos < 0:
            how = "POS_END"
            pos = -pos
        else:
            how = "POS_SET"
        return self.client.change_position(download.gid, pos, how)

    def move_up(self, download: Download, pos: int = 1) -> int:
        """
        Move a download up in the queue.

        Parameters:
            download: the download object to move.
            pos: number of times to move up. With negative values, will move down (use move or move_down instead).

        Returns:
            The new position of the download.
        """
        return self.client.change_position(download.gid, -pos, "POS_CUR")

    def move_down(self, download: Download, pos: int = 1) -> int:
        """
        Move a download down in the queue.

        Parameters:
            download: the download object to move.
            pos: number of times to move down. With negative values, will move up (use move or move_up instead).

        Returns:
            The new position of the download.
        """
        return self.client.change_position(download.gid, pos, "POS_CUR")

    def move_to_top(self, download: Download) -> int:
        """
        Move a download to the top of the queue.

        Parameters:
            download: the download object to move.

        Returns:
            The new position of the download.
        """
        return self.client.change_position(download.gid, 0, "POS_SET")

    def move_to_bottom(self, download: Download) -> int:
        """
        Move a download to the bottom of the queue.

        Parameters:
            download: the download object to move.

        Returns:
            The new position of the download.
        """
        return self.client.change_position(download.gid, 0, "POS_END")

    def remove(
        self, downloads: List[Download], force: bool = False, files: bool = False, clean: bool = True
    ) -> List[bool]:
        """
        Remove the given downloads from the list.

        Parameters:
            downloads: the list of downloads to remove.
            force: whether to force the removal or not.
            files: whether to remove downloads files as well.
            clean: whether to remove the aria2 control file as well.

        Returns:
            Success or failure of the operation for each given download.
        """
        # TODO: batch/multicall candidate
        if force:
            remove_func = self.client.force_remove
        else:
            remove_func = self.client.remove

        result = []

        for download in downloads:
            if download.is_complete or download.is_removed or download.has_failed:
                logger.debug(f"Try to remove download result {download.gid}")
                try:
                    self.client.remove_download_result(download.gid)
                except ClientException as error:
                    logger.exception(error)
                    result.append(error)
                else:
                    logger.success(f"Removed download result {download.gid}")
                    result.append(True)
            else:
                logger.debug(f"Try to remove download {download.gid}")
                try:
                    removed_gid = remove_func(download.gid)
                except ClientException as error:
                    logger.exception(error)
                    result.append(error)
                else:
                    logger.success(f"Removed download {download.gid}")
                    result.append(True)
                    try:
                        self.client.remove_download_result(download.gid)
                    except ClientException as error2:
                        logger.debug(f"Failed to remove download result {download.gid}")
                        logger.opt(exception=True).trace(error2)
                    if removed_gid != download.gid:
                        logger.debug(
                            f"Removed download GID#{removed_gid} is different than download GID#{download.gid}"
                        )
                        try:
                            self.client.remove_download_result(removed_gid)
                        except ClientException as error2:
                            logger.debug(f"Failed to remove download result {removed_gid}")
                            logger.opt(exception=True).trace(error2)

            if clean:
                # FUTURE: use missing_ok parameter on Python 3.8
                try:
                    download.control_file_path.unlink()
                except FileNotFoundError:
                    logger.debug(f"aria2 control file {download.control_file_path} was not found")
                else:
                    logger.debug(f"Removed control file {download.control_file_path}")

            if files and result[-1]:
                self.remove_files([download], force=True)

        return result

    def remove_all(self, force: bool = False) -> bool:
        """
        Remove all downloads from the list.

        Parameters:
            force: whether to force the removal or not.

        Returns:
            Success or failure of the operation to remove all downloads.
        """
        return all(self.remove(self.get_downloads(), force=force))

    def pause(self, downloads: List[Download], force: bool = False) -> List[bool]:
        """
        Remove the given downloads from the list.

        Parameters:
            downloads: the list of downloads to remove.
            force: whether to pause immediately without contacting servers or not.

        Returns:
            Success or failure of the operation for each given download.
        """
        # TODO: batch/multicall candidate
        if force:
            pause_func = self.client.force_pause
        else:
            pause_func = self.client.pause

        result = []

        for download in downloads:
            try:
                pause_func(download.gid)
            except ClientException as error:
                logger.debug(f"Failed to pause download {download.gid}")
                logger.opt(exception=True).trace(error)
                result.append(error)
            else:
                result.append(True)

        return result

    def pause_all(self, force: bool = False) -> bool:
        """
        Remove the given downloads from the list.

        Parameters:
            force: whether to pause immediately without contacting servers or not.

        Returns:
            Success or failure of the operation to pause all downloads.
        """
        if force:
            pause_func = self.client.force_pause_all
        else:
            pause_func = self.client.pause_all
        return pause_func() == "OK"

    def resume(self, downloads: List[Download]) -> List[bool]:
        """
        Resume (unpause) the given downloads.

        Parameters:
            downloads: the list of downloads to resume.

        Returns:
            Success or failure of the operation for each given download.
        """
        # TODO: batch/multicall candidate
        result = []

        for download in downloads:
            try:
                self.client.unpause(download.gid)
            except ClientException as error:
                logger.debug(f"Failed to resume download {download.gid}")
                logger.opt(exception=True).trace(error)
                result.append(error)
            else:
                result.append(True)

        return result

    def resume_all(self) -> bool:
        """
        Resume (unpause) all downloads.

        Returns:
            Success or failure of the operation to resume all downloads.
        """
        return self.client.unpause_all() == "OK"

    def autopurge(self) -> bool:
        """
        Purge completed, removed or failed downloads from the queue.

        Returns:
            Success or failure of the operation.
        """
        version = get_version()
        if version.major == 0 and 9 > version.minor >= 7:
            logger.warning("Future change warning: API method 'autopurge' will be renamed 'purge' in version 0.9.0.")
        return self.client.purge_download_result()

    def get_options(self, downloads: List[Download]) -> List[Options]:
        """
        Get options for each of the given downloads.

        Parameters:
            downloads: the list of downloads to get the options of.

        Returns:
            Options object for each given download.
        """
        # TODO: batch/multicall candidate
        options = []
        for download in downloads:
            options.append(Options(self, self.client.get_option(download.gid), download))
        return options

    def get_global_options(self) -> Options:
        """
        Get the global options.

        Returns:
            The global aria2c options.
        """
        return Options(self, self.client.get_global_option())

    def set_options(self, options: Union[Options, dict], downloads: List[Download]) -> List[bool]:
        """
        Set options for specific downloads.

        Parameters:
            options: an instance of the [`Options`][aria2p.options.Options] class or a dictionary
              containing aria2c options to create the download with.
            downloads: the list of downloads to set the options for.

        Returns:
            Success or failure of the operation for changing options for each given download.
        """
        if isinstance(options, Options):
            client_options = options.get_struct()
        else:
            client_options = options

        # TODO: batch/multicall candidate
        results = []
        for download in downloads:
            results.append(self.client.change_option(download.gid, client_options) == "OK")
        return results

    def set_global_options(self, options: Union[Options, dict]) -> bool:
        """
        Set global options.

        Parameters:
            options: an instance of the [`Options`][aria2p.options.Options] class or a dictionary
              containing aria2c options to create the download with.

        Returns:
            Success or failure of the operation for changing global options.
        """
        if isinstance(options, Options):
            client_options = options.get_struct()
        else:
            client_options = options

        return self.client.change_global_option(client_options) == "OK"

    def get_stats(self) -> Stats:
        """
        Get the stats of the remote aria2c process.

        Returns:
            stats: the global stats returned by the remote process.
        """
        return Stats(self.client.get_global_stat())

    @staticmethod
    def remove_files(downloads: List[Download], force: bool = False) -> List[bool]:
        """
        Remove downloaded files.

        Parameters:
            downloads:  the list of downloads for which to remove files.
            force: whether to remove files even if download is not complete.

        Returns:
            Success or failure of the operation for each given download.
        """
        results = []
        for download in downloads:
            if download.is_complete or force:
                for path in download.root_files_paths:
                    if path.is_dir():
                        shutil.rmtree(str(path))
                    else:
                        path.unlink()
                results.append(True)
            else:
                results.append(False)
        return results

    @staticmethod
    def move_files(downloads: List[Download], to_directory: Union[str, Path], force: bool = False) -> List[bool]:
        """
        Move downloaded files to another directory.

        Parameters:
            downloads:  the list of downloads for which to move files.
            to_directory: the target directory to move files to.
            force: whether to move files even if download is not complete.

        Returns:
            Success or failure of the operation for each given download.
        """
        if isinstance(to_directory, str):
            to_directory = Path(to_directory)

        # raises FileExistsError when target is already a file
        to_directory.mkdir(parents=True, exist_ok=True)

        results = []
        for download in downloads:
            if download.is_complete or force:
                for path in download.root_files_paths:
                    shutil.move(str(path), str(to_directory))
                results.append(True)
            else:
                results.append(False)
        return results

    @staticmethod
    def copy_files(downloads: List[Download], to_directory: Union[str, Path], force: bool = False) -> List[bool]:
        """
        Copy downloaded files to another directory.

        Parameters:
            downloads:  the list of downloads for which to move files.
            to_directory: the target directory to copy files into.
            force: whether to move files even if download is not complete.

        Returns:
            Success or failure of the operation for each given download.
        """
        if isinstance(to_directory, str):
            to_directory = Path(to_directory)

        # raises FileExistsError when target is already a file
        to_directory.mkdir(parents=True, exist_ok=True)

        results = []
        for download in downloads:
            if download.is_complete or force:
                for path in download.root_files_paths:
                    if path.is_dir():
                        shutil.copytree(str(path), str(to_directory / path.name))
                    elif path.is_file():
                        shutil.copy(str(path), str(to_directory))

                results.append(True)
            else:
                results.append(False)
        return results

    def listen_to_notifications(self, threaded: bool = False, **kwargs: Any) -> None:
        """
        Start listening to aria2 notifications via WebSocket.

        This method differs from [`Client.listen_to_notifications`][aria2p.client.Client.listen_to_notifications]
        in that it expects callbacks accepting two arguments, ``api`` and ``gid``, instead of only ``gid``.
        Accepting ``api`` allows to use the high-level methods of the [`API`][aria2p.api.API] class.

        Stop listening to notifications with the [`API.stop_listening`][aria2p.api.API.stop_listening] method.

        Parameters:
            threaded: Whether to start the listening loop in a thread or not (non-blocking or blocking).
        """

        def closure(callback):
            return (lambda gid: callback(self, gid)) if callable(callback) else None

        def run():
            self.client.listen_to_notifications(
                **{key: closure(value) if key.startswith("on_") else value for key, value in kwargs.items()}
            )

        if threaded:
            kwargs["handle_signals"] = False
            self.listener = threading.Thread(target=run)
            self.listener.start()
        else:
            run()

    def stop_listening(self) -> None:
        """
        Stop listening to notifications.

        If the listening loop was threaded, this method will wait for the thread to finish.
        The time it takes for the thread to finish will depend on the timeout given while calling
        [`listen_to_notifications`][aria2p.api.API.listen_to_notifications].
        """
        self.client.stop_listening()
        if self.listener:
            self.listener.join()
        self.listener = None
