<!--
IMPORTANT: This file is generated from the template at 'scripts/templates/README.md'.
           Please update the template instead of this file.
-->

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
{{ main_usage }}
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

Commands:
{% for command in commands %}
- [`{{ command.name }}`](#{{ command.name }}){% endfor %}

{% for command in commands %}
### `{{ command.name }}`
```
{{ command.usage }}
```

{% include "command_" + command.name.replace("-", "_") + "_extra.md" ignore missing %}
{% endfor %}
