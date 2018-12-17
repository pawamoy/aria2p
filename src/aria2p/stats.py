class Stats:
    def __init__(self, api, struct):
        self.api = api

        self.download_speed = struct.get("downloadSpeed")
        # Overall download speed (byte/sec).

        self.upload_speed = struct.get("uploadSpeed")
        # Overall upload speed(byte/sec).

        self.num_active = struct.get("numActive")
        # The number of active downloads.

        self.num_waiting = struct.get("numWaiting")
        # The number of waiting downloads.

        self.num_stopped = struct.get("numStopped")
        # The number of stopped downloads in the current session. This value is capped by the
        # --max-download-result option.

        self.num_stopped_total = struct.get("numStoppedTotal")
        # The number of stopped downloads in the current session and not capped by the
        # --max-download-result option.
