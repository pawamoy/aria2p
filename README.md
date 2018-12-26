# Aria2p
Command-line tool and Python library to interact with an `aria2c` daemon process through JSON-RPC.

## Requirements
`aria2p` requires Python 3.6 or above.

<details>
<summary>To install Python 3.6, I recommend using <a href="https://github.com/pyenv/pyenv"><code>pyenv</code></a>.</summary>

```bash
# install pyenv
git clone https://github.com/pyenv/pyenv ~/.pyenv

# setup pyenv (you should also put these two lines in .bashrc or similar)
export PATH="${HOME}/.pyenv/bin:${PATH}"
eval "$(pyenv init -)"

# install Python 3.6
pyenv install 3.6.7

# make it available globally
pyenv global system 3.6.7
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
**This library is still a work in progress. Some things listed here might not be implemented yet.**
```python
import aria2p

# initialization, these are the default values
aria2 = aria2p.API(
    aria2p.JSONRPCClient(
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
For now, the command-line tool can only call methods using the client.
More options directly using the API will come later.

```bash
aria2p -m,--method METHOD_NAME [-p,--params PARAMS... | -j,--json-params JSON_STRING]
```

The `METHOD_NAME` can be the exact method name, or just the name without the prefix.
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

Calling `aria2p` without any arguments will simply display the list of current downloads:
```
GID  STATUS  PROGRESS  DOWN_SPEED  UP_SPEED  ETA  NAME
```

There is no interactive mode yet, but you can use `watch` to see how the downloads progress:
```bash
watch -d -t -n1 aria2p
```

### Examples
List all available methods.
*This example uses [`jq`](https://github.com/stedolan/jq).*
```console
$ aria2p -m listmethods | jq
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
$ aria2p -m tellactive -j '[["gid"]]'
[{"gid": "b686cad55029d4df"}, {"gid": "4b39a1ad8fd94e26"}, {"gid": "9d331cc4b287e5df"}, {"gid": "8c9de0df753a5195"}]
```

Pause a download using its GID.
*Note that when a single string argument is required, it can be passed directly with `-p`.*
```console
$ aria2p -m pause -p b686cad55029d4df
"b686cad55029d4df"
```

Add a download using magnet URIs.
*This example uses `jq -r` to remove the quotation marks around the result.*
```console
$ aria2p -m adduri -j '[["magnet:?xt=urn:..."]]' | jq -r
4b39a1ad8fd94e26f
```

Purge download results (remove completed downloads from the list).
```console
$ aria2p -m purge_download_result
"OK"
```
