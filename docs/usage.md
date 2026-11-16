# Usage

Extensive usage instructions will be added later, when the application is more stable.
You can also refer to the README / Overview.

## Supported engines

aria2p supports aria2 and aria2-next 3.1.0 or later through the same Python API and CLI. Create an [`API`][aria2p.API] with the daemon's RPC address:

```python
from aria2p import API, Client

api = API(Client(host="http://localhost", port=6800))
print(api.engine.name, api.engine.version)
print(api.engine.capabilities.move_download)
```

[`API.engine`][aria2p.API.engine] calls `aria2.getVersion` on first access and caches the result for the client's endpoint and secret.

After restarting or replacing the daemon at the same address, call [`API.check_engine()`][aria2p.API.check_engine] to update the cached engine and capabilities:

```python
engine = api.check_engine()
print(engine.name, engine.version)
```

`check_engine()` connects immediately and returns the detected engine. If detection fails, the cache stays empty; the next `api.engine` access retries detection.

Summary of differences between aria2 and aria2-next:

| Capability | aria2 | aria2-next 3.1+ |
| --- | --- | --- |
| `ftp` | Yes | No |
| `metalink3` | Yes | No |
| `control_files` | Adjacent `.aria2` files | Separate engine state |
| `move_download` | No native move RPC | Native move RPC |

In particular, the native `move_download` means you can move files on the distant server. With aria2, this API method only works if the daemon and client run on the same host.

For more information, see [Compatibility](https://github.com/AnInsomniacy/aria2-next#compatibility) and [RPC extensions](https://github.com/AnInsomniacy/aria2-next/blob/main/docs/rpc-extensions.md) in aria2-next's documentation.

The high-level API rejects known unsupported options with `ValueError` instead of silently discarding them.

For example, aria2-next cannot honor `piece-length`, `max-resume-failure-tries`, or `always-resume`. Its connection and split limits also differ from aria2's limits. The `bt-require-crypto` and `bt-force-encryption` options map to aria2-next's `bt-encryption` policy. Do not combine these aliases with an explicit `bt-encryption` value in one update.

[`Client`][aria2p.Client] remains a low-level RPC interface and passes daemon errors to the caller. Its explicitly defined `move_download()` method requires aria2-next. Use `Client.call()` to send other engine extensions directly.

## Listing downloads

Use `aria2p list` to print one download name per line. The `aria2p show` command is deprecated and will be removed in version 2. Use `aria2p list -l -H` for the same table output with human-readable units.

```bash
aria2p list
aria2p list 0000000000000001
aria2p list '*.iso' '*.zip'
aria2p list -l -H
aria2p list --sort=-progress,name --limit 10
aria2p list --format '{gid} {status} {name}'
```

Selection arguments match exact GIDs or case-sensitive shell-style name patterns. A download appears once if any argument matches.
Quote patterns to prevent your shell from expanding them. Without selection arguments, all retrieved downloads are included.

Use `-l` or `--long` for a table with GID, status, progress, download speed, upload speed, ETA, and name.
Use `-f` or `--format` with `name`, `gid`, `long`, or a custom Python format string.
Custom formats accept these fields: `gid`, `status`, `progress`, `total_length`, `completed_length`, `download_speed`, `upload_speed`, `eta`, and `name`.
Progress is a number from 0 to 100. For a percentage, use `{progress:.2f}%`.
Literal text and standard Python format specifications are supported; backslash escapes are printed literally.

By default, sizes use bytes, speeds use bytes per second, and ETA uses seconds. An unknown ETA is `-`.
Use `-H` or `--human-readable` to format sizes, speeds, and ETA with units.
These fields become strings, so numeric format specifications for them require omitting `-H`.

Use `-s` or `--sort` with one or more comma-separated field names. Earlier fields take priority.
Prefix a field with `-` for descending order, using `--sort=-progress,name` when the value starts with `-`.
Sorting uses raw values, including when `-H` is enabled.
Without sorting, downloads appear in daemon order: active, waiting, then stopped. Retrieval includes up to 1,000 waiting and 1,000 stopped downloads.
Use `--limit` to restrict the result after filtering and sorting. A limit of zero prints no download rows.

## Moving downloads to another directory

Use [`Download.move_files()`][aria2p.Download.move_files] to move downloaded files to another directory.
For an unfinished download, pass `force=True` to change its output directory and move its existing files:

```python
download = api.get_download(gid)
download.move_files("/path/to/new-directory", force=True)
```

With aria2, the operation pauses active downloads, moves their files and `.aria2` control file, then resumes them in the new directory. With aria2-next, the operation uses its native move RPC to update files and engine state together. For a paused download without a resolved filename, it changes the output directory before the download starts.

Downloads that were already paused remain paused.
The destination directory is created if necessary.
Existing destination files cause an error when moving unfinished downloads.

Use [`API.move_files()`][aria2p.API.move_files] to move several downloads:

```python
api.move_files([first_gid, second_gid], "/path/to/new-directory", force=True)
```

Moving files requires a localhost connection and access to the same filesystem as the aria2 daemon.
For completed downloads, `move_files()` moves the files without changing aria2's recorded output directory.

## Listening to notifications

Since [version 0.3](changelog.md#030-2019-10-11), it is possible to listen to the server notifications
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

Both the [`API`][aria2p.API.listen_to_notifications]
and [`Client`][aria2p.Client.listen_to_notifications] classes provide a method called
`listen_to_notifications`, and another one called `stop_listening`. Please check their respective documentation.
