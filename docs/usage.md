# Usage

Extensive usage instructions will be added later, when the application is more stable.
You can also refer to the README / Overview.

## Listening to notifications

Since [version 0.3](changelog.md#v030-compare-2019-10-11), it is possible to listen to the server notifications
thanks to the [`websocket-client`](https://pypi.org/project/websocket_client/) Python package.

The server sends a notification to the client through a WebSocket for each of these events:
- a download is started,
- a download is paused,
- a download is stopped,
- a download fails,
- a download is complete,
- a bittorrent download is complete (received 100%, still seeding).

### Through the command line

The command line interface offers a `listen` subcommand:

```bash
aria2p listen -c /path/to/callbacks.py
```

<small><em>In the future, a default path will be used for the callbacks module.</em></small>

The `callbacks.py` file is a Python module defining one or more of these callback functions:
- `on_download_start`,
- `on_download_pause`,
- `on_download_stop`,
- `on_download_error`,
- `on_download_complete`,
- `on_bt_download_complete`.

Each one of these callbacks must accept two parameters: the API instance and the GID of the download.
You can use the names you want.

Example:

```python
# ~/callbacks.py
import subprocess
from pathlib import Path


def on_download_error(api, gid):
    # pop a desktop notification using notify-send
    download = api.get_download(gid)
    summary = f"A download failed"
    body = f"{download.name}\n{download.error_message} (code: {download.error_code})."
    subprocess.call(["notify-send", "-t", "10000", summary, body])


def on_download_complete(api, gid):
    download = api.get_download(gid)
    # purge if it was a magnet metadata download
    if download.is_metadata:
        download.purge()
        return
    # move files to another folder
    destination = Path.home() / "library"
    if download.move_files(destination):
        download.control_file_path.unlink()
        download.purge()
```

You can now use this callbacks module with `aria2p listen -c ~/callbacks.py`.

#### Process specific types of notifications

If you want to listen to only a particular type of notification, even though your callbacks module
defines all the possible callbacks, you can pass additional arguments:

```bash
# let say you want to run multiple listeners:
# one for errors, one for completions, and one for the rest
aria2p listen -c ~/callbacks.py error &
aria2p listen -c ~/callbacks.py complete btcomplete &
aria2p listen -c ~/callbacks.py start pause stop &
```

This is possible because the server sends the notifications to every client that is listening.

#### Interruption

To stop listening, send a SIGTERM or SIGINT signal to the process,
for example by hitting Control-C if aria2p is running in the foreground.
If a notification is currently being handled, it will finish before the listener is stopped.

#### Timeout

If you find the default five seconds to be too long when interrupting the process,
you can decrease this timeout value by passing the `-t` or `--timeout` option:

```bash
aria2p listen -c ~/callbacks.py -t 1
```

### Programmatically

Both the [`API`][aria2p.api.API.listen_to_notifications]
and [`Client`][aria2p.client.Client.listen_to_notifications] classes provide a method called
`listen_to_notifications`, and another one called `stop_listening`. Please check their respective documentation. 

