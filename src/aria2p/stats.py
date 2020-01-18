"""
This module defines the Stats class, which holds information retrieved with the ``get_global_stat`` method of the
client.
"""
from .utils import human_readable_bytes


class Stats:
    """This class holds information retrieved with the ``get_global_stat`` method of the client."""

    def __init__(self, struct: dict) -> None:
        """
        Initialization method.

        Parameters:
            struct: a dictionary Python object returned by the JSON-RPC client.
        """
        self._struct = struct or {}

    @property
    def download_speed(self) -> int:
        """Overall download speed (byte/sec)."""
        return int(self._struct.get("downloadSpeed"))

    def download_speed_string(self, human_readable: bool = True) -> str:
        """
        Return the download speed as string.

        Parameters:
            human_readable: return in human readable format or not.

        Returns:
            The download speed string.
        """
        if human_readable:
            return human_readable_bytes(self.download_speed, delim=" ", postfix="/s")
        return str(self.download_speed) + " B/s"

    @property
    def upload_speed(self) -> int:
        """Overall upload speed(byte/sec)."""
        return int(self._struct.get("uploadSpeed"))

    def upload_speed_string(self, human_readable: bool = True) -> str:
        """
        Return the upload speed as string.

        Parameters:
            human_readable: return in human readable format or not.

        Returns:
            The upload speed string.
        """
        if human_readable:
            return human_readable_bytes(self.upload_speed, delim=" ", postfix="/s")
        return str(self.upload_speed) + " B/s"

    @property
    def num_active(self) -> int:
        """The number of active downloads."""
        return int(self._struct.get("numActive"))

    @property
    def num_waiting(self) -> int:
        """The number of waiting downloads."""
        return int(self._struct.get("numWaiting"))

    @property
    def num_stopped(self) -> int:
        """
        The number of stopped downloads in the current session. This value is capped by the --max-download-result
        option.
        """
        return int(self._struct.get("numStopped"))

    @property
    def num_stopped_total(self) -> int:
        """The number of stopped downloads in the current session and not capped by the --max-download-result option."""
        return int(self._struct.get("numStoppedTotal"))
