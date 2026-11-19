# SPDX-License-Identifier: ISC
#
# ISC License
#
# Copyright (c) 2020, Timothée Mazzucotelli and contributors
#
# Permission to use, copy, modify, and/or distribute this software for any
# purpose with or without fee is hereby granted, provided that the above
# copyright notice and this permission notice appear in all copies.
#
# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
# WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
# ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
# WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
# ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
# OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.

"""Configuration for the pytest test suite."""

from __future__ import annotations

import hashlib
import os
import re
import socket
import subprocess
import sys
import time
from pathlib import Path
from typing import TYPE_CHECKING

import pytest
import requests

from aria2p import API, Client, Download, enable_logger
from tests import CONFIGS_DIR, SESSIONS_DIR

if TYPE_CHECKING:
    from collections.abc import Callable, Iterator


def wait_for(condition: Callable[[], bool], timeout: float = 10) -> None:
    """Wait for an asynchronous operation to finish, failing if it takes too long."""
    deadline = time.monotonic() + timeout
    while not condition():
        if time.monotonic() >= deadline:
            raise TimeoutError(f"Condition was not met within {timeout} seconds: {condition}")
        time.sleep(0.05)


@pytest.fixture(autouse=True)
def tests_logs(request: pytest.FixtureRequest) -> Path:
    # put logs in tests/logs
    log_path = Path("tests") / "logs"

    # tidy logs in subdirectories based on test module and class names
    module = request.module
    class_ = request.cls
    # Parameter values can contain invalid Windows filename characters. Keep a
    # bounded name and a unique suffix for names that sanitize to the same text.
    safe_name = re.sub(r'[<>:"/\\|?*\x00-\x1f]', "_", request.node.name)
    suffix = hashlib.sha256(request.node.nodeid.encode()).hexdigest()[:12]
    name = f"{safe_name[:150]}-{suffix}.log"

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
    return log_path


def spawn_and_wait_server(port: int = 8779) -> subprocess.Popen:
    process = subprocess.Popen(  # noqa: S603
        [
            sys.executable,
            "-m",
            "uvicorn",
            "tests.http_server:app",
            # Match download URLs to avoid IPv6 localhost connection delays.
            "--host",
            "127.0.0.1",
            "--port",
            str(port),
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    deadline = time.monotonic() + 10
    while time.monotonic() < deadline:
        if process.poll() is not None:
            raise RuntimeError(f"HTTP server exited with code {process.returncode}")
        try:
            response = requests.get(f"http://127.0.0.1:{port}/1024", timeout=1)
            response.raise_for_status()
        except requests.RequestException:
            time.sleep(0.05)
        else:
            return process

    process.kill()
    process.wait(timeout=5)
    raise TimeoutError("HTTP server did not become ready within 10 seconds")


def pytest_configure(config: pytest.Config) -> None:
    if hasattr(config, "workerinput") or config.option.collectonly:
        return

    # The controller starts the server before workers and keeps it alive until
    # every worker has finished. A worker's session fixture ends too early.
    process = spawn_and_wait_server()

    def stop_http_server() -> None:
        process.kill()
        process.wait(timeout=5)

    config.add_cleanup(stop_http_server)


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
            config: Daemon configuration file.
            session: Daemon session file.
            secret: Server secret.
        """
        self.tmp_dir = tmp_dir
        self.port = port
        self.log_path = Path("tests") / "logs" / f"aria2-{self.port}.log"

        engine = os.environ.get("ARIA2_ENGINE", "aria2-next")
        if engine == "aria2":
            executable = os.environ.get("ARIA2", "aria2c")
        elif engine == "aria2-next":
            executable = os.environ.get("ARIA2_NEXT", "aria2-next")
        else:
            raise ValueError(f"Unsupported ARIA2_ENGINE: {engine!r}; expected 'aria2' or 'aria2-next'")

        command = [
            executable,
            f"--dir={self.tmp_dir}",
            "--file-allocation=none",
            "--quiet",
            # Capture daemon diagnostics even when console output is suppressed.
            "--log=-",
            "--log-level=info",
            "--enable-rpc=true",
            f"--rpc-listen-port={self.port}",
        ]
        if engine == "aria2-next":
            # aria2-next persists engine state; aria2 does not support this option.
            # Isolate that state so later tests cannot restore earlier downloads.
            command.append(f"--state-dir={self.tmp_dir / '.aria2-next'}")
        if config:
            command.append(f"--conf-path={config}")
        else:
            config = CONFIGS_DIR / "default.conf"
            command.append(f"--conf-path={config}")
        if session:
            if isinstance(session, list):
                session_path = self.tmp_dir / "_session.txt"
                with open(session_path, "w", encoding="utf8") as stream:  # noqa: PTH123
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

        # The test daemon listens on IPv4; avoid IPv6 localhost connection timeouts.
        self.client = Client(host="http://127.0.0.1", port=self.port, secret=secret, timeout=20)

        # create the API instance
        self.api = API(self.client)

    def __enter__(self) -> Aria2Server:  # noqa: PYI034
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):  # noqa: ANN001
        self.destroy(force=True)

    def reach(self, retries: int = 5) -> bool:
        startup_client = Client(host=self.client.host, port=self.port, secret=self.client.secret, timeout=0.2)
        while retries:
            if self.process is not None and self.process.poll() is not None:
                return False
            try:
                startup_client.list_methods()
            except requests.RequestException:
                time.sleep(0.1)
                retries -= 1
            else:
                break
        else:
            return False
        return True

    def start(self) -> None:
        # Keep startup failures available after the process has been cleaned up.
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        with self.log_path.open("wb") as output:
            self.process = subprocess.Popen(self.command, stdout=output, stderr=subprocess.STDOUT)  # noqa: S603
        if not self.reach(retries=100):
            self.kill()
            raise RuntimeError(
                f"aria2 did not become ready:\n{self.log_path.read_text(encoding='utf-8', errors='replace')}"
            )

    def wait(self) -> None:
        if self.process:
            try:
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.process.kill()
                self.process.wait(timeout=5)

    def wait_for_download(
        self, gid: str = "0000000000000001", status: str = "complete", *, timeout: float = 10
    ) -> Download:
        """Return a download after its requested state has been reached."""
        download = self.api.get_download(gid)

        def reached_status() -> bool:
            download.update()
            assert not download.has_failed, f"Download {gid} failed: {download.error_message}"
            return download.status == status

        try:
            wait_for(reached_status, timeout=timeout)
        except TimeoutError as error:
            # Report the last poll without another RPC call that could hide the timeout.
            daemon_output = self.log_path.read_text(encoding="utf-8", errors="replace")[-8192:]
            raise TimeoutError(
                f"Download {gid} did not reach {status!r} within {timeout} seconds.\n"
                f"Last status: {download.status}; completed: {download.completed_length} bytes; "
                f"total: {download.total_length} bytes; speed: {download.download_speed} bytes/s; "
                f"error code: {download.error_code!r}; error message: {download.error_message!r}.\n"
                f"Daemon output ({self.log_path}, last 8192 characters):\n{daemon_output or '(empty)'}"
            ) from error
        return download

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


@pytest.fixture
def port() -> int:
    # Let the operating system choose an unused RPC port for this test.
    with socket.socket() as listener:
        listener.bind(("127.0.0.1", 0))
        return listener.getsockname()[1]


@pytest.fixture
def server(tmp_path: Path, port: int) -> Iterator[Aria2Server]:
    with Aria2Server(tmp_path, port) as server:
        yield server


@pytest.fixture
def isolated_http_server() -> Iterator[str]:
    """Run the HTTP test server on its own port to avoid other test sessions."""
    with socket.socket() as listener:
        listener.bind(("127.0.0.1", 0))
        http_port = listener.getsockname()[1]
    process = spawn_and_wait_server(http_port)
    try:
        yield f"http://127.0.0.1:{http_port}"
    finally:
        process.kill()
        process.wait(timeout=5)


@pytest.fixture
def multi_file_torrent(tmp_path: Path) -> Path:
    """Create a torrent with three files for selection tests without external downloads."""
    torrent = tmp_path / "selection.torrent"
    torrent.write_bytes(
        b"d4:infod5:filesl"
        b"d6:lengthi4e4:pathl9:first.txtee"
        b"d6:lengthi4e4:pathl10:second.txtee"
        b"d6:lengthi4e4:pathl9:third.txtee"
        b"e4:name5:files12:piece lengthi16384e6:pieces20:xxxxxxxxxxxxxxxxxxxxee",
    )
    return torrent
