"""Configuration for the pytest test suite."""

import json
import os
import random
import subprocess
import sys
import time
from pathlib import Path

import pytest
import requests

from aria2p import API, Client, enable_logger

from . import CONFIGS_DIR, SESSIONS_DIR


@pytest.fixture(autouse=True)
def tests_logs(request):
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
    enable_logger(sink=log_path, level=os.environ.get("PYTEST_LOG_LEVEL", "TRACE"))


def spawn_and_wait_server(port=8779):
    process = subprocess.Popen(
        [
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
            requests.get(f"http://localhost:{port}/1024")
        except:
            time.sleep(0.1)
        else:
            break
    return process


@pytest.fixture(scope="session", autouse=True)
def http_server(tmp_path_factory, worker_id):
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


class _Aria2Server:
    def __init__(self, tmp_dir, port, config=None, session=None, secret=""):
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
        self.process = None

        # create the client with port
        self.client = Client(port=self.port, secret=secret, timeout=20)

        # create the API instance
        self.api = API(self.client)

    def start(self):
        while True:
            # create the subprocess
            self.process = subprocess.Popen(self.command)

            # make sure the server is running
            retries = 5
            while retries:
                try:
                    self.client.list_methods()
                except requests.ConnectionError:
                    time.sleep(0.1)
                    retries -= 1
                else:
                    break

            if retries:
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
    def __init__(self, tmp_dir, port, config=None, session=None, secret=""):
        self.server = _Aria2Server(tmp_dir, port, config, session, secret)

    def __enter__(self):
        self.server.start()
        return self.server

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.server.destroy(force=True)


ports_file = Path(".ports.json")


def get_lock():
    lockdir = Path(".lockdir")
    while True:
        try:
            lockdir.mkdir(exist_ok=False)
        except FileExistsError:
            time.sleep(0.025)
        else:
            break


def release_lock():
    Path(".lockdir").rmdir()


def get_random_port():
    return random.randint(15000, 16000)


def get_current_ports():
    try:
        return json.loads(ports_file.read_text())
    except FileNotFoundError:
        return []


def set_current_ports(ports):
    ports_file.write_text(json.dumps(ports))


def reserve_port():
    get_lock()

    ports = get_current_ports()
    port_number = get_random_port()
    while port_number in ports:
        port_number = get_random_port()
    ports.append(port_number)
    set_current_ports(ports)

    release_lock()
    return port_number


def release_port(port_number):
    get_lock()
    ports = get_current_ports()
    ports.remove(port_number)
    set_current_ports(ports)
    release_lock()


@pytest.fixture
def port():
    port_number = reserve_port()
    yield port_number
    release_port(port_number)


@pytest.fixture
def server(tmp_path, port):
    with Aria2Server(tmp_path, port) as server:
        yield server
