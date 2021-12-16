<!--
IMPORTANT: This file is generated from the template at 'scripts/templates/README.md'.
           Please update the template instead of this file.
-->

# aria2p
[![ci](https://github.com/pawamoy/aria2p/workflows/ci/badge.svg)](https://github.com/pawamoy/aria2p/actions?query=workflow%3Aci)
[![documentation](https://img.shields.io/badge/docs-mkdocs%20material-blue.svg?style=flat)](https://pawamoy.github.io/aria2p/)
[![pypi version](https://img.shields.io/pypi/v/aria2p.svg)](https://pypi.org/project/aria2p/)
[![gitpod](https://img.shields.io/badge/gitpod-workspace-blue.svg?style=flat)](https://gitpod.io/#https://github.com/pawamoy/aria2p)
[![gitter](https://badges.gitter.im/join%20chat.svg)](https://gitter.im/aria2p/community)

Command-line tool and Python library to interact with an [`aria2c`][1] daemon process through JSON-RPC.

![demo](https://user-images.githubusercontent.com/3999221/72664104-41658180-39fa-11ea-838e-022ed29d8c0b.gif)

To avoid confusion:

- [*aria2*][1] is a lightweight multi-protocol & multi-source, cross platform download utility operated in command-line.
It supports HTTP/HTTPS, FTP, SFTP, BitTorrent and Metalink.
- `aria2c` is the name of the command-line executable provided by *aria2*. It can act as a daemon.
- `aria2p` (`p` for Python) is a command-line client that can interact with an `aria2c` daemon.
  It is not an official client. There are other Python packages allowing you to interact with an `aria2c` daemon.
  These other packages do not offer enough usability (in my opinion), this is why I'm developing `aria2p`.

**Purpose**: `aria2c` can run in the foreground, for one-time downloads, or in the background, as a daemon.
This is where `aria2p` intervenes: when an instance of `aria2c` is running in the background,
`aria2p` will be able to communicate with it to add downloads to the queue, remove, pause or resume them, etc.

In order for `aria2p` to be able to communicate with the `aria2c` process, RPC mode must be enabled
with the `--enable-rpc` option of `aria2c`. RPC stands for [Remote Procedure Call][2].
Although `aria2c` supports both JSON-RPC and XML-RPC protocols, `aria2p` **works with JSON only** (not XML).
More information about how to configure `aria2c` to run as a daemon with RPC mode enabled
can be found in the [Configuration section][conf doc] of the documentation.

[conf doc]: https://aria2p.readthedocs.io/en/latest/configuration.html

**Table of contents**

- [Requirements](#requirements)
- [Installation](#installation)
- [Usage as a library](#usage-as-a-library)
- [Usage on the command line](#usage-command-line)
- [Troubleshoot](#troubleshoot)
- [Support](#support)


## Requirements

`aria2p` requires Python 3.6 or above.

<details>
<summary>To install Python 3.6, I recommend using <a href="https://github.com/pyenv/pyenv"><code>pyenv</code></a>.</summary>

```bash
# install pyenv
git clone https://github.com/pyenv/pyenv ~/.pyenv

# setup pyenv (you should also put these three lines in .bashrc or similar)
export PATH="${HOME}/.pyenv/bin:${PATH}"
export PYENV_ROOT="${HOME}/.pyenv"
eval "$(pyenv init -)"

# install Python 3.6
pyenv install 3.6.12

# make it available globally
pyenv global system 3.6.12
```
</details>

You must also install [*aria2*][1]. On systems with `apt-get`:

```bash
sudo apt-get install aria2
```

[1]: https://github.com/aria2/aria2
[2]: https://en.wikipedia.org/wiki/Remote_procedure_call

## Installation

With `pip`:

```bash
python3.6 -m pip install aria2p[tui]
```

With [`pipx`](https://github.com/pipxproject/pipx):

```bash
python3.6 -m pip install --user pipx

pipx install --python python3.6 aria2p[tui]
```

The `tui` extra is needed for the interactive interface. If you don't need the interface (for example when you are
writing a Python package with a dependency to aria2p), simply install `aria2p` without any extra.

## Usage (as a library)

**This library is still a work in progress. More examples will be added later.
In the meantime, you can read the [Reference section](https://aria2p.readthedocs.io/en/latest/reference.html) on the official documentation.**

```python
import aria2p

# initialization, these are the default values
aria2 = aria2p.API(
    aria2p.Client(
        host="http://localhost",
        port=6800,
        secret=""
    )
)

# list downloads
downloads = aria2.get_downloads()

for download in downloads:
    print(download.name, download.download_speed)

# add downloads
magnet_uri = "magnet:?xt=urn:..."

download = aria2.add_magnet(magnet_uri)
```

## Usage (command-line)

```
usage: aria2p [GLOBAL_OPTS...] COMMAND [COMMAND_OPTS...]

Command-line tool and Python library to interact with an `aria2c` daemon
process through JSON-RPC.

Global options:
  -h, --help            Show this help message and exit. Commands also accept
                        the -h/--help option.
  -p PORT, --port PORT  Port to use to connect to the remote server.
  -H HOST, --host HOST  Host address for the remote server.
  -s SECRET, --secret SECRET
                        Secret token to use to connect to the remote server.
  -L {TRACE,DEBUG,INFO,SUCCESS,WARNING,ERROR,CRITICAL}, --log-level {TRACE,DEBUG,INFO,SUCCESS,WARNING,ERROR,CRITICAL}
                        Log level to use
  -P LOG_PATH, --log-path LOG_PATH
                        Log path to use. Can be a directory or a file.
  -T CLIENT_TIMEOUT, --client-timeout CLIENT_TIMEOUT
                        Timeout in seconds for requests to the remote server.
                        Floats supported. Default: 60.0.

Commands:
  
    add                 Add downloads with URIs/Magnets/torrents/Metalinks.
    add-magnets (add-magnet)
                        Add downloads with Magnet URIs.
    add-metalinks (add-metalink)
                        Add downloads with Metalink files.
    add-torrents (add-torrent)
                        Add downloads with torrent files.
    autopurge (autoclear)
                        Automatically purge completed/removed/failed
                        downloads.
    call                Call a remote method through the JSON-RPC client.
    pause (stop)        Pause downloads.
    remove (rm, del, delete)
                        Remove downloads.
    resume (start)      Resume downloads.
    show                Show the download progression.
    top                 Launch the top-like interactive interface.
    listen              Listen to notifications.

```

Calling `aria2p` without any arguments will by default call the `top` command,
which is a console interactive interface.

Commands:


- [`add`](#add)
- [`add-magnets`](#add-magnets)
- [`add-metalinks`](#add-metalinks)
- [`add-torrents`](#add-torrents)
- [`autopurge`](#autopurge)
- [`call`](#call)
- [`listen`](#listen)
- [`pause`](#pause)
- [`remove`](#remove)
- [`resume`](#resume)
- [`show`](#show)
- [`top`](#top)


---

### `add`

```
usage: aria2p add [-h] [-f FROM_FILE] [uris [uris ...]]

Add downloads with URIs/Magnets/torrents/Metalinks.

positional arguments:
  uris                  The URIs/file-paths to add.

optional arguments:
  -h, --help            Show this help message and exit.
  -f FROM_FILE, --from-file FROM_FILE
                        Load URIs from a file.

```



---

### `add-magnets`

```
usage: aria2p add-magnets [-h] [-f FROM_FILE] [uris [uris ...]]

Add downloads with Magnet URIs.

positional arguments:
  uris                  The magnet URIs to add.

optional arguments:
  -h, --help            Show this help message and exit.
  -f FROM_FILE, --from-file FROM_FILE
                        Load URIs from a file.

```



---

### `add-metalinks`

```
usage: aria2p add-metalinks [-h] [-f FROM_FILE]
                            [metalink_files [metalink_files ...]]

Add downloads with Metalink files.

positional arguments:
  metalink_files        The paths to the metalink files.

optional arguments:
  -h, --help            Show this help message and exit.
  -f FROM_FILE, --from-file FROM_FILE
                        Load file paths from a file.

```



---

### `add-torrents`

```
usage: aria2p add-torrents [-h] [-f FROM_FILE]
                           [torrent_files [torrent_files ...]]

Add downloads with torrent files.

positional arguments:
  torrent_files         The paths to the torrent files.

optional arguments:
  -h, --help            Show this help message and exit.
  -f FROM_FILE, --from-file FROM_FILE
                        Load file paths from a file.

```



---

### `autopurge`

```
usage: aria2p autopurge [-h]

Automatically purge completed/removed/failed downloads.

optional arguments:
  -h, --help  Show this help message and exit.

```



---

### `call`

```
usage: aria2p call [-h] [-P PARAMS [PARAMS ...] | -J PARAMS] method

Call a remote method through the JSON-RPC client.

positional arguments:
  method                The method to call (case insensitive). Dashes and
                        underscores will be removed so you can use as many as
                        you want, or none. Prefixes like 'aria2.' or 'system.'
                        are also optional.

optional arguments:
  -h, --help            Show this help message and exit.
  -P PARAMS [PARAMS ...], --params-list PARAMS [PARAMS ...]
                        Parameters as a list of strings.
  -J PARAMS, --json-params PARAMS
                        Parameters as a JSON string. You should always wrap it
                        at least once in an array '[]'.

```

As explained in the help text,
the `method` can be the exact method name,
or just the name without the prefix.
It is case-insensitive, and dashes and underscores will be removed.

The following are all equivalent:
- `aria2.addUri`
- `aria2.adduri`
- `addUri`
- `ADDURI`
- `aria2.ADD-URI`
- `add_uri`
- `A-d_D-u_R-i` (yes it's valid)
- `A---R---I---A---2.a__d__d__u__r__i` (I think you got it)
- and even more ugly forms...

#### Examples
List all available methods.
*This example uses [`jq`](https://github.com/stedolan/jq).*
```console
$ aria2p call listmethods | jq
[
  "aria2.addUri",
  "aria2.addTorrent",
  "aria2.getPeers",
  "aria2.addMetalink",
  "aria2.remove",
  "aria2.pause",
  "aria2.forcePause",
  "aria2.pauseAll",
  "aria2.forcePauseAll",
  "aria2.unpause",
  "aria2.unpauseAll",
  "aria2.forceRemove",
  "aria2.changePosition",
  "aria2.tellStatus",
  "aria2.getUris",
  "aria2.getFiles",
  "aria2.getServers",
  "aria2.tellActive",
  "aria2.tellWaiting",
  "aria2.tellStopped",
  "aria2.getOption",
  "aria2.changeUri",
  "aria2.changeOption",
  "aria2.getGlobalOption",
  "aria2.changeGlobalOption",
  "aria2.purgeDownloadResult",
  "aria2.removeDownloadResult",
  "aria2.getVersion",
  "aria2.getSessionInfo",
  "aria2.shutdown",
  "aria2.forceShutdown",
  "aria2.getGlobalStat",
  "aria2.saveSession",
  "system.multicall",
  "system.listMethods",
  "system.listNotifications"
]
```

List the GIDs (identifiers) of all active downloads.
*Note that we must give the parameters as a JSON string.*
```console
$ aria2p call tellactive -J '[["gid"]]'
[{"gid": "b686cad55029d4df"}, {"gid": "4b39a1ad8fd94e26"}, {"gid": "9d331cc4b287e5df"}, {"gid": "8c9de0df753a5195"}]
```

Pause a download using its GID.
*Note that when a single string argument is required, it can be passed directly with `-P`.*
```console
$ aria2p call pause -P b686cad55029d4df
"b686cad55029d4df"
```

Add a download using magnet URIs.
*This example uses `jq -r` to remove the quotation marks around the result.*
```console
$ aria2p call adduri -J '[["magnet:?xt=urn:..."]]' | jq -r
4b39a1ad8fd94e26f
```

Purge download results (remove completed downloads from the list).
```console
$ aria2p call purge_download_result
"OK"
```

---

### `listen`

```
usage: aria2p listen [-h] [-c CALLBACKS_MODULE] [-t TIMEOUT]
                     [event_types [event_types ...]]

Listen to notifications.

positional arguments:
  event_types           The types of notifications to process: start, pause,
                        stop, error, complete or btcomplete. Example: aria2p
                        listen error btcomplete. Useful if you want to spawn
                        multiple specialized aria2p listener, for example one
                        for each type of notification, but still want to use
                        only one callback file.

optional arguments:
  -h, --help            Show this help message and exit.
  -c CALLBACKS_MODULE, --callbacks-module CALLBACKS_MODULE
                        Path to the Python module defining your notifications
                        callbacks.
  -t TIMEOUT, --timeout TIMEOUT
                        Timeout in seconds to use when waiting for data over
                        the WebSocket at each iteration. Use small values for
                        faster reactivity when stopping to listen.

```



---

### `pause`

```
usage: aria2p pause [-h] [-a] [-f] [gids [gids ...]]

Pause downloads.

positional arguments:
  gids         The GIDs of the downloads to pause.

optional arguments:
  -h, --help   Show this help message and exit.
  -a, --all    Pause all the downloads.
  -f, --force  Pause without contacting servers first.

```



---

### `remove`

```
usage: aria2p remove [-h] [-a] [-f] [gids [gids ...]]

Remove downloads.

positional arguments:
  gids         The GIDs of the downloads to remove.

optional arguments:
  -h, --help   Show this help message and exit.
  -a, --all    Remove all the downloads.
  -f, --force  Remove without contacting servers first.

```



---

### `resume`

```
usage: aria2p resume [-h] [-a] [gids [gids ...]]

Resume downloads.

positional arguments:
  gids        The GIDs of the downloads to resume.

optional arguments:
  -h, --help  Show this help message and exit.
  -a, --all   Resume all the downloads.

```



---

### `show`

```
usage: aria2p show [-h]

Show the download progression.

optional arguments:
  -h, --help  Show this help message and exit.

```



---

### `top`

```
usage: aria2p top [-h]

Launch the top-like interactive interface.

optional arguments:
  -h, --help  Show this help message and exit.

```




## Troubleshooting

- Error outputs like below when using `aria2p` as a Python library:

  ```
  requests.exceptions.ConnectionError: HTTPConnectionPool(host='localhost', port=6800): Max retries exceeded with url: /jsonrpc (Caused by NewConnectionError('<urllib3.connection.HTTPConnection object at 0x1115b1908>: Failed to establish a new connection: [Errno 61] Connection refused',))
  ```

  Solution: `aria2c` needs to be up and running first.

## Support

To support me as an open-source software author,
consider donating or be a supporter through one of the following platforms

- [GitHub](https://github.com/sponsors/pawamoy)
- [Ko-fi](https://www.ko-fi.com/pawamoy)
- [Liberapay](https://liberapay.com/pawamoy/)
- [Patreon](https://www.patreon.com/pawamoy)
- [Paypal](https://www.paypal.me/pawamoy)

Thank you!