"""
This module defines the BitTorrent, File and Download classes, which respectively hold structured information about
torrent files, files and downloads in aria2c.
"""
from datetime import datetime, timedelta
from pathlib import Path

from .client import ClientException
from .utils import bool_or_value, human_readable_bytes, human_readable_timedelta


class BitTorrent:
    """Information retrieved from a .torrent file."""

    def __init__(self, struct):
        """
        Initialization method.

        Args:
            struct (dict): a dictionary Python object returned by the JSON-RPC client.
        """
        self._struct = struct

    def __str__(self):
        return self.info["name"]

    @property
    def announce_list(self):
        """
        List of lists of announce URIs.

        If the torrent contains announce and no announce-list, announce is converted to the announce-list format.
        """
        return self._struct.get("announceList")

    @property
    def comment(self):
        """
        The comment of the torrent.

        comment.utf-8 is used if available.
        """
        return self._struct.get("comment")

    @property
    def creation_date(self):
        """
        The creation time of the torrent.

        The value is an integer since the epoch, measured in seconds.
        """
        return datetime.fromtimestamp(self._struct.get("creationDate"))

    @property
    def mode(self):
        """
        File mode of the torrent.

        The value is either single or multi.
        """
        return self._struct.get("mode")

    @property
    def info(self):
        """
        Struct which contains data from Info dictionary.

        It contains following keys:
            name   name in info dictionary. name.utf-8 is used if available.
        """
        return self._struct.get("info")


class File:
    """Information about a download's file."""

    def __init__(self, struct):
        """
        Initialization method.

        Args:
            struct (dict): a dictionary Python object returned by the JSON-RPC client.
        """
        self._struct = struct

    def __str__(self):
        return str(self.path)

    def __eq__(self, other):
        return self.path == other.path

    @property
    def index(self):
        """Index of the file, starting at 1, in the same order as files appear in the multi-file torrent."""
        return int(self._struct.get("index"))

    @property
    def path(self):
        """File path."""
        return Path(self._struct.get("path"))

    @property
    def length(self):
        """File size in bytes."""
        return int(self._struct.get("length"))

    def length_string(self, human_readable=True):
        if human_readable:
            return human_readable_bytes(self.length, delim=" ")
        return str(self.length) + " B"

    @property
    def completed_length(self):
        """
        Completed length of this file in bytes.

        Please note that it is possible that sum of completedLength is less than the completedLength returned by the
        aria2.tellStatus() method. This is because completedLength in aria2.getFiles() only includes completed
        pieces. On the other hand, completedLength in aria2.tellStatus() also includes partially completed pieces.
        """
        return int(self._struct.get("completedLength"))

    def completed_length_string(self, human_readable=True):
        if human_readable:
            return human_readable_bytes(self.completed_length, delim=" ")
        return str(self.completed_length) + " B"

    @property
    def selected(self):
        """
        True if this file is selected by --select-file option.

        If --select-file is not specified or this is single-file torrent or not a torrent download at all, this value
        is always true. Otherwise false.
        """
        return bool_or_value(self._struct.get("selected"))

    @property
    def uris(self):
        """
        Return a list of URIs for this file.

        The element type is the same struct used in the aria2.getUris() method.
        """
        return self._struct.get("uris")


class Download:
    """Class containing all information about a download, as retrieved with the client."""

    def __init__(self, api, struct):
        """
        Initialization method.

        Args:
            api (:class:`aria2p.API`): the reference to an :class:`aria2p.API` instance.
            struct (dict): a dictionary Python object returned by the JSON-RPC client.
        """
        self.api = api
        self._struct = struct
        self._files = []
        self._bittorrent = None
        self._name = ""
        self._options = None
        self._followed_by = None
        self._following = None
        self._belongs_to = None

    def __str__(self):
        return self.name

    def __eq__(self, other):
        return self.gid == other.gid

    def update(self):
        """Method to update the internal values of the download with more recent values."""
        self._struct = self.api.client.tell_status(self.gid)

        self._files = []
        self._name = None
        self._bittorrent = None
        self._followed_by = []
        self._following = None
        self._belongs_to = None

    @property
    def name(self):
        """
        The name of the download.

        Name is the name of the file if single-file, first file's directory name if multi-file.
        """
        if not self._name:
            self._name = str(self.files[0].path).replace(str(self.dir), "").lstrip("/").split("/")[0]
        return self._name

    @property
    def options(self):
        """
        Options specific to this download.

        The returned object is an instance of :class:`aria2p.Options`.
        """
        if not self._options:
            self.update_options()
        return self._options

    @options.setter
    def options(self, value):
        self._options = value

    def update_options(self):
        self._options = self.api.get_options(downloads=[self])[0]

    @property
    def gid(self):
        """GID of the download."""
        return self._struct.get("gid")

    @property
    def status(self):
        """Status of the download: active, waiting, paused, error, complete or removed."""
        return self._struct.get("status")

    @property
    def is_active(self):
        return self.status == "active"

    @property
    def is_waiting(self):
        return self.status == "waiting"

    @property
    def is_paused(self):
        return self.status == "paused"

    @property
    def has_failed(self):
        return self.status == "error"

    @property
    def is_complete(self):
        return self.status == "complete"

    @property
    def is_removed(self):
        return self.status == "removed"

    @property
    def total_length(self):
        """Total length of the download in bytes."""
        return int(self._struct.get("totalLength"))

    def total_length_string(self, human_readable=True):
        if human_readable:
            return human_readable_bytes(self.total_length, delim=" ")
        return str(self.total_length) + " B"

    @property
    def completed_length(self):
        """Completed length of the download in bytes."""
        return int(self._struct.get("completedLength"))

    def completed_length_string(self, human_readable=True):
        if human_readable:
            return human_readable_bytes(self.completed_length, delim=" ")
        return str(self.completed_length) + " B"

    @property
    def upload_length(self):
        """Uploaded length of the download in bytes."""
        return int(self._struct.get("uploadLength"))

    def upload_length_string(self, human_readable=True):
        if human_readable:
            return human_readable_bytes(self.upload_length, delim=" ")
        return str(self.upload_length) + " B"

    @property
    def bitfield(self):
        """
        Hexadecimal representation of the download progress.

        The highest bit corresponds to the piece at index 0. Any set bits indicate loaded pieces, while unset bits
        indicate not yet loaded and/or missing pieces. Any overflow bits at the end are set to zero. When the
        download was not started yet, this key will not be included in the response.
        """
        return self._struct.get("bitfield")

    @property
    def download_speed(self):
        """Download speed of this download measured in bytes/sec."""
        return int(self._struct.get("downloadSpeed"))

    def download_speed_string(self, human_readable=True):
        if human_readable:
            return human_readable_bytes(self.download_speed, delim=" ", postfix="/s")
        return str(self.download_speed) + " B/s"

    @property
    def upload_speed(self):
        """Upload speed of this download measured in bytes/sec."""
        return int(self._struct.get("uploadSpeed"))

    def upload_speed_string(self, human_readable=True):
        if human_readable:
            return human_readable_bytes(self.upload_speed, delim=" ", postfix="/s")
        return str(self.upload_speed) + " B/s"

    @property
    def info_hash(self):
        """
        InfoHash.

        BitTorrent only.
        """
        return self._struct.get("infoHash")

    @property
    def num_seeders(self):
        """
        The number of seeders aria2 has connected to.

        BitTorrent only.
        """
        return int(self._struct.get("numSeeders"))

    @property
    def seeder(self):
        """
        True if the local endpoint is a seeder, otherwise false.

        BitTorrent only.
        """
        return bool_or_value(self._struct.get("seeder"))

    @property
    def piece_length(self):
        """Piece length in bytes."""
        return int(self._struct.get("pieceLength"))

    def piece_length_string(self, human_readable=True):
        if human_readable:
            return human_readable_bytes(self.piece_length, delim=" ")
        return str(self.piece_length) + " B"

    @property
    def num_pieces(self):
        """The number of pieces."""
        return int(self._struct.get("numPieces"))

    @property
    def connections(self):
        """The number of peers/servers aria2 has connected to."""
        return int(self._struct.get("connections"))

    @property
    def error_code(self):
        """
        The code of the last error for this item, if any.

        The value is a string. The error codes are defined in the EXIT STATUS section. This value is only available
        for stopped/completed downloads.
        """
        return self._struct.get("errorCode")

    @property
    def error_message(self):
        """The (hopefully) human readable error message associated to errorCode."""
        return self._struct.get("errorMessage")

    @property
    def followed_by_ids(self):
        """
        List of GIDs which are generated as the result of this download.

        For example, when aria2 downloads a Metalink file, it generates downloads described in the Metalink (see the
        --follow-metalink option). This value is useful to track auto-generated downloads. If there are no such
        downloads, this key will not be included in the response.
        """
        return self._struct.get("followedBy", [])

    @property
    def followed_by(self):
        """
        List of downloads generated as the result of this download.

        Returns a list of instances of :class:`aria2p.Download`.
        """
        if self._followed_by is None:
            result = []
            for gid in self.followed_by_ids:
                try:
                    result.append(self.api.get_download(gid))
                except ClientException:
                    pass
            self._followed_by = result
        return self._followed_by

    @property
    def following_id(self):
        """
        The reverse link for followedBy.

        A download included in followedBy has this object's GID in its following value.
        """
        return self._struct.get("following")

    @property
    def following(self):
        """
        The download this download is following.

        Returns an instance of :class:`aria2p.Download`.
        """
        if not self._following:
            try:
                self._following = self.api.get_download(self.following_id)
            except ClientException:
                return None
        return self._following

    @property
    def belongs_to_id(self):
        """
        GID of a parent download.

        Some downloads are a part of another download. For example, if a file in a Metalink has BitTorrent resources,
        The downloads of ".torrent" files are parts of that parent. If this download has no parent, this key will not
        be included in the response.
        """
        return self._struct.get("belongsTo")

    @property
    def belongs_to(self):
        """
        Parent download.

        Returns an instance of :class:`aria2p.Download`.
        """
        if not self._belongs_to:
            try:
                self._belongs_to = self.api.get_download(self.belongs_to_id)
            except ClientException:
                return None
        return self._belongs_to

    @property
    def dir(self):
        """Directory to save files."""
        return Path(self._struct.get("dir"))

    @property
    def files(self):
        """
        Return the list of files.

        The elements of this list are the same structs used in aria2.getFiles() method.
        """
        if not self._files:
            self._files = [File(s) for s in self._struct.get("files")]
        return self._files

    @property
    def bittorrent(self):
        """
        Struct which contains information retrieved from the .torrent (file).

        BitTorrent only.
        """
        if not self._bittorrent:
            self._bittorrent = BitTorrent(self._struct.get("bittorrent"))
        return self._bittorrent

    @property
    def verified_length(self):
        """
        The number of verified number of bytes while the files are being hash checked.

        This key exists only when this download is being hash checked.
        """
        return int(self._struct.get("verifiedLength", 0))

    def verified_length_string(self, human_readable=True):
        if human_readable:
            return human_readable_bytes(self.verified_length, delim=" ")
        return str(self.verified_length) + " B"

    @property
    def verify_integrity_pending(self):
        """
        True if this download is waiting for the hash check in a queue.

        This key exists only when this download is in the queue.
        """
        return bool_or_value(self._struct.get("verifyIntegrityPending"))

    @property
    def progress(self):
        """Return the progress of the download as float."""
        try:
            return self.completed_length / self.total_length * 100
        except ZeroDivisionError:
            return 0.0

    def progress_string(self, digits=2):
        return f"{self.progress:.{digits}f}%"

    @property
    def eta(self):
        try:
            return timedelta(seconds=int((self.total_length - self.completed_length) / self.download_speed))
        except ZeroDivisionError:
            return float("Inf")

    def eta_string(self):
        eta = self.eta

        if eta == float("Inf"):
            return "-"

        return human_readable_timedelta(eta)

    def move(self, pos):
        return self.api.move(self, pos)

    def move_to(self, pos):
        return self.api.move_to(self, pos)

    def move_up(self, pos=1):
        return self.api.move_up(self, -pos)

    def move_down(self, pos=1):
        return self.api.move_down(self, pos)

    def move_to_top(self):
        return self.api.move_to_top(self)

    def move_to_bottom(self):
        return self.api.move_to_bottom(self)

    def remove(self):
        result = self.api.remove([self])[0]
        if not result:
            raise result
        return result

    def pause(self):
        result = self.api.pause([self])[0]
        if not result:
            raise result
        return result

    def resume(self):
        result = self.api.resume([self])[0]
        if not result:
            raise result
        return result
