"""Configuration for the pytest test suite."""

from __future__ import annotations

import json
import os
import random
import subprocess
import sys
import time
from pathlib import Path
from typing import Iterator

import psutil
import pytest
import requests

from aria2p import API, Client, enable_logger
from tests import CONFIGS_DIR, SESSIONS_DIR


@pytest.fixture(autouse=True)
def tests_logs(request: pytest.FixtureRequest) -> None:  # noqa: PT004
    # put logs in tests/logs
    log_path = Path("tests") / "logs"

    # tidy logs in subdirectories based on test module and class names
    module = request.module
    class_ = request.cls
    name = request.node.name + ".log"

    if module:
        log_path /= module.__name__.replace("tests.", "")
    if class_:
        log_path /= class_.__name__

    log_path.mkdir(parents=True, exist_ok=True)

    # append last part of the name and enable logger
    log_path /= name
    if log_path.exists():
        log_path.unlink()
    enable_logger(sink=str(log_path), level=os.environ.get("PYTEST_LOG_LEVEL", "TRACE"))


def spawn_and_wait_server(port: int = 8779) -> subprocess.Popen:
    process = subprocess.Popen(
        [  # noqa: S603
            sys.executable,
            "-m",
            "uvicorn",
            "tests.http_server:app",
            "--port",
            str(port),
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    while True:
        try:
            requests.get(f"http://localhost:{port}/1024")  # noqa: S113
        except:  # noqa: E722
            time.sleep(0.1)
        else:
            break
    return process


@pytest.fixture(scope="session", autouse=True)
def http_server(tmp_path_factory: pytest.TempPathFactory, worker_id: str) -> Iterator:
    if worker_id == "master":
        # single worker: just run the HTTP server
        process = spawn_and_wait_server()
        yield process
        process.kill()
        process.wait()
        return

    # get the temp directory shared by all workers
    root_tmp_dir = tmp_path_factory.getbasetemp().parent

    # try to get a lock
    lock = root_tmp_dir / "lock"
    try:
        lock.mkdir(exist_ok=False)
    except FileExistsError:
        yield  # failed, don't run the HTTP server
        return

    # got the lock, run the HTTP server
    process = spawn_and_wait_server()
    yield process
    process.kill()
    process.wait()


class Aria2Server:
    def __init__(
        self,
        tmp_dir: Path,
        port: int,
        config: str | Path | None = None,
        session: str | Path | list[str] | None = None,
        secret: str = "",
    ) -> None:
        """Initialize the server.

        Parameters:
            tmp_dir: Temporary download directory.
            port: Server port.
            config: aria2c configuration file.
            session: aria2c session file.
            secret: Server secret.
        """
        self.tmp_dir = tmp_dir
        self.port = port

        # create the command used to launch an aria2c process
        command = [
            "aria2c",
            f"--dir={self.tmp_dir}",
            "--file-allocation=none",
            "--quiet",
            "--enable-rpc=true",
            f"--rpc-listen-port={self.port}",
        ]
        if config:
            command.append(f"--conf-path={config}")
        else:
            # command.append("--no-conf")
            config = CONFIGS_DIR / "default.conf"
            command.append(f"--conf-path={config}")
        if session:
            if isinstance(session, list):
                session_path = self.tmp_dir / "_session.txt"
                with open(session_path, "w") as stream:
                    stream.write("\n".join(session))
                command.append(f"--input-file={session_path}")
            else:
                session_path = SESSIONS_DIR / session
                if not session_path.exists():
                    raise ValueError(f"no such session: {session}")
                command.append(f"--input-file={session_path}")
        if secret:
            command.append(f"--rpc-secret={secret}")

        self.command = command
        self.process: subprocess.Popen | None = None

        # create the client with port
        self.client = Client(port=self.port, secret=secret, timeout=20)

        # create the API instance
        self.api = API(self.client)

    def __enter__(self) -> Aria2Server:  # noqa: PYI034
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):  # noqa: ANN001
        self.destroy(force=True)

    def reach(self, retries: int = 5) -> None:
        while retries:
            try:
                self.client.list_methods()
            except requests.ConnectionError:
                time.sleep(0.1)
                retries -= 1
            else:
                break
        else:
            return False
        return True

    def start(self) -> None:
        # Make sure we kill any remaining aria2c process using the same port.
        for proc in psutil.process_iter():
            try:
                cmdline = proc.cmdline()
                if "aria2c" in cmdline and f"--rpc-listen-port={self.port}" in cmdline:
                    proc.kill()
                    proc.wait()
                    break
            except psutil.NoSuchProcess:
                pass

        # Make sure we start the new process.
        while True:
            self.process = subprocess.Popen(self.command)  # noqa: S603
            if self.reach(retries=10):
                break
            else:
                self.kill()

    def wait(self) -> None:
        if self.process:
            while True:
                try:
                    self.process.wait()
                except subprocess.TimeoutExpired:
                    pass
                else:
                    break

    def terminate(self) -> None:
        if self.process:
            self.process.terminate()
        self.wait()

    def kill(self) -> None:
        if self.process:
            self.process.kill()
        self.wait()

    def rmdir(self, directory: Path | None = None) -> None:
        if directory is None:
            directory = self.tmp_dir
        for item in directory.iterdir():
            if item.is_dir():
                self.rmdir(item)
            else:
                item.unlink()
        directory.rmdir()

    def destroy(self, *, force: bool = False) -> None:
        if force:
            self.kill()
        else:
            self.terminate()
        self.rmdir()


ports_file = Path(".ports.json")


def get_lock() -> None:
    lockdir = Path(".lockdir")
    while True:
        try:
            lockdir.mkdir(exist_ok=False)
        except FileExistsError:
            time.sleep(0.025)
        else:
            break


def release_lock() -> None:
    Path(".lockdir").rmdir()


def get_random_port() -> int:
    return random.randint(15000, 16000)  # noqa: S311


def get_current_ports() -> list[int]:
    try:
        return json.loads(ports_file.read_text())
    except FileNotFoundError:
        return []


def set_current_ports(ports: list[int]) -> None:
    ports_file.write_text(json.dumps(ports))


def reserve_port() -> int:
    get_lock()

    ports = get_current_ports()
    port_number = get_random_port()
    while port_number in ports:
        port_number = get_random_port()
    ports.append(port_number)
    set_current_ports(ports)

    release_lock()
    return port_number


def release_port(port_number: int) -> None:
    get_lock()
    ports = get_current_ports()
    ports.remove(port_number)
    set_current_ports(ports)
    release_lock()


@pytest.fixture()
def port() -> Iterator[int]:
    port_number = reserve_port()
    yield port_number
    release_port(port_number)


@pytest.fixture()
def server(tmp_path: Path, port: int) -> Iterator[Aria2Server]:
    with Aria2Server(tmp_path, port) as server:
        yield server
