"""Aria2 API.

This module defines the API class, which makes use of a JSON-RPC client to provide higher-level methods to
interact easily with a remote aria2c process.
"""

from __future__ import annotations

import functools
import shutil
import aioshutil
import asyncio
from inspect import iscoroutinefunction
from base64 import b64encode
from pathlib import Path
from typing import Callable, Dict, Iterator, List, TextIO, Tuple, Union, Coroutine

from loguru import logger

from aria2p.client import Client, AsyncClient, ClientException
from aria2p.downloads import Download, AsyncDownload
from aria2p.options import SyncOptions, AsyncOptions
from aria2p.stats import Stats

OptionsType = Union[SyncOptions | AsyncOptions, dict]
OperationResult = Union[bool, ClientException]
InputFileContentsType = List[Tuple[List[str], Dict[str, str]]]


class API:
    """A class providing high-level methods to interact with a remote aria2c process.

    This class is instantiated with a reference to a [`Client`][aria2p.client.Client] instance. It then uses this client
    to call remote procedures, or remote methods. While the client methods reflect exactly what aria2c is providing
    through JSON-RPC, this class's methods allow for easier / faster control of the remote process. It also
    wraps the information the client retrieves in Python object, like [`Download`][aria2p.downloads.Download],
    allowing for even more Pythonic interactions, without worrying about payloads, responses, JSON, etc..
    """

    def __init__(self, client: Client | None = None) -> None:
        """Initialize the object.

        Parameters:
            client: An instance of the [aria2p.client.Client][] class.
        """
        self.client = client or Client()
        self.listener: asyncio.create_task | None = None
        self.loop = None

    def __repr__(self) -> str:
        return f"API({self.client!r})"

    def __enter__(self) -> API:
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.client.session.close()
        self.client.session = None

    def add(
        self,
        uri: str,
        options: OptionsType | None = None,
        position: int | None = None,
    ) -> list[Download]:
        """Add a download (guess its type).

        If the provided URI is in fact a file-path, and is neither a torrent or a metalink,
        then we read its lines and try to add each line as a download, recursively.

        Parameters:
            uri: The URI or file-path to add.
            options: An instance of the [`SyncOptions`][aria2p.options.SyncOptions] class or a dictionary
                containing aria2c options to create the download with.
            position: The position where to insert the new download in the queue. Start at 0 (top).

        Returns:
            The created downloads.
        """
        new_downloads = []
        path = Path(uri)

        # On Windows, path.exists() generates an OSError when path is an URI
        # See https://github.com/pawamoy/aria2p/issues/41
        try:
            path_exists = path.exists()
        except OSError:
            path_exists = False

        if path_exists:
            if path.suffix == ".torrent":
                new_downloads.append(self.add_torrent(path, options=options, position=position))
            elif path.suffix == ".metalink":
                new_downloads.extend(self.add_metalink(path, options=options, position=position))
            else:
                for uris, download_options in self.parse_input_file(path):
                    # Add batch downloads in specified position in queue.
                    new_downloads.append(self.add_uris(uris, options=download_options, position=position))
                    if position is not None:
                        position += 1

        elif uri.startswith("magnet:?"):
            new_downloads.append(self.add_magnet(uri, options=options, position=position))
        else:
            new_downloads.append(self.add_uris([uri], options=options, position=position))

        return new_downloads

    def add_magnet(self, magnet_uri: str, options: OptionsType | None = None, position: int | None = None) -> Download:
        """Add a download with a Magnet URI.

        Parameters:
            magnet_uri: The Magnet URI.
            options: An instance of the [`SyncOptions`][aria2p.options.SyncOptions] class or a dictionary
                containing aria2c options to create the download with.
            position: The position where to insert the new download in the queue. Start at 0 (top).

        Returns:
            The newly created download object.
        """
        if options is None:
            options = {}

        client_options = options.get_struct() if isinstance(options, SyncOptions) else options

        gid = self.client.add_uri([magnet_uri], client_options, position)

        return self.get_download(gid)

    def add_torrent(
        self,
        torrent_file_path: str | Path,
        uris: list[str] | None = None,
        options: OptionsType | None = None,
        position: int | None = None,
    ) -> Download:
        """Add a download with a torrent file (usually .torrent extension).

        Parameters:
            torrent_file_path: The path to the torrent file.
            uris: A list of URIs used for Web-seeding.
            options: An instance of the [`SyncOptions`][aria2p.options.SyncOptions] class or a dictionary
                containing aria2c options to create the download with.
            position: The position where to insert the new download in the queue. Start at 0 (top).

        Returns:
            The newly created download object.
        """
        if uris is None:
            uris = []

        if options is None:
            options = {}

        client_options = (
            options.get_struct() if isinstance(options, SyncOptions) else options
        )

        with open(torrent_file_path, "rb") as stream:
            torrent_contents = stream.read()
        encoded_contents = b64encode(torrent_contents).decode("utf8")

        gid = self.client.add_torrent(encoded_contents, uris, client_options, position)

        return self.get_download(gid)

    def add_metalink(
        self,
        metalink_file_path: str | Path,
        options: OptionsType | None = None,
        position: int | None = None,
    ) -> list[Download]:
        """Add a download with a Metalink file.

        Parameters:
            metalink_file_path: The path to the Metalink file.
            options: An instance of the [`SyncOptions`][aria2p.options.SyncOptions] class or a dictionary
                containing aria2c options to create the download with.
            position: The position where to insert the new download in the queue. Start at 0 (top).

        Returns:
            The newly created download objects.
        """
        if options is None:
            options = {}

        client_options = (
            options.get_struct() if isinstance(options, SyncOptions) else options
        )

        with open(metalink_file_path, "rb") as stream:
            metalink_contents = stream.read()
        encoded_contents = b64encode(metalink_contents).decode("utf8")

        gids = self.client.add_metalink(encoded_contents, client_options, position)

        return self.get_downloads(gids)

    def add_uris(
        self,
        uris: list[str],
        options: OptionsType | None = None,
        position: int | None = None,
    ) -> Download:
        """Add a download with a URL (or more).

        Parameters:
            uris: A list of URIs that point to the same resource.
            options: An instance of the `SyncOptions` class or a dictionary
                containing aria2c options to create the download with.
            position: The position where to insert the new download in the queue. Start at 0 (top).

        Returns:
            The newly created download object.

        """
        if options is None:
            options = {}

        client_options = (
            options.get_struct() if isinstance(options, SyncOptions) else options
        )

        gid = self.client.add_uri(uris, client_options, position)

        return self.get_download(gid)

    def search(self, patterns: list[str]) -> list[Download]:
        """Not implemented.

        Search and return [`Download`][aria2p.downloads.Download] objects based on multiple patterns.

        Parameters:
            patterns: The patterns used to filter the download list.

        Raises:
            NotImplementedError: This method is not implemented yet.
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
        """Get a [`Download`][aria2p.downloads.Download] object thanks to its GID.

        Parameters:
            gid: The GID of the download to get.

        Returns:
            The retrieved download object.
        """
        return Download(self, self.client.tell_status(gid))

    def get_downloads(self, gids: list[str] | None = None) -> list[Download]:
        """Get a list of [`Download`][aria2p.downloads.Download] object thanks to their GIDs.

        Parameters:
            gids: The GIDs of the downloads to get. If None, return all the downloads.

        Returns:
            The retrieved download objects.
        """
        downloads = []

        if gids:
            downloads.extend(Download(self, self.client.tell_status(gid)) for gid in gids)
        else:
            structs = []
            structs.extend(self.client.tell_active())
            structs.extend(self.client.tell_waiting(0, 1000))
            structs.extend(self.client.tell_stopped(0, 1000))
            downloads = [Download(self, struct) for struct in structs]

        return downloads

    def move(self, download: Download, pos: int) -> int:
        """Move a download in the queue, relatively to its current position.

        Parameters:
            download: The download object to move.
            pos: The relative position (1 to move down, -1 to move up, -2 to move up two times, etc.).

        Returns:
            The new position of the download.
        """
        return self.client.change_position(download.gid, pos, "POS_CUR")

    def move_to(self, download: Download, pos: int) -> int:
        """Move a download in the queue, with absolute positioning.

        Parameters:
            download: The download object to move.
            pos: The absolute position in the queue where to move the download. 0 for top, -1 for bottom.

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
        """Move a download up in the queue.

        Parameters:
            download: The download object to move.
            pos: Number of times to move up. With negative values, will move down (use move or move_down instead).

        Returns:
            The new position of the download.
        """
        return self.client.change_position(download.gid, -pos, "POS_CUR")

    def move_down(self, download: Download, pos: int = 1) -> int:
        """Move a download down in the queue.

        Parameters:
            download: The download object to move.
            pos: Number of times to move down. With negative values, will move up (use move or move_up instead).

        Returns:
            The new position of the download.
        """
        return self.client.change_position(download.gid, pos, "POS_CUR")

    def move_to_top(self, download: Download) -> int:
        """Move a download to the top of the queue.

        Parameters:
            download: The download object to move.

        Returns:
            The new position of the download.
        """
        return self.client.change_position(download.gid, 0, "POS_SET")

    def move_to_bottom(self, download: Download) -> int:
        """Move a download to the bottom of the queue.

        Parameters:
            download: The download object to move.

        Returns:
            The new position of the download.
        """
        return self.client.change_position(download.gid, 0, "POS_END")

    def retry_downloads(
        self,
        downloads: list[Download],
        clean: bool = False,  # noqa: FBT001,FBT002
    ) -> list[OperationResult]:
        """Resume failed downloads from where they left off with new GIDs.

        Parameters:
            downloads: The list of downloads to remove.
            clean: Whether to remove the aria2 control file as well.

        Returns:
            Success or failure of the operation for each given download.
        """
        result: list[OperationResult] = []

        for download in downloads:
            if not download.has_failed:
                continue
            try:
                uri = download.files[0].uris[0]["uri"]
            except IndexError:
                continue
            try:
                new_download_gid = self.add_uris([uri], download.options)
            except ClientException as error:
                result.append(error)
            else:
                if not new_download_gid:
                    continue

                self.remove([download], clean=clean)
                result.append(True)

        return result

    def remove(
        self,
        downloads: list[Download],
        force: bool = False,  # noqa: FBT001,FBT002
        files: bool = False,  # noqa: FBT001,FBT002
        clean: bool = True,  # noqa: FBT001,FBT002
    ) -> list[OperationResult]:
        """Remove the given downloads from the list.

        Parameters:
            downloads: The list of downloads to remove.
            force: Whether to force the removal or not.
            files: Whether to remove downloads files as well.
            clean: Whether to remove the aria2 control file as well.

        Returns:
            Success or failure of the operation for each given download.
        """
        # Note: batch/multicall candidate
        remove_func = self.client.force_remove if force else self.client.remove

        result: list[OperationResult] = []

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
                    try:  # (nested try)
                        self.client.remove_download_result(download.gid)
                    except ClientException as error:
                        logger.debug(f"Failed to remove download result {download.gid}")
                        logger.opt(exception=True).trace(error)
                    if removed_gid != download.gid:
                        logger.debug(
                            f"Removed download GID#{removed_gid} is different than download GID#{download.gid}",
                        )
                        try:
                            self.client.remove_download_result(removed_gid)
                        except ClientException as error:
                            logger.debug(f"Failed to remove download result {removed_gid}")
                            logger.opt(exception=True).trace(error)

            if clean:
                download.control_file_path.unlink(missing_ok=True)
                logger.debug(f"Removed control file {download.control_file_path}")

            if files and result[-1]:
                self.remove_files([download], force=True)

        return result

    def remove_all(self, force: bool = False) -> bool:  # noqa: FBT001,FBT002
        """Remove all downloads from the list.

        Parameters:
            force: Whether to force the removal or not.

        Returns:
            Success or failure of the operation to remove all downloads.
        """
        return all(self.remove(self.get_downloads(), force=force))

    def pause(self, downloads: list[Download], force: bool = False) -> list[OperationResult]:  # noqa: FBT001,FBT002
        """Pause the given (active) downloads.

        Parameters:
            downloads: The list of downloads to pause.
            force: Whether to pause immediately without contacting servers or not.

        Returns:
            Success or failure of the operation for each given download.
        """
        # Note: batch/multicall candidate
        pause_func = self.client.force_pause if force else self.client.pause

        result: list[OperationResult] = []

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

    def pause_all(self, force: bool = False) -> bool:  # noqa: FBT001,FBT002
        """Pause all (active) downloads.

        Parameters:
            force: Whether to pause immediately without contacting servers or not.

        Returns:
            Success or failure of the operation to pause all downloads.
        """
        pause_func = self.client.force_pause_all if force else self.client.pause_all
        return pause_func() == "OK"

    def resume(self, downloads: list[Download]) -> list[OperationResult]:
        """Resume (unpause) the given downloads.

        Parameters:
            downloads: The list of downloads to resume.

        Returns:
            Success or failure of the operation for each given download.
        """
        # Note: batch/multicall candidate
        result: list[OperationResult] = []

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
        """Resume (unpause) all downloads.

        Returns:
            Success or failure of the operation to resume all downloads.
        """
        return self.client.unpause_all() == "OK"

    def purge(self) -> bool:
        """Purge completed, removed or failed downloads from the queue.

        Returns:
            Success or failure of the operation.
        """
        return self.client.purge_download_result() == "OK"

    def autopurge(self) -> bool:
        """Purge completed, removed or failed downloads from the queue.

        Deprecated. Use [`purge`][aria2p.api.API.purge] instead.

        Returns:
            Success or failure of the operation.
        """
        logger.warning("Deprecation warning: API method 'autopurge' is deprecated, use 'purge' instead.")
        return self.purge()

    def get_options(self, downloads: list[Download]) -> list[SyncOptions]:
        """Get options for each of the given downloads.

        Parameters:
            downloads: The list of downloads to get the options of.

        Returns:
            SyncOptions object for each given download.
        """
        return [
            SyncOptions(self, self.client.get_option(download.gid), download)
            for download in downloads
        ]

    def get_global_options(self) -> SyncOptions:
        """Get the global options.

        Returns:
            The global aria2c options.
        """
        return SyncOptions(self, self.client.get_global_option())

    def set_options(self, options: OptionsType, downloads: list[Download]) -> list[bool]:
        """Set options for specific downloads.

        Parameters:
            options: An instance of the [`SyncOptions`][aria2p.options.SyncOptions] class or a dictionary
                containing aria2c options to create the download with.
            downloads: The list of downloads to set the options for.

        Returns:
            Success or failure of the operation for changing options for each given download.
        """
        client_options = options.get_struct() if isinstance(options, SyncOptions) else options

        return [
            self.client.change_option(download.gid, client_options) == "OK"
            for download in downloads
        ]

    def set_global_options(self, options: OptionsType) -> bool:
        """Set global options.

        Parameters:
            options: An instance of the [`SyncOptions`][aria2p.options.SyncOptions] class or a dictionary
                containing aria2c options to create the download with.

        Returns:
            Success or failure of the operation for changing global options.
        """
        client_options = (
            options.get_struct() if isinstance(options, SyncOptions) else options
        )

        return self.client.change_global_option(client_options) == "OK"

    def get_stats(self) -> Stats:
        """Get the stats of the remote aria2c process.

        Returns:
            The global stats returned by the remote process.
        """
        return Stats(self.client.get_global_stat())

    @staticmethod
    def remove_files(
        downloads: list[Download],
        force: bool = False,  # noqa: FBT001,FBT002
    ) -> list[bool]:
        """Remove downloaded files.

        Parameters:
            downloads:  the list of downloads for which to remove files.
            force: Whether to remove files even if download is not complete.

        Returns:
            Success or failure of the operation for each given download.
        """
        results = []
        for download in downloads:
            if download.is_complete or force:
                for path in download.root_files_paths:
                    if path.is_dir():
                        try:
                            shutil.rmtree(str(path))
                        except OSError as error:
                            logger.error(f"Could not delete directory '{path}'")
                            logger.opt(exception=True).trace(error)
                            results.append(False)
                        else:
                            results.append(True)
                    else:
                        try:
                            path.unlink()
                        except FileNotFoundError as error:
                            logger.warning(f"File '{path}' did not exist when trying to delete it")
                            logger.opt(exception=True).trace(error)
                        results.append(True)
            else:
                results.append(False)
        return results

    @staticmethod
    def move_files(
        downloads: list[Download],
        to_directory: str | Path,
        force: bool = False,  # noqa: FBT001,FBT002
    ) -> list[bool]:
        """Move downloaded files to another directory.

        Parameters:
            downloads:  the list of downloads for which to move files.
            to_directory: The target directory to move files to.
            force: Whether to move files even if download is not complete.

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
    def copy_files(
        downloads: list[Download],
        to_directory: str | Path,
        force: bool = False,  # noqa: FBT001,FBT002
    ) -> list[bool]:
        """Copy downloaded files to another directory.

        Parameters:
            downloads:  the list of downloads for which to move files.
            to_directory: The target directory to copy files into.
            force: Whether to move files even if download is not complete.

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

    def listen_to_notifications(
        self,
        block: bool = True,  # noqa: FBT001,FBT002
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

        This method differs from [`Client.listen_to_notifications`][aria2p.client.Client.listen_to_notifications]
        in that it expects callbacks accepting two arguments, `api` and `gid`, instead of only `gid`.
        Accepting `api` allows to use the high-level methods of the [`API`][aria2p.api.API] class.

        Stop listening to notifications with the [`API.stop_listening`][aria2p.api.API.stop_listening] method.

        Parameters:
            block: Whether to start the listening loop in a new task or not (block execute).
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

        def closure(callback: Callable | None) -> Callable | None:
            return functools.partial(callback, self) if callable(callback) else None

        kwargs = {
            "on_download_start": closure(on_download_start),
            "on_download_pause": closure(on_download_pause),
            "on_download_stop": closure(on_download_stop),
            "on_download_complete": closure(on_download_complete),
            "on_download_error": closure(on_download_error),
            "on_bt_download_complete": closure(on_bt_download_complete),
            "timeout": timeout,
            "handle_signals": handle_signals,
        }
        try:
            self.loop = asyncio.get_event_loop()
        except:
            self.loop = asyncio.new_event_loop()
        if not block:
            kwargs["handle_signals"] = False
            self.listener = self.loop.create_task(
                self.client.listen_to_notifications(**kwargs)
            )
        else:
            self.loop.run_until_complete(self.client.listen_to_notifications(**kwargs))  # type: ignore[arg-type]

    def stop_listening(self) -> None:
        """Stop listening to notifications.

        If the listening loop was threaded, this method will wait for the thread to finish.
        The time it takes for the thread to finish will depend on the timeout given while calling
        [`listen_to_notifications`][aria2p.api.API.listen_to_notifications].
        """
        self.client.stop_listening()
        if self.listener:
            self.loop.run_until_complete(self.listener.cancel())
        self.listener = None

    def split_input_file(self, lines: list[str] | TextIO) -> Iterator[list[str]]:
        """Helper to split downloads in an input file.

        Parameters:
             lines: The lines of the input file.

        Yields:
            list[str]: Blocks of lines.
        """
        block: list[str] = []
        for line in lines:
            if line.lstrip().startswith("#"):  # Ignore Comments
                continue
            if not line.strip():  # Ignore empty line
                continue
            if not line.startswith(" ") and block:  # URIs line
                yield block
                block = []
            block.append(line.rstrip("\n"))
        if block:
            yield block

    def parse_input_file(self, input_file: str | Path) -> InputFileContentsType:
        """Parse a file with URIs or an aria2c input file.

        Parameters:
            input_file: Path to file with URIs or aria2c input file.

        Returns:
            List of tuples containing list of URIs and dictionary with aria2c options.
        """
        downloads = []
        with Path(input_file).open() as fd:
            for download_lines in self.split_input_file(fd):
                uris = download_lines[0].split("\t")
                options = {}
                try:
                    for option_line in download_lines[1:]:
                        option_name, option_value = option_line.split("=", 1)
                        options[option_name.lstrip()] = option_value
                    downloads.append((uris, options))
                except ValueError as error:
                    logger.error(f"Skipping download because of invalid option line '{option_line}'")
                    logger.opt(exception=True).trace(error)
        return downloads


class AsyncAPI:
    """A class providing high-level methods to interact with a remote aria2c process.

    This class is instantiated with a reference to a [`Client`][aria2p.client.Client] instance. It then uses this client
    to call remote procedures, or remote methods. While the client methods reflect exactly what aria2c is providing
    through JSON-RPC, this class's methods allow for easier / faster control of the remote process. It also
    wraps the information the client retrieves in Python object, like [`Download`][aria2p.downloads.Download],
    allowing for even more Pythonic interactions, without worrying about payloads, responses, JSON, etc..
    """

    def __init__(self, client: AsyncClient | None = None) -> None:
        """Initialize the object.

        Parameters:
            client: An instance of the [aria2p.client.Client][] class.
        """
        self.client = client or AsyncClient()
        self.listener: asyncio.create_task | None = None

    def __repr__(self) -> str:
        return f"API({self.client!r})"

    async def __aenter__(self) -> API:
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.session.close()
        self.client.session = None

    async def add(
        self,
        uri: str,
        options: OptionsType | None = None,
        position: int | None = None,
    ) -> list[AsyncDownload]:
        """Add a download (guess its type).

        If the provided URI is in fact a file-path, and is neither a torrent or a metalink,
        then we read its lines and try to add each line as a download, recursively.

        Parameters:
            uri: The URI or file-path to add.
            options: An instance of the [`AsyncOptions`][aria2p.options.AsyncOptions] class or a dictionary
                containing aria2c options to create the download with.
            position: The position where to insert the new download in the queue. Start at 0 (top).

        Returns:
            The created downloads.
        """
        new_downloads = []
        path = Path(uri)

        # On Windows, path.exists() generates an OSError when path is an URI
        # See https://github.com/pawamoy/aria2p/issues/41
        try:
            path_exists = path.exists()
        except OSError:
            path_exists = False

        if path_exists:
            if path.suffix == ".torrent":
                new_downloads.append(
                    await self.add_torrent(path, options=options, position=position)
                )
            elif path.suffix == ".metalink":
                new_downloads.extend(
                    await self.add_metalink(path, options=options, position=position)
                )
            else:
                for uris, download_options in self.parse_input_file(path):
                    # Add batch downloads in specified position in queue.
                    new_downloads.append(
                        (await self.add_uris(uris, options=download_options, position=position)
                    ))
                    if position is not None:
                        position += 1

        elif uri.startswith("magnet:?"):
            new_downloads.append(
                await self.add_magnet(uri, options=options, position=position)
            )
        else:
            new_downloads.append(
                await self.add_uris([uri], options=options, position=position)
            )

        return new_downloads

    async def add_magnet(
        self,
        magnet_uri: str,
        options: OptionsType | None = None,
        position: int | None = None,
    ) -> AsyncDownload:
        """Add a download with a Magnet URI.

        Parameters:
            magnet_uri: The Magnet URI.
            options: An instance of the [`AsyncOptions`][aria2p.options.AsyncOptions] class or a dictionary
                containing aria2c options to create the download with.
            position: The position where to insert the new download in the queue. Start at 0 (top).

        Returns:
            The newly created download object.
        """
        if options is None:
            options = {}

        client_options = (
            options.get_struct() if isinstance(options, AsyncOptions) else options
        )

        gid = await self.client.add_uri([magnet_uri], client_options, position)

        return await self.get_download(gid)

    async def add_torrent(
        self,
        torrent_file_path: str | Path,
        uris: list[str] | None = None,
        options: OptionsType | None = None,
        position: int | None = None,
    ) -> AsyncDownload:
        """Add a download with a torrent file (usually .torrent extension).

        Parameters:
            torrent_file_path: The path to the torrent file.
            uris: A list of URIs used for Web-seeding.
            options: An instance of the [`AsyncOptions`][aria2p.options.AsyncOptions] class or a dictionary
                containing aria2c options to create the download with.
            position: The position where to insert the new download in the queue. Start at 0 (top).

        Returns:
            The newly created download object.
        """
        if uris is None:
            uris = []

        if options is None:
            options = {}

        client_options = (
            options.get_struct() if isinstance(options, AsyncOptions) else options
        )

        with open(torrent_file_path, "rb") as stream:
            torrent_contents = stream.read()
        encoded_contents = b64encode(torrent_contents).decode("utf8")

        gid = await self.client.add_torrent(encoded_contents, uris, client_options, position)

        return await self.get_download(gid)

    async def add_metalink(
        self,
        metalink_file_path: str | Path,
        options: OptionsType | None = None,
        position: int | None = None,
    ) -> list[AsyncDownload]:
        """Add a download with a Metalink file.

        Parameters:
            metalink_file_path: The path to the Metalink file.
            options: An instance of the [`AsyncOptions`][aria2p.options.AsyncOptions] class or a dictionary
                containing aria2c options to create the download with.
            position: The position where to insert the new download in the queue. Start at 0 (top).

        Returns:
            The newly created download objects.
        """
        if options is None:
            options = {}

        client_options = (
            options.get_struct() if isinstance(options, AsyncOptions) else options
        )

        with open(metalink_file_path, "rb") as stream:
            metalink_contents = stream.read()
        encoded_contents = b64encode(metalink_contents).decode("utf8")

        gids = await self.client.add_metalink(encoded_contents, client_options, position)

        return await self.get_downloads(gids)

    async def add_uris(
        self,
        uris: list[str],
        options: OptionsType | None = None,
        position: int | None = None,
    ) -> AsyncDownload:
        """Add a download with a URL (or more).

        Parameters:
            uris: A list of URIs that point to the same resource.
            options: An instance of the `AsyncOptions` class or a dictionary
                containing aria2c options to create the download with.
            position: The position where to insert the new download in the queue. Start at 0 (top).

        Returns:
            The newly created download object.

        """
        if options is None:
            options = {}

        client_options = (
            options.get_struct() if isinstance(options, AsyncOptions) else options
        )

        gid = await self.client.add_uri(uris, client_options, position)

        return await self.get_download(gid)

    async def search(self, patterns: list[str]) -> list[AsyncDownload]:
        """Not implemented.

        Search and return [`AsyncDownload`][aria2p.downloads.AsyncDownload] objects based on multiple patterns.

        Parameters:
            patterns: The patterns used to filter the download list.

        Raises:
            NotImplementedError: This method is not implemented yet.
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

    async def get_download(self, gid: str) -> AsyncDownload:
        """Get a [`AsyncDownload`][aria2p.downloads.AsyncDownload] object thanks to its GID.

        Parameters:
            gid: The GID of the download to get.

        Returns:
            The retrieved download object.
        """
        return AsyncDownload(self, (await self.client.tell_status(gid)))

    async def get_downloads(self, gids: list[str] | None = None) -> list[AsyncDownload]:
        """Get a list of [`AsyncDownload`][aria2p.downloads.AsyncDownload] object thanks to their GIDs.

        Parameters:
            gids: The GIDs of the downloads to get. If None, return all the downloads.

        Returns:
            The retrieved download objects.
        """
        downloads = []

        if gids:
            for gid in gids:
                downloads.append(AsyncDownload(self, (await self.client.tell_status(gid))))
        else:
            structs = []
            results = await asyncio.gather(
                self.client.tell_active(),
                self.client.tell_waiting(0, 1000),
                self.client.tell_stopped(0, 1000)
            )

            structs.extend(results[0])
            structs.extend(results[1])
            structs.extend(results[2])

            downloads = [AsyncDownload(self, struct) for struct in structs]

        return downloads

    async def move(self, download: AsyncDownload, pos: int) -> int:
        """Move a download in the queue, relatively to its current position.

        Parameters:
            download: The download object to move.
            pos: The relative position (1 to move down, -1 to move up, -2 to move up two times, etc.).

        Returns:
            The new position of the download.
        """
        return await self.client.change_position(download.gid, pos, "POS_CUR")

    async def move_to(self, download: AsyncDownload, pos: int) -> int:
        """Move a download in the queue, with absolute positioning.

        Parameters:
            download: The download object to move.
            pos: The absolute position in the queue where to move the download. 0 for top, -1 for bottom.

        Returns:
            The new position of the download.
        """
        if pos < 0:
            how = "POS_END"
            pos = -pos
        else:
            how = "POS_SET"
        return await self.client.change_position(download.gid, pos, how)

    async def move_up(self, download: AsyncDownload, pos: int = 1) -> int:
        """Move a download up in the queue.

        Parameters:
            download: The download object to move.
            pos: Number of times to move up. With negative values, will move down (use move or move_down instead).

        Returns:
            The new position of the download.
        """
        return await self.client.change_position(download.gid, -pos, "POS_CUR")

    async def move_down(self, download: AsyncDownload, pos: int = 1) -> int:
        """Move a download down in the queue.

        Parameters:
            download: The download object to move.
            pos: Number of times to move down. With negative values, will move up (use move or move_up instead).

        Returns:
            The new position of the download.
        """
        return await self.client.change_position(download.gid, pos, "POS_CUR")

    async def move_to_top(self, download: AsyncDownload) -> int:
        """Move a download to the top of the queue.

        Parameters:
            download: The download object to move.

        Returns:
            The new position of the download.
        """
        return await self.client.change_position(download.gid, 0, "POS_SET")

    async def move_to_bottom(self, download: AsyncDownload) -> int:
        """Move a download to the bottom of the queue.

        Parameters:
            download: The download object to move.

        Returns:
            The new position of the download.
        """
        return await self.client.change_position(download.gid, 0, "POS_END")

    async def retry_downloads(
        self,
        downloads: list[AsyncDownload],
        clean: bool = False,  # noqa: FBT001,FBT002
    ) -> list[OperationResult]:
        """Resume failed downloads from where they left off with new GIDs.

        Parameters:
            downloads: The list of downloads to remove.
            clean: Whether to remove the aria2 control file as well.

        Returns:
            Success or failure of the operation for each given download.
        """
        result: list[OperationResult] = []

        for download in downloads:
            if not download.has_failed:
                continue
            try:
                uri = download.files[0].uris[0]["uri"]
            except IndexError:
                continue
            try:
                new_download_gid = await self.add_uris([uri], (await download.get_options()))
            except ClientException as error:
                result.append(error)
            else:
                if not new_download_gid:
                    continue

                await self.remove([download], clean=clean)
                result.append(True)

        return result

    async def remove(
        self,
        downloads: list[AsyncDownload],
        force: bool = False,  # noqa: FBT001,FBT002
        files: bool = False,  # noqa: FBT001,FBT002
        clean: bool = True,  # noqa: FBT001,FBT002
    ) -> list[OperationResult]:
        """Remove the given downloads from the list.

        Parameters:
            downloads: The list of downloads to remove.
            force: Whether to force the removal or not.
            files: Whether to remove downloads files as well.
            clean: Whether to remove the aria2 control file as well.

        Returns:
            Success or failure of the operation for each given download.
        """
        # Note: batch/multicall candidate
        remove_func = self.client.force_remove if force else self.client.remove

        result: list[OperationResult] = []

        for download in downloads:
            if download.is_complete or download.is_removed or download.has_failed:
                logger.debug(f"Try to remove download result {download.gid}")
                try:
                    await self.client.remove_download_result(download.gid)
                except ClientException as error:
                    logger.exception(error)
                    result.append(error)
                else:
                    logger.success(f"Removed download result {download.gid}")
                    result.append(True)
            else:
                logger.debug(f"Try to remove download {download.gid}")
                try:
                    removed_gid = await remove_func(download.gid)
                except ClientException as error:
                    logger.exception(error)
                    result.append(error)
                else:
                    logger.success(f"Removed download {download.gid}")
                    result.append(True)
                    try:  # (nested try)
                        await self.client.remove_download_result(download.gid)
                    except ClientException as error:
                        logger.debug(f"Failed to remove download result {download.gid}")
                        logger.opt(exception=True).trace(error)
                    if removed_gid != download.gid:
                        logger.debug(
                            f"Removed download GID#{removed_gid} is different than download GID#{download.gid}",
                        )
                        try:
                            await self.client.remove_download_result(removed_gid)
                        except ClientException as error:
                            logger.debug(
                                f"Failed to remove download result {removed_gid}"
                            )
                            logger.opt(exception=True).trace(error)

            if clean:
                download.control_file_path.unlink(missing_ok=True)
                logger.debug(f"Removed control file {download.control_file_path}")

            if files and result[-1]:
                await self.remove_files([download], force=True)

        return result

    async def remove_all(self, force: bool = False) -> bool:  # noqa: FBT001,FBT002
        """Remove all downloads from the list.

        Parameters:
            force: Whether to force the removal or not.

        Returns:
            Success or failure of the operation to remove all downloads.
        """
        return all((await self.remove((await self.get_downloads()), force=force)))

    async def pause(
        self, downloads: list[AsyncDownload], force: bool = False
    ) -> list[OperationResult]:  # noqa: FBT001,FBT002
        """Pause the given (active) downloads.

        Parameters:
            downloads: The list of downloads to pause.
            force: Whether to pause immediately without contacting servers or not.

        Returns:
            Success or failure of the operation for each given download.
        """
        # Note: batch/multicall candidate
        pause_func = self.client.force_pause if force else self.client.pause

        result: list[OperationResult] = []
        for download in downloads:
            try:
                await pause_func(download.gid)
            except ClientException as error:
                logger.debug(f"Failed to pause download {download.gid}")
                logger.opt(exception=True).trace(error)
                result.append(error)
            else:
                result.append(True)

        return result

    async def pause_all(self, force: bool = False) -> bool:  # noqa: FBT001,FBT002
        """Pause all (active) downloads.

        Parameters:
            force: Whether to pause immediately without contacting servers or not.

        Returns:
            Success or failure of the operation to pause all downloads.
        """
        pause_func = self.client.force_pause_all if force else self.client.pause_all
        return (await pause_func()) == "OK"

    async def resume(self, downloads: list[AsyncDownload]) -> list[OperationResult]:
        """Resume (unpause) the given downloads.

        Parameters:
            downloads: The list of downloads to resume.

        Returns:
            Success or failure of the operation for each given download.
        """
        # Note: batch/multicall candidate
        result: list[OperationResult] = []
        for download in downloads:
            try:
                await self.client.unpause(download.gid)
            except ClientException as error:
                logger.debug(f"Failed to resume download {download.gid}")
                logger.opt(exception=True).trace(error)
                result.append(error)
            else:
                result.append(True)

        return result

    async def resume_all(self) -> bool:
        """Resume (unpause) all downloads.

        Returns:
            Success or failure of the operation to resume all downloads.
        """
        return (await self.client.unpause_all()) == "OK"

    async def purge(self) -> bool:
        """Purge completed, removed or failed downloads from the queue.

        Returns:
            Success or failure of the operation.
        """
        return (await self.client.purge_download_result()) == "OK"

    async def autopurge(self) -> bool:
        """Purge completed, removed or failed downloads from the queue.

        Deprecated. Use [`purge`][aria2p.api.API.purge] instead.

        Returns:
            Success or failure of the operation.
        """
        logger.warning(
            "Deprecation warning: API method 'autopurge' is deprecated, use 'purge' instead."
        )
        return await self.purge()

    async def get_options(self, downloads: list[AsyncDownload]) -> list[AsyncOptions]:
        """Get options for each of the given downloads.

        Parameters:
            downloads: The list of downloads to get the options of.

        Returns:
            Options object for each given download.
        """
        # Note: batch/multicall candidate
        options = []
        for download in downloads:
            options.append(
                AsyncOptions(self, (await self.client.get_option(download.gid)), download)
            )
        return options

    async def get_global_options(self) -> AsyncOptions:
        """Get the global options.

        Returns:
            The global aria2c options.
        """
        return AsyncOptions(self, (await self.client.get_global_option()))

    async def set_options(
        self, options: OptionsType, downloads: list[AsyncDownload]
    ) -> list[bool]:
        """Set options for specific downloads.

        Parameters:
            options: An instance of the [`AsyncOptions`][aria2p.options.AsyncOptions] class or a dictionary
                containing aria2c options to create the download with.
            downloads: The list of downloads to set the options for.

        Returns:
            Success or failure of the operation for changing options for each given download.
        """
        client_options = (
            options.get_struct() if isinstance(options, AsyncOptions) else options
        )

        # Note: batch/multicall candidate
        results = []
        for download in downloads:
            results.append(
                (await self.client.change_option(download.gid, client_options)) == "OK"
            )
        return results

    async def set_global_options(self, options: OptionsType) -> bool:
        """Set global options.

        Parameters:
            options: An instance of the [`AsyncOptions`][aria2p.options.AsyncOptions] class or a dictionary
                containing aria2c options to create the download with.

        Returns:
            Success or failure of the operation for changing global options.
        """
        client_options = (
            options.get_struct() if isinstance(options, AsyncOptions) else options
        )

        return (await self.client.change_global_option(client_options)) == "OK"

    async def get_stats(self) -> Stats:
        """Get the stats of the remote aria2c process.

        Returns:
            The global stats returned by the remote process.
        """
        return Stats((await self.client.get_global_stat()))

    @staticmethod
    async def remove_files(
        downloads: list[AsyncDownload],
        force: bool = False,  # noqa: FBT001,FBT002
    ) -> list[bool]:
        """Remove downloaded files.

        Parameters:
            downloads:  the list of downloads for which to remove files.
            force: Whether to remove files even if download is not complete.

        Returns:
            Success or failure of the operation for each given download.
        """
        results = []
        for download in downloads:
            if download.is_complete or force:
                for path in download.root_files_paths:
                    if path.is_dir():
                        try:
                            await aioshutil.rmtree(str(path))
                        except OSError as error:
                            logger.error(f"Could not delete directory '{path}'")
                            logger.opt(exception=True).trace(error)
                            results.append(False)
                        else:
                            results.append(True)
                    else:
                        try:
                            path.unlink()
                        except FileNotFoundError as error:
                            logger.warning(
                                f"File '{path}' did not exist when trying to delete it"
                            )
                            logger.opt(exception=True).trace(error)
                        results.append(True)
            else:
                results.append(False)
        return results

    @staticmethod
    async def move_files(
        downloads: list[AsyncDownload],
        to_directory: str | Path,
        force: bool = False,  # noqa: FBT001,FBT002
    ) -> list[bool]:
        """Move downloaded files to another directory.

        Parameters:
            downloads:  the list of downloads for which to move files.
            to_directory: The target directory to move files to.
            force: Whether to move files even if download is not complete.

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
                    await aioshutil.move(str(path), str(to_directory))
                results.append(True)
            else:
                results.append(False)
        return results

    @staticmethod
    async def copy_files(
        downloads: list[AsyncDownload],
        to_directory: str | Path,
        force: bool = False,  # noqa: FBT001,FBT002
    ) -> list[bool]:
        """Copy downloaded files to another directory.

        Parameters:
            downloads:  the list of downloads for which to move files.
            to_directory: The target directory to copy files into.
            force: Whether to move files even if download is not complete.

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
                        await aioshutil.copytree(str(path), str(to_directory / path.name))
                    elif path.is_file():
                        await aioshutil.copy(str(path), str(to_directory))

                results.append(True)
            else:
                results.append(False)
        return results

    async def listen_to_notifications(
        self,
        block: bool = True,  # noqa: FBT001,FBT002
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

        This method differs from [`Client.listen_to_notifications`][aria2p.client.Client.listen_to_notifications]
        in that it expects callbacks accepting two arguments, `api` and `gid`, instead of only `gid`.
        Accepting `api` allows to use the high-level methods of the [`API`][aria2p.api.API] class.

        Stop listening to notifications with the [`API.stop_listening`][aria2p.api.API.stop_listening] method.

        Parameters:
            block: Whether to start the listening loop in a new task or not (block execute).
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

        def closure(callback: Coroutine | None) -> Coroutine | None:
            return (
                functools.partial(callback, self)
                if iscoroutinefunction(callback)
                else None
            )

        kwargs = {
            "on_download_start": closure(on_download_start),
            "on_download_pause": closure(on_download_pause),
            "on_download_stop": closure(on_download_stop),
            "on_download_complete": closure(on_download_complete),
            "on_download_error": closure(on_download_error),
            "on_bt_download_complete": closure(on_bt_download_complete),
            "timeout": timeout,
            "handle_signals": handle_signals,
        }

        if not block:
            kwargs["handle_signals"] = False
            loop = asyncio.get_event_loop()
            self.listener = loop.create_task(self.client.listen_to_notifications(**kwargs))
        else:
            await self.client.listen_to_notifications(**kwargs)  # type: ignore[arg-type]

    async def stop_listening(self) -> None:
        """Stop listening to notifications.

        If the listening loop was threaded, this method will wait for the thread to finish.
        The time it takes for the thread to finish will depend on the timeout given while calling
        [`listen_to_notifications`][aria2p.api.API.listen_to_notifications].
        """
        self.client.stop_listening()
        if self.listener:
            self.listener.cancel()
        self.listener = None

    def split_input_file(self, lines: list[str] | TextIO) -> Iterator[list[str]]:
        """Helper to split downloads in an input file.

        Parameters:
             lines: The lines of the input file.

        Yields:
            list[str]: Blocks of lines.
        """
        block: list[str] = []
        for line in lines:
            if line.lstrip().startswith("#"):  # Ignore Comments
                continue
            if not line.strip():  # Ignore empty line
                continue
            if not line.startswith(" ") and block:  # URIs line
                yield block
                block = []
            block.append(line.rstrip("\n"))
        if block:
            yield block

    def parse_input_file(self, input_file: str | Path) -> InputFileContentsType:
        """Parse a file with URIs or an aria2c input file.

        Parameters:
            input_file: Path to file with URIs or aria2c input file.

        Returns:
            List of tuples containing list of URIs and dictionary with aria2c options.
        """
        downloads = []
        with Path(input_file).open() as fd:
            for download_lines in self.split_input_file(fd):
                uris = download_lines[0].split("\t")
                options = {}
                try:
                    for option_line in download_lines[1:]:
                        option_name, option_value = option_line.split("=", 1)
                        options[option_name.lstrip()] = option_value
                    downloads.append((uris, options))
                except ValueError as error:
                    logger.error(
                        f"Skipping download because of invalid option line '{option_line}'"
                    )
                    logger.opt(exception=True).trace(error)
        return downloads
