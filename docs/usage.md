# Usage

Extensive usage instructions will be added later, when the application is more stable.
You can also refer to the README / Overview.

## Custom JSON-RPC path

By default, aria2p connects to `/jsonrpc`. If a reverse proxy exposes a different path, set the global `--path` option before the command:

```bash
aria2p --host https://example.com --port 443 --path /custom/rpc list
```

When you use the Python library, pass `path` to `Client`:

```python
import aria2p

client = aria2p.Client(host="https://example.com", port=443, path="/custom/rpc")
aria2 = aria2p.API(client)
```

The path applies to HTTP requests and WebSocket notifications. A leading slash is optional. Use `/` or an empty string to connect to the server root.

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

## Selecting files in a torrent

With Python, use the indexes from [`Download.files`][aria2p.Download.files]:

```python
import aria2p

api = aria2p.API()
download = api.add_torrent("example.torrent", options={"pause": "true"})
for file in download.files:
    print(file.index, file.path, file.selected)

download.select_files([1, 3])
download.resume()
```

[`Download.select_files`][aria2p.Download.select_files] replaces the previous selection and refreshes the download's data after success.
Indexes start at 1.
To select every file again, pass all indexes from `download.files`.

When adding a torrent through the command line, pass the aria2 `select-file` option:

```bash
aria2p add-torrent --options 'select-file=1,3-5' example.torrent
```

aria2 can restart an active download when you change its selection.
It can also download parts of adjacent files that share torrent pieces with selected files.

## Selecting downloads

Use search options with `list`, `pause`, `resume`, or `remove` to select downloads before applying the command:

```bash
aria2p pause --filter status=waiting
aria2p resume --pattern "forest sounds"
aria2p resume --pattern '\.iso$'
aria2p list --pattern linux --filter status=paused
```

`--pattern` searches download names with a Python regular expression. Matching is case-insensitive by default. Wrap an expression in `(?-i:...)` to make it case-sensitive. For example, `(?-i:Linux)` matches `Linux` but does not match `linux`. See [Python's regex flags](https://docs.python.org/3/library/re.html#re-syntax) for other inline flags.

```bash
aria2p list --pattern '(?-i:Linux)'
aria2p list --pattern 'forest sounds\.flac'
```

Escape regex metacharacters to match them literally, as with `\.` in the second example. Quote patterns to prevent your shell from interpreting them.

Search criteria combine as follows:

- Repeated `--pattern` values use **OR**. Matching any one name pattern is enough.
- All `--filter` values use **AND**. A download must match every field filter as well as the name selection.
- Without name patterns, only the field filters restrict the results.

For example:

```bash
aria2p list --pattern linux --pattern '\.iso$' --filter status=paused --filter is_torrent=false
```

This selects paused, non-torrent downloads whose names contain `linux` **OR** end with `.iso`:

```text
(contains "linux" OR matches '\.iso$') AND status=paused AND is_torrent=false
```

Filters use `field=value` with Python `Download` property names in snake_case. Values match exactly; `total_length=1024` matches a size in bytes. Boolean values accept `true` and `false` without regard to case. Each field can appear only once. Use `--pattern` for more flexible name matching.

These local scalar fields support filtering:

- Identity and location: `gid`, `name`, `dir`, `info_hash`, `following_id`, `belongs_to_id`.
- Status: `status`, `is_active`, `is_waiting`, `is_paused`, `has_failed`, `is_complete`, `is_removed`, `is_metadata`, `is_torrent`.
- Transfer: `total_length`, `completed_length`, `upload_length`, `download_speed`, `upload_speed`, `progress`, `eta`, `connections`.
- Torrent and verification: `bitfield`, `num_seeders`, `seeder`, `piece_length`, `num_pieces`, `verified_length`, `verify_integrity_pending`.
- Errors: `error_code`, `error_message`.

Some fields, such as `num_seeders`, are unavailable for non-torrent downloads. These downloads do not match filters on those fields.

Search options also work with command aliases, such as `stop`, `start`, and `rm`. When you supply GIDs, search options narrow that selection. Search options cannot be combined with `--all`. If no downloads match, the command succeeds without changing any downloads.

With `list`, search options narrow the positional GID or shell-style pattern selection before sorting and limiting the results:

```bash
aria2p list '*.iso' --filter status=paused --sort=name --limit 10
aria2p list --pattern '\.iso$' --filter is_torrent=false -l -H
```

### Through the Python API

[`API.search`][aria2p.API.search] returns download objects that you can pass directly to an API action:

```python
import aria2p

api = aria2p.API()
api.pause(api.search(filters={"status": "waiting"}))
api.resume(api.search(["forest sounds"]))
api.resume(api.search([r"\.iso$"]))
```

API filters accept typed Python values, such as `{"total_length": 1024}` or `{"is_torrent": False}`. They also accept the string values used by the CLI. To search an existing selection without fetching downloads, pass `downloads=selection`. An empty selection returns no matches. Without criteria, `api.search()` returns all current downloads.

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
