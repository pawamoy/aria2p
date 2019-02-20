import random
import re
import subprocess
import tempfile
import time
from pathlib import Path

import aria2p
import requests

TESTS_DIR = Path(__file__).parent
TESTS_TMP_DIR = TESTS_DIR / "tmp"
TESTS_DATA_DIR = TESTS_DIR / "data"
CONFIGS_DIR = TESTS_DATA_DIR / "configs"
SESSIONS_DIR = TESTS_DATA_DIR / "sessions"

BUNSENLABS_TORRENT = TESTS_DATA_DIR / "bunsenlabs-helium-4.iso.torrent"
BUNSENLABS_MAGNET = "magnet:?xt=urn:btih:7fb1b254fdbdd8863d686c7fa61b3b0b671551b1&dn=bl-Helium-4-amd64.iso"
DEBIAN_METALINK = TESTS_DATA_DIR / "debian.metalink"
XUBUNTU_MIRRORS = [
    "http://ubuntutym2.u-toyama.ac.jp/xubuntu/18.04/release/xubuntu-18.04.1-desktop-amd64.iso",
    "http://ftp.free.fr/mirrors/ftp.xubuntu.com/releases/18.04/release/xubuntu-18.04.1-desktop-amd64.iso",
    "http://mirror.us.leaseweb.net/ubuntu-cdimage/xubuntu/releases/18.04/release/xubuntu-18.04.1-desktop-amd64.iso",
]


class _Aria2Server:
    def __init__(self, port=None, config=None, session=None, secret=""):
        # create the tmp dir
        self.tmp_dir = Path(tempfile.mkdtemp(dir=TESTS_TMP_DIR))

        if port is None:
            ports_used = {
                int(_.split("=")[1])
                for _ in re.findall(
                    r"--rpc-listen-port=[0-9]{4}", subprocess.check_output(["ps", "aux"]).decode("utf-8")
                )
            }
            while True:
                port = random.randint(6810, 7000)
                if port not in ports_used:
                    break

        self.port = port

        # create the command used to launch an aria2c process
        command = [
            "/usr/bin/aria2c",
            f"--dir={self.tmp_dir}",
            "--file-allocation=none",
            "--quiet",
            "--enable-rpc=true",
            f"--rpc-listen-port={self.port}",
        ]
        if config:
            command.append(f"--conf-path={config}")
        else:
            command.append("--no-conf")
        if session:
            if isinstance(session, list):
                session_path = self.tmp_dir / "_session.txt"
                with open(session_path, "w") as stream:
                    stream.write("\n".join(session))
                command.append(f"--input-file={session_path}")
            else:
                command.append(f"--input-file={session}")
        if secret:
            command.append(f"--rpc-secret={secret}")

        self.command = command
        self.process = None

        # create the client with port
        self.client = aria2p.Client(port=self.port, secret=secret)

        # create the API instance
        self.api = aria2p.API(self.client)

    def start(self):
        # create the subprocess
        self.process = subprocess.Popen(self.command)

        # make sure the server is running
        while True:
            try:
                self.client.list_methods()
            except requests.ConnectionError:
                time.sleep(0.1)
            else:
                break

    def wait(self):
        while True:
            try:
                self.process.wait()
            except subprocess.TimeoutExpired:
                pass
            else:
                break

    def terminate(self):
        self.process.terminate()
        self.wait()

    def kill(self):
        self.process.kill()
        self.wait()

    def rmdir(self, directory=None):
        if directory is None:
            directory = self.tmp_dir
        for item in directory.iterdir():
            if item.is_dir():
                self.rmdir(item)
            else:
                item.unlink()
        directory.rmdir()

    def destroy(self, force=False):
        if force:
            self.kill()
        else:
            self.terminate()
        self.rmdir()


class Aria2Server:
    def __init__(self, port=None, config=None, session=None, secret=""):
        self.server = _Aria2Server(port, config, session, secret)

    def __enter__(self):
        self.server.start()
        return self.server

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.server.destroy()
