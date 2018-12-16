# Aria2p
Command-line tool and Python library to interact with an `aria2c` daemon process through JSON-RPC.

## Installation
No packaging yet.
Clone the repo and install `requests` with `[sudo] pip install requests`,
or create a dedicated Python virtualenv with **Python 3.6**.

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
./aria2p.py -m,--method METHOD_NAME [-p,--params PARAMS... | -j,--json-params JSON_STRING]
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

### Examples
List all available methods.
*This example uses [`jq`](https://github.com/stedolan/jq).*
```console
$ ./aria2p.py -m listmethods | jq
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
$ ./aria2p.py -m tellactive -j '[["gid"]]'
[{"gid": "b686cad55029d4df"}, {"gid": "4b39a1ad8fd94e26"}, {"gid": "9d331cc4b287e5df"}, {"gid": "8c9de0df753a5195"}]
```

Pause a download using its GID.
*Note that when a single string argument is required, it can be passed directly with `-p`.*
```console
$ ./aria2p.py -m pause -p b686cad55029d4df
"b686cad55029d4df"
```

Add a download using magnet URIs.
*This example uses `jq -r` to remove the quotation marks around the result.*
```console
$ ./aria2p.py -m adduri -j '[["magnet:?xt=urn:..."]]' | jq -r
4b39a1ad8fd94e26f
```

Purge download results (remove completed downloads from the list).
```console
$ ./aria2p.py -m purge_download_result
"OK"
```
