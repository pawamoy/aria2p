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

"""Tests for selecting and verifying the test daemon's release artifacts."""

from __future__ import annotations

import hashlib
import os
import stat
from io import BytesIO
from typing import TYPE_CHECKING

import pytest

from scripts import install_aria2_next as installer

if TYPE_CHECKING:
    from pathlib import Path


@pytest.mark.parametrize(
    ("system", "machine", "platform_asset"),
    [
        ("Linux", "x86_64", "linux-x86_64"),
        ("Linux", "aarch64", "linux-aarch64"),
        ("Darwin", "x86_64", "macos-x86_64"),
        ("Darwin", "arm64", "macos-arm64"),
        ("Windows", "AMD64", "windows-x86_64.exe"),
        ("Windows", "ARM64", "windows-arm64.exe"),
    ],
)
def test_install_supported_platform(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    system: str,
    machine: str,
    platform_asset: str,
) -> None:
    # Supply a matching checksum for each platform's release asset.
    content = b"verified executable"
    asset = f"aria2-next-{installer.VERSION}-{platform_asset}"
    checksum = hashlib.sha256(content).hexdigest()
    downloads = []

    def download(url: str, timeout: int) -> BytesIO:
        assert timeout > 0
        downloads.append(url)
        if url.endswith("checksums.sha256"):
            return BytesIO(f"{checksum}  {asset}\n".encode())
        assert url.endswith(f"/{asset}")
        return BytesIO(content)

    monkeypatch.setattr(installer.platform, "system", lambda: system)
    monkeypatch.setattr(installer.platform, "machine", lambda: machine)
    monkeypatch.setattr(installer, "urlopen", download)

    executable = installer.install(tmp_path)

    assert executable.read_bytes() == content
    assert executable.name == ("aria2-next.exe" if system == "Windows" else "aria2-next")
    # Windows chmod does not set POSIX executable permission bits.
    if os.name != "nt":
        assert executable.stat().st_mode & stat.S_IXUSR
    assert len(downloads) == 2


def test_checksum_mismatch_preserves_existing_installation(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    # An invalid download must not replace an executable that already works.
    executable = tmp_path / "aria2-next"
    executable.write_bytes(b"existing executable")
    checksum = hashlib.sha256(b"expected executable").hexdigest()
    asset = f"aria2-next-{installer.VERSION}-linux-x86_64"

    def download(url: str, timeout: int) -> BytesIO:
        assert timeout > 0
        if url.endswith("checksums.sha256"):
            return BytesIO(f"{checksum}  {asset}\n".encode())
        return BytesIO(b"incorrect executable")

    monkeypatch.setattr(installer.platform, "system", lambda: "Linux")
    monkeypatch.setattr(installer.platform, "machine", lambda: "x86_64")
    monkeypatch.setattr(installer, "urlopen", download)

    with pytest.raises(ValueError, match="Checksum verification failed"):
        installer.install(tmp_path)

    assert executable.read_bytes() == b"existing executable"


def test_main_registers_the_executable_for_later_ci_steps(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    # GitHub Actions provides files for exposing paths and variables to later steps.
    runner_temp = tmp_path / "runner temp"
    github_path = tmp_path / "github-path"
    github_env = tmp_path / "github-env"
    monkeypatch.setenv("RUNNER_TEMP", str(runner_temp))
    monkeypatch.setenv("GITHUB_PATH", str(github_path))
    monkeypatch.setenv("GITHUB_ENV", str(github_env))
    monkeypatch.setattr(installer, "install", lambda directory: directory / "aria2-next")

    installer.main()

    # Preserve paths containing spaces so the daemon can be found on every runner.
    executable = runner_temp / "aria2-next" / "aria2-next"
    assert github_path.read_text(encoding="utf-8") == f"{executable.parent}\n"
    assert github_env.read_text(encoding="utf-8") == f"ARIA2_NEXT={executable}\n"


@pytest.mark.parametrize(("system", "machine"), [("FreeBSD", "x86_64"), ("Linux", "riscv64")])
def test_unsupported_platform_fails_before_downloading(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, system: str, machine: str
) -> None:
    # Unsupported runners must fail clearly without creating a partial installation.
    monkeypatch.setattr(installer.platform, "system", lambda: system)
    monkeypatch.setattr(installer.platform, "machine", lambda: machine)

    with pytest.raises(ValueError, match="Unsupported platform"):
        installer.install(tmp_path / "bin")

    assert not (tmp_path / "bin").exists()
