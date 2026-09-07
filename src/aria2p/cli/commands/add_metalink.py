"""Deprecated. Import from [`aria2p`][] directly."""

# YORE: Bump 2: Remove file.

import warnings
from typing import Any

from aria2p._internal.cli.commands import add_metalink as _add_metalink


def __getattr__(name: str) -> Any:
    warnings.warn(
        "Importing from `aria2p.cli.commands.add_metalink` is deprecated. Import from `aria2p` directly.",
        DeprecationWarning,
        stacklevel=2,
    )
    return getattr(_add_metalink, name)
