"""Deprecated. Import from [`aria2p`][] directly."""

# YORE: Bump 2: Remove file.

import warnings
from typing import Any

from aria2p._internal.cli.commands import remove as _remove


def __getattr__(name: str) -> Any:
    warnings.warn(
        "Importing from `aria2p.cli.commands.remove` is deprecated. Import from `aria2p` directly.",
        DeprecationWarning,
        stacklevel=2,
    )
    return getattr(_remove, name)
