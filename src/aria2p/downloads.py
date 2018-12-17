class Bittorrent:
    def __init__(self, struct):
        self._struct = struct

    def __str__(self):
        return self.info["name"]

    @property
    def announce_list(self):
        # List of lists of announce URIs. If the torrent contains announce and no announce-list, announce
        # is converted to the announce-list format.
        return self._struct.get("announceList")

    @property
    def comment(self):
        # The comment of the torrent. comment.utf-8 is used if available.
        return self._struct.get("comment")

    @property
    def creation_date(self):
        # The creation time of the torrent. The value is an integer since the epoch, measured in seconds.
        return self._struct.get("creationDate")

    @property
    def mode(self):
        # File mode of the torrent. The value is either single or multi.
        return self._struct.get("mode")

    @property
    def info(self):
        # Struct which contains data from Info dictionary. It contains following keys.
        # name   name in info dictionary. name.utf-8 is used if available.
        return self._struct.get("info")


class File:
    def __init__(self, struct):
        self._struct = struct

    def __str__(self):
        return self.path

    @property
    def index(self):
        # Index of the file, starting at 1, in the same order as files appear in the multi-file torrent.
        return self._struct.get("index")

    @property
    def path(self):
        # File path.
        return self._struct.get("path")

    @property
    def length(self):
        # File size in bytes.
        return self._struct.get("length")

    @property
    def completed_length(self):
        # Completed length of this file in bytes. Please note that it is possible that sum of completedLength
        # is less than the completedLength returned by the aria2.tellStatus() method. This is because
        # completedLength in aria2.getFiles() only includes completed pieces. On the other hand,
        # completedLength in aria2.tellStatus() also includes partially completed pieces.
        return self._struct.get("completedLength")

    @property
    def selected(self):
        # true if this file is selected by --select-file option. If --select-file is not specified or this is
        # single-file torrent or not a torrent download at all, this value is always true. Otherwise false.
        return self._struct.get("selected")

    @property
    def uris(self):
        # Returns a list of URIs for this file. The element type is the same struct used in the aria2.getUris()
        # method.
        return self._struct.get("uris")


class Download:
    def __init__(self, api, struct):
        self.api = api
        self._struct = struct
        self._files = []
        self._bittorrent = None
        self._name = ""
        self._options = None

    def __str__(self):
        return self.name

    @property
    def name(self):
        if not self._name:
            self._name = self.files[0].path.replace(self.dir, "").lstrip("/")
        return self._name

    @property
    def options(self):
        if not self._options:
            self._options = self.api.get_options(gids=[self.gid]).get(self.gid)
        return self._options

    @property
    def gid(self):
        return self._struct.get("gid")

    @property
    def status(self):
        # active waiting paused error complete removed
        return self._struct.get("status")

    @property
    def total_length(self):
        # Total length of the download in bytes.
        return self._struct.get("totalLength")

    @property
    def completed_length(self):
        # Completed length of the download in bytes.
        return self._struct.get("completedLength")

    @property
    def upload_length(self):
        # Uploaded length of the download in bytes.
        return self._struct.get("uploadLength")

    @property
    def bitfield(self):
        # Hexadecimal representation of the download progress. The highest bit corresponds to the piece at
        # index 0. Any set bits indicate loaded pieces, while unset bits indicate not yet loaded and/or missing
        # pieces. Any overflow bits at the end are set to zero. When the download was not started yet, this key
        # will not be included in the response.
        return self._struct.get("bitfield")

    @property
    def download_speed(self):
        # Download speed of this download measured in bytes/sec.
        return self._struct.get("downloadSpeed")

    @property
    def upload_speed(self):
        # Upload speed of this download measured in bytes/sec.
        return self._struct.get("uploadSpeed")

    @property
    def info_hash(self):
        # InfoHash. BitTorrent only.
        return self._struct.get("infoHash")

    @property
    def num_seeders(self):
        # The number of seeders aria2 has connected to. BitTorrent only.
        return self._struct.get("numSeeders")

    @property
    def seeder(self):
        # true if the local endpoint is a seeder. Otherwise false. BitTorrent only.
        return self._struct.get("seeder ")

    @property
    def piece_length(self):
        # Piece length in bytes.
        return self._struct.get("pieceLength")

    @property
    def num_pieces(self):
        # The number of pieces.
        return self._struct.get("numPieces")

    @property
    def connections(self):
        # The number of peers/servers aria2 has connected to.
        return self._struct.get("connections")

    @property
    def error_code(self):
        # The code of the last error for this item, if any. The value is a string. The error codes are defined
        # in the EXIT STATUS section. This value is only available for stopped/completed downloads.
        return self._struct.get("errorCode")

    @property
    def error_message(self):
        # The (hopefully) human readable error message associated to errorCode.
        return self._struct.get("errorMessage")

    @property
    def followed_by_ids(self):
        # List of GIDs which are generated as the result of this download. For example, when aria2 downloads a
        # Metalink file, it generates downloads described in the Metalink (see the --follow-metalink
        # option). This value is useful to track auto-generated downloads. If there are no such downloads,
        # this key will not be included in the response.
        return self._struct.get("followedBy")

    @property
    def followed_by(self):
        return [self.api.get_download(gid) for gid in self.followed_by_ids]

    @property
    def following_id(self):
        # The reverse link for followedBy. A download included in followedBy has this object's GID in its
        # following value.
        return self._struct.get("following")

    @property
    def following(self):
        return self.api.get_download(self.following_id)

    @property
    def belongs_to_id(self):
        # GID of a parent download. Some downloads are a part of another download. For example, if a file in a
        # Metalink has BitTorrent resources, the downloads of ".torrent" files are parts of that parent. If
        # this download has no parent, this key will not be included in the response.
        return self._struct.get("belongsTo")

    @property
    def belongs_to(self):
        return self.api.get_download(self.belongs_to_id)

    @property
    def dir(self):
        # Directory to save files.
        return self._struct.get("dir")

    @property
    def files(self):
        # Return the list of files. The elements of this list are the same structs used in aria2.getFiles() method.
        if not self._files:
            self._files = [File(s) for s in self._struct.get("files")]
        return self._files

    @property
    def bittorrent(self):
        # Struct which contains information retrieved from the .torrent (file). BitTorrent only.
        if not self._bittorrent:
            self._bittorrent = Bittorrent(self._struct.get("bittorrent"))
        return self._bittorrent

    @property
    def verified_length(self):
        # The number of verified number of bytes while the files are being hash checked. This key exists only
        # when this download is being hash checked.
        return self._struct.get("verifiedLength")

    @property
    def verify_integrity_pending(self):
        # true if this download is waiting for the hash check in a queue.
        # This key exists only when this download is in the queue.
        return self._struct.get("verifyIntegrityPending")

    def update(self, struct):
        self._struct.update(struct)
