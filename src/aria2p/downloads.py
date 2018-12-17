class Bittorrent:
    def __init__(self, struct):
        self.announce_list = struct.get("announceList")
        # List of lists of announce URIs. If the torrent contains announce and no announce-list, announce
        # is converted to the announce-list format.

        self.comment = struct.get("comment")
        # The comment of the torrent. comment.utf-8 is used if available.

        self.creation_date = struct.get("creationDate")
        # The creation time of the torrent. The value is an integer since the epoch, measured in seconds.

        self.mode = struct.get("mode")
        # File mode of the torrent. The value is either single or multi.

        self.info = struct.get("info")
        # Struct which contains data from Info dictionary. It contains following keys.
        # name   name in info dictionary. name.utf-8 is used if available.

    def __str__(self):
        return self.info["name"]


class File:
    def __init__(self, struct):
        self.index = struct.get("index")
        # Index of the file, starting at 1, in the same order as files appear in the multi-file torrent.

        self.path = struct.get("path")
        # File path.

        self.length = struct.get("length")
        # File size in bytes.

        self.completed_length = struct.get("completedLength")
        # Completed length of this file in bytes. Please note that it is possible that sum of completedLength
        # is less than the completedLength returned by the aria2.tellStatus() method. This is because
        # completedLength in aria2.getFiles() only includes completed pieces. On the other hand,
        # completedLength in aria2.tellStatus() also includes partially completed pieces.

        self.selected = struct.get("selected")
        # true if this file is selected by --select-file option. If --select-file is not specified or this is
        # single-file torrent or not a torrent download at all, this value is always true. Otherwise false.

        self.uris = struct.get("uris")
        # Returns a list of URIs for this file. The element type is the same struct used in the aria2.getUris()
        # method.

    def __str__(self):
        return self.path


class Download:
    def __init__(self, api, struct):
        self.api = api

        self.gid = struct.get("gid")

        self.status = struct.get("status")
        # active waiting paused error complete removed

        self.total_length = struct.get("totalLength")
        # Total length of the download in bytes.

        self.completed_length = struct.get("completedLength")
        # Completed length of the download in bytes.

        self.upload_length = struct.get("uploadLength")
        # Uploaded length of the download in bytes.

        self.bitfield = struct.get("bitfield")
        # Hexadecimal representation of the download progress. The highest bit corresponds to the piece at
        # index 0. Any set bits indicate loaded pieces, while unset bits indicate not yet loaded and/or missing
        # pieces. Any overflow bits at the end are set to zero. When the download was not started yet, this key
        # will not be included in the response.

        self.download_speed = struct.get("downloadSpeed")
        # Download speed of this download measured in bytes/sec.

        self.upload_speed = struct.get("uploadSpeed")
        # Upload speed of this download measured in bytes/sec.

        self.info_hash = struct.get("infoHash")
        # InfoHash. BitTorrent only.

        self.num_seeders = struct.get("numSeeders")
        # The number of seeders aria2 has connected to. BitTorrent only.

        self.seeder = struct.get("seeder ")
        # true if the local endpoint is a seeder. Otherwise false. BitTorrent only.

        self.piece_length = struct.get("pieceLength")
        # Piece length in bytes.

        self.num_pieces = struct.get("numPieces")
        # The number of pieces.

        self.connections = struct.get("connections")
        # The number of peers/servers aria2 has connected to.

        self.error_code = struct.get("errorCode")
        # The code of the last error for this item, if any. The value is a string. The error codes are defined
        # in the EXIT STATUS section. This value is only available for stopped/completed downloads.

        self.error_message = struct.get("errorMessage")
        # The (hopefully) human readable error message associated to errorCode.

        self.followed_by_ids = struct.get("followedBy")
        # List of GIDs which are generated as the result of this download. For example, when aria2 downloads a
        # Metalink file, it generates downloads described in the Metalink (see the --follow-metalink
        # option). This value is useful to track auto-generated downloads. If there are no such downloads,
        # this key will not be included in the response.

        self.following_id = struct.get("following")
        # The reverse link for followedBy. A download included in followedBy has this object's GID in its
        # following value.

        self.belongs_to_id = struct.get("belongsTo")
        # GID of a parent download. Some downloads are a part of another download. For example, if a file in a
        # Metalink has BitTorrent resources, the downloads of ".torrent" files are parts of that parent. If
        # this download has no parent, this key will not be included in the response.

        self.dir = struct.get("dir")
        # Directory to save files.

        self.files = [File(s) for s in struct.get("files")]
        # Return the list of files. The elements of this list are the same structs used in aria2.getFiles() method.

        self.bittorrent = Bittorrent(struct.get("bittorrent"))
        # Struct which contains information retrieved from the .torrent (file). BitTorrent only.

        self.verified_length = struct.get("verifiedLength")
        # The number of verified number of bytes while the files are being hash checked. This key exists only
        # when this download is being hash checked.

        self.verify_integrity_pending = struct.get("verifyIntegrityPending")
        # true if this download is waiting for the hash check in a queue.
        # This key exists only when this download is in the queue.

        self.name = self.files[0].path.replace(self.dir, "").lstrip("/")

    def __str__(self):
        return self.name

    @property
    def followed_by(self):
        return [self.api.get_download(gid) for gid in self.followed_by_ids]

    @property
    def following(self):
        return self.api.get_download(self.following_id)

    @property
    def belongs_to(self):
        return self.api.get_download(self.belongs_to_id)
