"""Command to show downloads."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from aria2p.api import API


def show(api: API) -> int:
    """Show subcommand.

    Parameters:
        api: The API instance to use.

    Returns:
        int: Always 0.
    """
    downloads = api.get_downloads()

    def print_line(*args: Any) -> None:
        print("{:<17} {:<9} {:>8} {:>12} {:>12} {:>8}  {}".format(*args))

    print_line("GID", "STATUS", "PROGRESS", "DOWN_SPEED", "UP_SPEED", "ETA", "NAME")

    for download in downloads:
        print_line(
            download.gid,
            download.status,
            download.progress_string(),
            download.download_speed_string(),
            download.upload_speed_string(),
            download.eta_string(),
            download.name,
        )

    return 0
