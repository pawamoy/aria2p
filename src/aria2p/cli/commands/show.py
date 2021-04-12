"""Command to show downloads."""

from aria2p.api import API


def show(api: API) -> int:
    """
    Show subcommand.

    Arguments:
        api: The API instance to use.

    Returns:
        int: Always 0.
    """
    downloads = api.get_downloads()

    def print_line(*args):  # noqa: WPS430 (nested function)
        print("{:<17} {:<9} {:>8} {:>12} {:>12} {:>8}  {}".format(*args))  # noqa: P101 (unindexed params)

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
