"""This module defines the BitTorrent, File and Download classes.

They respectively hold structured information about
torrent files, files and downloads in aria2c.
"""

from __future__ import annotations

from contextlib import suppress
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import TYPE_CHECKING

from loguru import logger

from aria2p.client import ClientException
from aria2p.utils import bool_or_value, human_readable_bytes, human_readable_timedelta

if TYPE_CHECKING:
    from aria2p.api import API
    from aria2p.options import Options


class BitTorrent:
    """Information retrieved from a torrent file."""

    def __init__(self, struct: dict) -> None:
        """Initialize the object.

        Parameters:
            struct: A dictionary Python object returned by the JSON-RPC client.
        """
        self._struct = struct or {}

    def __str__(self):
        return self.info["name"]

    @property
    def announce_list(self) -> list[list[str]] | None:
        """List of lists of announce URIs.

        If the torrent contains announce and no announce-list, announce is converted to the announce-list format.

        Returns:
            The announce URIs.
        """
        return self._struct.get("announceList")

    @property
    def comment(self) -> str | None:
        """Return the comment of the torrent.

        comment.utf-8 is used if available.

        Returns:
            The torrent's comment.
        """
        return self._struct.get("comment")

    @property
    def creation_date(self) -> datetime:
        """Return the creation time of the torrent.

        The value is an integer since the epoch, measured in seconds.

        Returns:
            The creation date.
        """
        return datetime.fromtimestamp(self._struct["creationDate"], tz=timezone.utc)

    @property
    def mode(self) -> str | None:
        """File mode of the torrent.

        The value is either single or multi.

        Returns:
            The file mode.
        """
        return self._struct.get("mode")

    @property
    def info(self) -> dict | None:
        """Struct which contains data from Info dictionary.

        It contains the `name` key: name in info dictionary. `name.utf-8` is used if available.

        Returns:
            The torrent's info.
        """
        return self._struct.get("info")


class File:
    """Information about a download's file."""

    def __init__(self, struct: dict) -> None:
        """Initialize the object.

        Parameters:
            struct: A dictionary Python object returned by the JSON-RPC client.
        """
        self._struct = struct or {}

    def __str__(self):
        return str(self.path)

    def __eq__(self, other: object) -> bool:
        if isinstance(other, File):
            return self.path == other.path
        return NotImplemented

    @property
    def index(self) -> int:
        """Index of the file, starting at 1, in the same order as files appear in the multi-file torrent.

        Returns:
            The index of the file.
        """
        return int(self._struct["index"])

    @property
    def path(self) -> Path:
        """File path.

        Returns:
            The file path.
        """
        return Path(self._struct["path"])

    @property
    def is_metadata(self) -> bool:
        """Return True if this file is aria2 metadata and not an actual file.

        Returns:
            If the file is metadata.
        """
        return str(self.path).startswith("[METADATA]")

    @property
    def length(self) -> int:
        """Return the file size in bytes.

        Returns:
            The file size in bytes.
        """
        return int(self._struct["length"])

    def length_string(self, human_readable: bool = True) -> str:  # noqa: FBT001,FBT002
        """Return the length as string.

        Parameters:
            human_readable: Return in human readable format or not.

        Returns:
            The length string.
        """
        if human_readable:
            return human_readable_bytes(self.length, delim=" ")
        return str(self.length) + " B"

    @property
    def completed_length(self) -> int:
        """Completed length of this file in bytes.

        Please note that it is possible that sum of completedLength is less than the completedLength returned by the
        aria2.tellStatus() method. This is because completedLength in aria2.getFiles() only includes completed
        pieces. On the other hand, completedLength in aria2.tellStatus() also includes partially completed pieces.

        Returns:
            The completed length.
        """
        return int(self._struct["completedLength"])

    def completed_length_string(self, human_readable: bool = True) -> str:  # noqa: FBT001,FBT002
        """Return the completed length as string.

        Parameters:
            human_readable: Return in human readable format or not.

        Returns:
            The completed length string.
        """
        if human_readable:
            return human_readable_bytes(self.completed_length, delim=" ")
        return str(self.completed_length) + " B"

    @property
    def selected(self) -> bool:
        """Return True if this file is selected by [`--select-file`][aria2p.options.Options.select_file] option.

        If [`--select-file`][aria2p.options.Options.select_file] is not specified
        or this is single-file torrent or not a torrent download at all, this value is always true.
        Otherwise false.

        Returns:
            If this file is selected.
        """
        return bool_or_value(self._struct["selected"])

    @property
    def uris(self) -> list[dict]:
        """Return a list of URIs for this file.

        The element type is the same struct
        used in the [`client.get_uris()`][aria2p.client.Client.get_uris] method.

        Returns:
            The list of URIs.
        """
        return self._struct.get("uris", [])


class Download:
    """Class containing all information about a download, as retrieved with the client."""

    def __init__(self, api: API, struct: dict) -> None:
        """Initialize the object.

        Parameters:
            api: The reference to an [`API`][aria2p.api.API] instance.
            struct: A dictionary Python object returned by the JSON-RPC client.
        """
        self.api = api
        self._struct = struct or {}
        self._files: list[File] = []
        self._root_files_paths: list[Path] = []
        self._bittorrent: BitTorrent | None = None
        self._name = ""
        self._options: Options | None = None
        self._followed_by: list[Download] | None = None
        self._following: Download | None = None
        self._belongs_to: Download | None = None

    def __str__(self):
        return self.name

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Download):
            return self.gid == other.gid
        return NotImplemented

    def update(self) -> None:
        """Update the internal values of the download with more recent values."""
        self._struct = self.api.client.tell_status(self.gid)

        self._files = []
        self._name = ""
        self._bittorrent = None
        self._followed_by = None
        self._following = None
        self._belongs_to = None
        self._options = None

    @property
    def live(self) -> Download:
        """Return the same object with updated data.

        Returns:
            Itself.
        """
        self.update()
        return self

    @property
    def name(self) -> str:
        """Return the name of the download.

        Name is the name of the file if single-file, first file's directory name if multi-file.

        Returns:
            The download name.
        """
        if not self._name:
            if self.bittorrent and self.bittorrent.info:
                self._name = self.bittorrent.info["name"]
            elif self.files[0].is_metadata:
                self._name = str(self.files[0].path)
            else:
                file_path = str(self.files[0].path.absolute())
                dir_path = str(self.dir.absolute())
                if file_path.startswith(dir_path):
                    start_pos = len(dir_path) + 1
                    with suppress(IndexError):
                        self._name = Path(file_path[start_pos:]).parts[0]
                else:
                    with suppress(IndexError):
                        self._name = self.files[0].uris[0]["uri"].split("/")[-1]
        return self._name

    @property
    def control_file_path(self) -> Path:
        """Return the path to the aria2 control file for this download.

        Returns:
            The control file path.
        """
        return self.dir / (self.name + ".aria2")

    @property
    def root_files_paths(self) -> list[Path]:
        """Return the unique set of directories/files for this download.

        Instead of returning all the leaves like self.files,
        return the relative root directories if any, and relative root files.

        This property is useful when we need to list the directories and files
        in order to move or copy them. We don't want to copy files one by one,
        but rather entire directories at once when possible.

        Returns:
            The root file paths.

        Examples:
            Download directory is `/a/b`.

            >>> self.files
            ["/a/b/c/1.txt", "/a/b/c/2.txt", "/a/b/3.txt"]
            >>> self.root_files_paths
            ["/a/b/c", "/a/b/3.txt"]
        """
        if not self._root_files_paths:
            paths = []
            for file in self.files:
                if file.is_metadata:
                    continue
                try:
                    relative_path = file.path.relative_to(self.dir)
                except ValueError as error:
                    logger.warning(f"Can't determine file path '{file.path}' relative to '{self.dir}'")
                    logger.opt(exception=True).trace(error)
                else:
                    path = self.dir / relative_path.parts[0]
                    if path not in paths:
                        paths.append(path)
            self._root_files_paths = paths
        return self._root_files_paths

    @property
    def options(self) -> Options:
        """Options specific to this download.

        Returns:
            The download options.
        """
        if not self._options:
            self.update_options()
        return self._options  # type: ignore

    @options.setter
    def options(self, value: Options) -> None:
        self._options = value

    def update_options(self) -> None:
        """Re-fetch the options from the remote."""
        self._options = self.api.get_options(downloads=[self])[0]

    @property
    def gid(self) -> str:
        """GID of the download.

        Returns:
            The download GID.
        """
        return self._struct["gid"]

    @property
    def status(self) -> str:
        """Return the status of the download.

        Returns:
            `active`, `waiting`, `paused`, `error`, `complete` or `removed`.
        """
        return self._struct["status"]

    @property
    def is_active(self) -> bool:
        """Return True if download is active.

        Returns:
            If this download is active.
        """
        return self.status == "active"

    @property
    def is_waiting(self) -> bool:
        """Return True if download is waiting.

        Returns:
            If this download is waiting.
        """
        return self.status == "waiting"

    @property
    def is_paused(self) -> bool:
        """Return True if download is paused.

        Returns:
            If this download is paused.
        """
        return self.status == "paused"

    @property
    def has_failed(self) -> bool:
        """Return True if download has errored.

        Returns:
            If this download has failed.
        """
        return self.status == "error"

    @property
    def is_complete(self) -> bool:
        """Return True if download is complete.

        Returns:
            If this download is complete.
        """
        return self.status == "complete"

    @property
    def is_removed(self) -> bool:
        """Return True if download was removed.

        Returns:
            If this download was removed.
        """
        return self.status == "removed"

    @property
    def is_metadata(self) -> bool:
        """Return True if this download is only composed of metadata, and no actual files.

        Returns:
            If this is a metadata download.
        """
        return all(_.is_metadata for _ in self.files)

    @property
    def is_torrent(self) -> bool:
        """Return true if this download is a torrent.

        Returns:
            If this is a torrent downlaod.
        """
        return "bittorrent" in self._struct

    @property
    def total_length(self) -> int:
        """Total length of the download in bytes.

        Returns:
            The total length in bytes.
        """
        return int(self._struct["totalLength"])

    def total_length_string(self, human_readable: bool = True) -> str:  # noqa: FBT001,FBT002
        """Return the total length as string.

        Parameters:
            human_readable: Return in human readable format or not.

        Returns:
            The total length string.
        """
        if human_readable:
            return human_readable_bytes(self.total_length, delim=" ")
        return str(self.total_length) + " B"

    @property
    def completed_length(self) -> int:
        """Completed length of the download in bytes.

        Returns:
            The completed length in bytes.
        """
        return int(self._struct["completedLength"])

    def completed_length_string(self, human_readable: bool = True) -> str:  # noqa: FBT001,FBT002
        """Return the completed length as string.

        Parameters:
            human_readable: Return in human readable format or not.

        Returns:
            The completed length string.
        """
        if human_readable:
            return human_readable_bytes(self.completed_length, delim=" ")
        return str(self.completed_length) + " B"

    @property
    def upload_length(self) -> int:
        """Return the uploaded length of the download in bytes.

        Returns:
            The uploaded length in bytes.
        """
        return int(self._struct["uploadLength"])

    def upload_length_string(self, human_readable: bool = True) -> str:  # noqa: FBT001,FBT002
        """Return the upload length as string.

        Parameters:
            human_readable: Return in human readable format or not.

        Returns:
            The upload length string.
        """
        if human_readable:
            return human_readable_bytes(self.upload_length, delim=" ")
        return str(self.upload_length) + " B"

    @property
    def bitfield(self) -> str | None:
        """Hexadecimal representation of the download progress.

        The highest bit corresponds to the piece at index 0. Any set bits indicate loaded pieces, while unset bits
        indicate not yet loaded and/or missing pieces. Any overflow bits at the end are set to zero. When the
        download was not started yet, this key will not be included in the response.

        Returns:
            The hexadecimal representation of the download progress.
        """
        return self._struct.get("bitfield")

    @property
    def download_speed(self) -> int:
        """Download speed of this download measured in bytes/sec.

        Returns:
            The download speed in bytes/sec.
        """
        return int(self._struct["downloadSpeed"])

    def download_speed_string(self, human_readable: bool = True) -> str:  # noqa: FBT001,FBT002
        """Return the download speed as string.

        Parameters:
            human_readable: Return in human readable format or not.

        Returns:
            The download speed string.
        """
        if human_readable:
            return human_readable_bytes(self.download_speed, delim=" ", postfix="/s")
        return str(self.download_speed) + " B/s"

    @property
    def upload_speed(self) -> int:
        """Upload speed of this download measured in bytes/sec.

        Returns:
            The upload speed in bytes/sec.
        """
        return int(self._struct["uploadSpeed"])

    def upload_speed_string(self, human_readable: bool = True) -> str:  # noqa: FBT001,FBT002
        """Return the upload speed as string.

        Parameters:
            human_readable: Return in human readable format or not.

        Returns:
            The upload speed string.
        """
        if human_readable:
            return human_readable_bytes(self.upload_speed, delim=" ", postfix="/s")
        return str(self.upload_speed) + " B/s"

    @property
    def info_hash(self) -> str | None:
        """Return the InfoHash.

        BitTorrent only.

        Returns:
            The InfoHash.
        """
        return self._struct.get("infoHash")

    @property
    def num_seeders(self) -> int:
        """Return the number of seeders aria2 has connected to.

        BitTorrent only.

        Returns:
            The numbers of seeders.
        """
        return int(self._struct["numSeeders"])

    @property
    def seeder(self) -> bool:
        """Return True if the local endpoint is a seeder, otherwise false.

        BitTorrent only.

        Returns:
            If the local endpoint is a seeder.
        """
        return bool_or_value(self._struct.get("seeder"))

    @property
    def piece_length(self) -> int:
        """Piece length in bytes.

        Returns:
            The piece length in bytes.
        """
        return int(self._struct["pieceLength"])

    def piece_length_string(self, human_readable: bool = True) -> str:  # noqa: FBT001,FBT002
        """Return the piece length as string.

        Parameters:
            human_readable: Return in human readable format or not.

        Returns:
            The piece length string.
        """
        if human_readable:
            return human_readable_bytes(self.piece_length, delim=" ")
        return str(self.piece_length) + " B"

    @property
    def num_pieces(self) -> int:
        """Return the number of pieces.

        Returns:
            The number of pieces.
        """
        return int(self._struct["numPieces"])

    @property
    def connections(self) -> int:
        """Return the number of peers/servers aria2 has connected to.

        Returns:
            The number of connected peers/servers.
        """
        return int(self._struct["connections"])

    @property
    def error_code(self) -> str | None:
        """Return the code of the last error for this item, if any.

        The value is a string. The error codes are defined in the EXIT STATUS section. This value is only available
        for stopped/completed downloads.

        Returns:
            The error code.
        """
        return self._struct.get("errorCode")

    @property
    def error_message(self) -> str | None:
        """Return the (hopefully) human readable error message associated to errorCode.

        Returns:
            The error message.
        """
        return self._struct.get("errorMessage")

    @property
    def followed_by_ids(self) -> list[str]:
        """List of GIDs which are generated as the result of this download.

        For example, when aria2 downloads a Metalink file, it generates downloads described in the Metalink (see the
        --follow-metalink option). This value is useful to track auto-generated downloads. If there are no such
        downloads, this key will not be included in the response.

        Returns:
            The children downloads IDs.
        """
        return self._struct.get("followedBy", [])

    @property
    def followed_by(self) -> list[Download]:
        """List of downloads generated as the result of this download.

        Returns:
            A list of instances of [`Download`][aria2p.downloads.Download].
        """
        if self._followed_by is None:
            result = []
            for gid in self.followed_by_ids:
                try:
                    result.append(self.api.get_download(gid))
                except ClientException as error:
                    logger.warning(
                        f"Can't find download with GID {gid}, try to update download {self.gid} ({id(self)}",
                    )
                    logger.opt(exception=True).trace(error)
            self._followed_by = result
        return self._followed_by

    @property
    def following_id(self) -> str | None:
        """Return the reverse link for followedBy.

        A download included in followedBy has this object's GID in its following value.

        Returns:
            The parent download ID.
        """
        return self._struct.get("following")

    @property
    def following(self) -> Download | None:
        """Return the download this download is following.

        Returns:
            An instance of [`Download`][aria2p.downloads.Download].
        """
        if not self._following:
            following_id = self.following_id
            if following_id:
                try:
                    self._following = self.api.get_download(following_id)
                except ClientException as error:
                    logger.warning(
                        f"Can't find download with GID {following_id}, try to update download {self.gid} ({id(self)}",
                    )
                    logger.opt(exception=True).trace(error)
                    self._following = None
        return self._following

    @property
    def belongs_to_id(self) -> str | None:
        """GID of a parent download.

        Some downloads are a part of another download. For example, if a file in a Metalink has BitTorrent resources,
        The downloads of ".torrent" files are parts of that parent. If this download has no parent, this key will not
        be included in the response.

        Returns:
            The GID of the parent download.
        """
        return self._struct.get("belongsTo")

    @property
    def belongs_to(self) -> Download | None:
        """Parent download.

        Returns:
            An instance of [`Download`][aria2p.downloads.Download].
        """
        if not self._belongs_to:
            belongs_to_id = self.belongs_to_id
            if belongs_to_id:
                try:
                    self._belongs_to = self.api.get_download(belongs_to_id)
                except ClientException as error:
                    logger.warning(
                        f"Can't find download with GID {belongs_to_id}, try to update download {self.gid} ({id(self)})",
                    )
                    logger.opt(exception=True).trace(error)
                    self._belongs_to = None
        return self._belongs_to

    @property
    def dir(self) -> Path:  # noqa: A003
        """Directory to save files.

        Returns:
            The directory where the files are saved.
        """
        return Path(self._struct["dir"])

    @property
    def files(self) -> list[File]:
        """Return the list of files.

        The elements of this list are the same structs used in aria2.getFiles() method.

        Returns:
            The files of this download.
        """
        if not self._files:
            self._files = [File(struct) for struct in self._struct.get("files", [])]
        return self._files

    @property
    def bittorrent(self) -> BitTorrent | None:
        """Struct which contains information retrieved from the .torrent (file).

        BitTorrent only.

        Returns:
            A [BitTorrent][aria2p.downloads.BitTorrent] instance or `None`.
        """
        if not self._bittorrent and "bittorrent" in self._struct:
            self._bittorrent = BitTorrent(self._struct.get("bittorrent", {}))
        return self._bittorrent

    @property
    def verified_length(self) -> int:
        """Return the number of verified number of bytes while the files are being hash checked.

        This key exists only when this download is being hash checked.

        Returns:
            The verified length.
        """
        return int(self._struct.get("verifiedLength", 0))

    def verified_length_string(self, human_readable: bool = True) -> str:  # noqa: FBT001,FBT002
        """Return the verified length as string.

        Parameters:
            human_readable: Return in human readable format or not.

        Returns:
            The verified length string.
        """
        if human_readable:
            return human_readable_bytes(self.verified_length, delim=" ")
        return str(self.verified_length) + " B"

    @property
    def verify_integrity_pending(self) -> bool | None:
        """Return True if this download is waiting for the hash check in a queue.

        This key exists only when this download is in the queue.

        Returns:
            Whether this download is waiting for the hash check.
        """
        return bool_or_value(self._struct.get("verifyIntegrityPending"))

    @property
    def progress(self) -> float:
        """Return the progress of the download as float.

        Returns:
            Progress percentage.
        """
        try:
            return self.completed_length / self.total_length * 100
        except ZeroDivisionError:
            return 0.0

    def progress_string(self, digits: int = 2) -> str:
        """Return the progress percentage as string.

        Parameters:
            digits: Number of decimal digits to use.

        Returns:
            The progress percentage.
        """
        return f"{self.progress:.{digits}f}%"

    @property
    def eta(self) -> timedelta:
        """Return the Estimated Time of Arrival (a timedelta).

        Returns:
            ETA or `timedelta.max` if unknown.
        """
        try:
            return timedelta(seconds=int((self.total_length - self.completed_length) / self.download_speed))
        except ZeroDivisionError:
            return timedelta.max

    def eta_string(self, precision: int = 0) -> str:
        """Return the Estimated Time of Arrival as a string.

        Parameters:
            precision: The precision to use, see [aria2p.utils.human_readable_timedelta].

        Returns:
            The Estimated Time of Arrival as a string.
        """
        eta = self.eta

        if eta == timedelta.max:
            return "-"

        return human_readable_timedelta(eta, precision=precision)

    def move(self, pos: int) -> int:
        """Move the download in the queue, relatively.

        Parameters:
            pos: Number of times to move.

        Returns:
            The new position of the download.
        """
        return self.api.move(self, pos)

    def move_to(self, pos: int) -> int:
        """Move the download in the queue, absolutely.

        Parameters:
            pos: The absolute position in the queue to take.

        Returns:
            The new position of the download.
        """
        return self.api.move_to(self, pos)

    def move_up(self, pos: int = 1) -> int:
        """Move the download up in the queue.

        Parameters:
            pos: Number of times to move up.

        Returns:
            The new position of the download.
        """
        return self.api.move_up(self, pos)

    def move_down(self, pos: int = 1) -> int:
        """Move the download down in the queue.

        Parameters:
            pos: Number of times to move down.

        Returns:
            The new position of the download.
        """
        return self.api.move_down(self, pos)

    def move_to_top(self) -> int:
        """Move the download to the top of the queue.

        Returns:
            The new position of the download.
        """
        return self.api.move_to_top(self)

    def move_to_bottom(self) -> int:
        """Move the download to the bottom of the queue.

        Returns:
            The new position of the download.
        """
        return self.api.move_to_bottom(self)

    def remove(self, force: bool = False, files: bool = False) -> bool:  # noqa: FBT001,FBT002
        """Remove the download from the queue (even if active).

        Parameters:
            force: Whether to force removal.
            files: Whether to remove files as well.

        Returns:
            Always True (raises exception otherwise).

        Raises:
            ClientException: When removal failed.
        """
        result = self.api.remove([self], force=force, files=files)[0]
        if not result:
            raise result  # type: ignore  # we know it's a ClientException
        return True

    def pause(self, force: bool = False) -> bool:  # noqa: FBT001,FBT002
        """Pause the download.

        Parameters:
            force: Whether to force pause (don't contact servers).

        Returns:
            Always True (raises exception otherwise).

        Raises:
            ClientException: When pausing failed.
        """
        result = self.api.pause([self], force=force)[0]
        if not result:
            raise result  # type: ignore  # we know it's a ClientException
        return True

    def resume(self) -> bool:
        """Resume the download.

        Returns:
            Always True (raises exception otherwise).

        Raises:
            ClientException: When resuming failed.
        """
        result = self.api.resume([self])[0]
        if not result:
            raise result  # type: ignore  # we know it's a ClientException
        return True

    def purge(self) -> bool:
        """Purge itself from the results.

        Returns:
            Success or failure of the operation.
        """
        return self.api.client.remove_download_result(self.gid) == "OK"

    def move_files(self, to_directory: str | Path, force: bool = False) -> bool:  # noqa: FBT001,FBT002
        """Move downloaded files to another directory.

        Parameters:
            to_directory: The target directory to move files to.
            force: Whether to move files even if download is not complete.

        Returns:
            Success or failure of the operation.
        """
        return self.api.move_files([self], to_directory, force)[0]

    def copy_files(self, to_directory: str | Path, force: bool = False) -> bool:  # noqa: FBT001,FBT002
        """Copy downloaded files to another directory.

        Parameters:
            to_directory: The target directory to copy files into.
            force: Whether to move files even if download is not complete.

        Returns:
            Success or failure of the operation.
        """
        return self.api.copy_files([self], to_directory, force)[0]
