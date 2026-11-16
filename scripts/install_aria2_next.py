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

"""Install a pinned aria2-next release for the CI test matrix."""

from __future__ import annotations

import hashlib
import os
import platform
import stat
from pathlib import Path
from urllib.request import urlopen

# Keep the same daemon release across CI platforms, including Windows without Homebrew.
VERSION = "3.1.0"
RELEASE_URL = f"https://github.com/AnInsomniacy/aria2-next/releases/download/v{VERSION}"


def install(directory: Path) -> Path:
    """Download and verify the current platform's executable before installing it."""
    system = platform.system()
    machine = platform.machine().lower()
    systems = {"Linux": "linux", "Darwin": "macos", "Windows": "windows"}
    architectures = {"x86_64": "x86_64", "amd64": "x86_64", "aarch64": "arm64", "arm64": "arm64"}
    if system not in systems or machine not in architectures:
        raise ValueError(f"Unsupported platform: {system} {machine}")
    architecture = architectures[machine]
    if system == "Linux" and architecture == "arm64":
        architecture = "aarch64"
    suffix = ".exe" if system == "Windows" else ""
    asset = f"aria2-next-{VERSION}-{systems[system]}-{architecture}{suffix}"

    with urlopen(f"{RELEASE_URL}/aria2-next-{VERSION}-checksums.sha256", timeout=60) as response:  # noqa: S310
        manifest = response.read().decode("utf-8")
    checksums = {}
    for line in manifest.splitlines():
        if line.strip():
            checksum, name = line.split()
            checksums[name.lstrip("*")] = checksum
    with urlopen(f"{RELEASE_URL}/{asset}", timeout=60) as response:  # noqa: S310
        content = response.read()
    if hashlib.sha256(content).hexdigest() != checksums.get(asset):
        raise ValueError(f"Checksum verification failed for {asset}")

    # Verify before writing so a failed download preserves any working installation.
    directory.mkdir(parents=True, exist_ok=True)
    executable = directory / f"aria2-next{suffix}"
    executable.write_bytes(content)
    executable.chmod(executable.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
    return executable


def main() -> None:
    """Install the daemon and expose its path to subsequent GitHub Actions steps."""
    directory = Path(os.environ.get("RUNNER_TEMP", ".cache")) / "aria2-next"
    executable = install(directory.resolve())
    if github_path := os.environ.get("GITHUB_PATH"):
        with Path(github_path).open("a", encoding="utf-8") as file:
            file.write(f"{executable.parent}\n")
    if github_env := os.environ.get("GITHUB_ENV"):
        with Path(github_env).open("a", encoding="utf-8") as file:
            file.write(f"ARIA2_NEXT={executable}\n")
    print(f"Installed aria2-next {VERSION}: {executable}")


if __name__ == "__main__":
    main()
