# Aria2p
[![pipeline status](https://gitlab.com/pawamoy/aria2p/badges/master/pipeline.svg)](https://gitlab.com/pawamoy/aria2p/commits/master)
[![coverage report](https://gitlab.com/pawamoy/aria2p/badges/master/coverage.svg)](https://gitlab.com/pawamoy/aria2p/commits/master)
[![documentation](https://img.shields.io/readthedocs/aria2p.svg?style=flat)](https://aria2p.readthedocs.io/en/latest/index.html)
[![pypi version](https://img.shields.io/pypi/v/aria2p.svg)](https://pypi.org/project/aria2p/)

Command-line tool and Python library to interact with an `aria2c` daemon process through JSON-RPC.

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
pyenv install 3.6.8

# make it available globally
pyenv global system 3.6.8
```
</details>

## Installation
With `pip`:
```bash
python3.6 -m pip install aria2p
```

With [`pipx`](https://github.com/cs01/pipx):
```bash
# install pipx with the recommended method
curl https://raw.githubusercontent.com/cs01/pipx/master/get-pipx.py | python3

pipx install --python python3.6 aria2p
```

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

Commands:
  
    show                Show the download progression.
    call                Call a remote method through the JSON-RPC client.
    add-magnet          Add a download with a Magnet URI.
    add-torrent         Add a download with a Torrent file.
    add-metalink        Add a download with a Metalink file.
    pause               Pause downloads.
    pause-all           Pause all downloads.
    resume              Resume downloads.
    resume-all          Resume all downloads.
    remove (rm)         Remove downloads.
    remove-all          Remove all downloads.
    purge (clear)       Purge the completed/removed/failed downloads.
```

Calling `aria2p` without any arguments will by default call the `show` command,
which displays the list of current downloads:
```
GID  STATUS  PROGRESS  DOWN_SPEED  UP_SPEED  ETA  NAME
```

There is no interactive mode yet,
but you can use `watch` combined with the `show` subcommand
to see how the downloads progress:

```bash
watch -t -n1 aria2p show
```

Commands help:
- [`show`](#show)
- [`call`](#call)
- [`add-magnet`](#add-magnet)
- [`add-torrent`](#add-torrent)
- [`add-metalink`](#add-metalink)
- [`pause`](#pause)
- [`pause-all`](#pause-all)
- [`resume`](#resume)
- [`resume-all`](#resume-all)
- [`remove (rm)`](#remove)
- [`remove-all`](#remove-all)
- [`purge (clear)`](#purge)

### `show`
```
usage: aria2p show [-h]

Show the download progression.

optional arguments:
  -h, --help  Show this help message and exit.
```

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

As explain in the help text,
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
*Note that when a single string argument is required, it can be passed directly with `-p`.*
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


### `add-magnet`
```
usage: aria2p add-magnet [-h] uri

Add a download with a Magnet URI.

positional arguments:
  uri         The magnet URI to use.

optional arguments:
  -h, --help  Show this help message and exit.
```

### `add-torrent`
```
usage: aria2p add-torrent [-h] torrent_file

Add a download with a Torrent file.

positional arguments:
  torrent_file  The path to the torrent file.

optional arguments:
  -h, --help    Show this help message and exit.
```

### `add-metalink`
```
usage: aria2p add-metalink [-h] metalink_file

Add a download with a Metalink file.

positional arguments:
  metalink_file  The path to the metalink file.

optional arguments:
  -h, --help     Show this help message and exit.
```

### `pause`
```
usage: aria2p pause [-h] [-f] gids [gids ...]

Pause downloads.

positional arguments:
  gids         The GIDs of the downloads to pause.

optional arguments:
  -h, --help   Show this help message and exit.
  -f, --force  Pause without contacting servers first.
```

### `pause-all`
```
usage: aria2p pause-all [-h] [-f]

Pause all downloads.

optional arguments:
  -h, --help   Show this help message and exit.
  -f, --force  Pause without contacting servers first.
```

### `resume`
```
usage: aria2p resume [-h] gids [gids ...]

Resume downloads.

positional arguments:
  gids        The GIDs of the downloads to resume.

optional arguments:
  -h, --help  Show this help message and exit.
```

### `resume-all`
```
usage: aria2p resume-all [-h]

Resume all downloads.

optional arguments:
  -h, --help  Show this help message and exit.
```

### `remove`
```
usage: aria2p remove [-h] [-f] gids [gids ...]

Remove downloads.

positional arguments:
  gids         The GIDs of the downloads to remove.

optional arguments:
  -h, --help   Show this help message and exit.
  -f, --force  Remove without contacting servers first.
```

### `remove-all`
```
usage: aria2p remove-all [-h] [-f]

Remove all downloads.

optional arguments:
  -h, --help   Show this help message and exit.
  -f, --force  Remove without contacting servers first.
```

### `purge`
```
usage: aria2p purge [-h] [gids [gids ...]]

Purge the completed/removed/failed downloads.

positional arguments:
  gids        The GIDs of the downloads to purge.

optional arguments:
  -h, --help  Show this help message and exit.
```
