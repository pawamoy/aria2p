"""
Daemon module.

This module defines the `Daemon` context manager to help running `aria2c`
process as a daemon.
"""

import os
import shlex
from signal import SIGINT
from subprocess import PIPE, Popen  # noqa: S404
from tempfile import NamedTemporaryFile


class Daemon:
    """Context manager to run aria2c as a daemon."""

    def __init__(self, secret, port=6800, listen_all=False, executable="aria2c"):
        """Instantiate the daemon.

        Arguments:
            secret: equivalent to `--rpc-secret`
            port: equivalent to `--rpc-listen-port`
            listen_all: equivalent to `--rpc-listen-all`
            executable: absolute or relative name to `aria2c` executable
        """
        self.executable = executable
        self.config = {
            "enable-color": "false",
            "enable-rpc": "true",
            "rpc-listen-all": str(listen_all).lower(),
            "rpc-listen-port": port,
            "rpc-secret": secret,
            "summary-interval": "0",
        }

    def __enter__(self):  # noqa: WPS231
        tmp = NamedTemporaryFile(delete=False, suffix=".conf", prefix="aria2c-")
        self.config_filename = tmp.name
        with open(tmp.name, mode="w") as fobj:
            for key, value in self.config.items():
                fobj.write(f"{key}={value}\n")
        os.chmod(tmp.name, 0o600)  # noqa: WPS432 (magic number)
        command = f"{self.executable} --conf-path {shlex.quote(tmp.name)}"
        self.process = Popen(shlex.split(command), stdin=PIPE, stdout=PIPE, stderr=PIPE)  # noqa: S603 (subprocess call)
        for _ in range(10):  # Read first lines
            line = self.process.stdout.readline().strip()
            if b"[ERROR]" in line:
                raise RuntimeError(f"Error when running aria2c: '{line}'")
            elif b"[NOTICE]" in line and b"listening" in line:  # Listening!
                break
        return self

    def __exit__(self, exc_type, exc_value, exc_tb):
        self.process.send_signal(SIGINT)
        self.process.wait()
        os.remove(self.config_filename)
