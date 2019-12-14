<!--
IMPORTANT: This file is generated from the template at 'scripts/templates/README.md'.
           Please update the template instead of this file.
-->

# aria2p
[![pipeline status](https://gitlab.com/pawamoy/aria2p/badges/master/pipeline.svg)](https://gitlab.com/pawamoy/aria2p/commits/master)
[![coverage report](https://gitlab.com/pawamoy/aria2p/badges/master/coverage.svg)](https://gitlab.com/pawamoy/aria2p/commits/master)
[![documentation](https://img.shields.io/readthedocs/aria2p.svg?style=flat)](https://aria2p.readthedocs.io/en/latest/index.html)
[![pypi version](https://img.shields.io/pypi/v/aria2p.svg)](https://pypi.org/project/aria2p/)
[![Gitter](https://badges.gitter.im/aria2p/community.svg)](https://gitter.im/aria2p/community?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge)
[![support](https://img.shields.io/badge/sponsor-or%20donate-blue.svg?style=flat)](#support)

Command-line tool and Python library to interact with an [`aria2c`][1] daemon process through JSON-RPC.

![demo](demo.svg)

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
pyenv install 3.6.8

# make it available globally
pyenv global system 3.6.8
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
{{ main_usage }}
```

Calling `aria2p` without any arguments will by default call the `top` command,
which is a console interactive interface.

Commands:
{% for command in commands %}
- [`{{ command.name }}`](#{{ command.name }}){% endfor %}

{% for command in commands %}
---

### `{{ command.name }}`
```
{{ command.usage }}
```

{% include "command_" + command.name.replace("-", "_") + "_extra.md" ignore missing %}
{% endfor %}

## Troubleshoot
- Error outputs like below when using `aria2p` as a Python library:

  ```
  requests.exceptions.ConnectionError: HTTPConnectionPool(host='localhost', port=6800): Max retries exceeded with url: /jsonrpc (Caused by NewConnectionError('<urllib3.connection.HTTPConnection object at 0x1115b1908>: Failed to establish a new connection: [Errno 61] Connection refused',))
  ```

  Solution: `aria2c` needs to be up and running first.

## Support
To support this project,
consider donating through one of the following platforms:
- [Beerpay](https://beerpay.io/pawamoy/aria2p)

To support me as an open-source software author,
consider donating or be a supporter through one of the following platforms:
- [GitHub](https://github.com/sponsors/pawamoy)
- [Ko-fi](https://www.ko-fi.com/pawamoy)
- [Liberapay](https://liberapay.com/pawamoy/)
- [Patreon](https://www.patreon.com/pawamoy)
- [Paypal](https://www.paypal.me/pawamoy)

Thank you!
