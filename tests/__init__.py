"""Tests suite for `aria2p`."""

from __future__ import annotations

from pathlib import Path

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

INPUT_FILES = [
    TESTS_DATA_DIR / "input_files" / "two-valid-downloads",
    TESTS_DATA_DIR / "input_files" / "one-valid-one-invalid-downloads",
    TESTS_DATA_DIR / "input_files" / "two-invalid-downloads",
]
