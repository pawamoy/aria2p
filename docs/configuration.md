# Configuration
In this section we will see how to:
- write a configuration file for `aria2c`
- write an `init.d` script to be able to run our `aria2c` daemon as a system service
- pass the right option to `aria2p` to connect to the right `aria2c` instance

## `aria2c`
By default, aria2 checks whether the legacy path `$HOME/.aria2/aria2.conf` is present,
otherwise it parses `$XDG_CONFIG_HOME/aria2/aria2.conf` as its configuration file.

You can specify the path to configuration file using `--conf-path` option.
If you don't want to use the configuration file, use `--no-conf` option.

**Comprehensive documentation about the format of the configuration file can be found in the man page of `aria2c`.**

Here is an example of configuration:

```
continue=true
daemon=true
dir=$HOME/Downloads
enable-rpc=true
file-allocation=falloc
force-save=true
input-file=$HOME/.config/aria2/session.txt
log=$HOME/.config/aria2/aria2.log
log-level=notice
max-concurrent-downloads=2
max-tries=5
retry-wait=30
rpc-listen-all=true
rpc-listen-port=6801
rpc-secret=HeLLo
save-session=$HOME/.config/aria2/session.txt
save-session-interval=20
timeout=600
```

This configuration says to start in daemon mode, with RPC mode enabled and listening on port 6801
(default is 6800), with HeLLo as secret token.
The session is loaded from $HOME/.config/.aria2/session.txt, and saved in the same file.
This session file is used to retain download information between reboots, so you can resume them.
Other options are self-describing. Read the man page for more explanations, and to see the complete list of options.

With this configuration file, you would now start your `aria2c` daemon with:

```bash
aria2c --conf-path=$HOME/.config/aria2/aria2.conf
```

## `init.d` script
I currently use this script, but am planning to improve it. Copy it as `/etc/init.d/aria2server`.

With this script you will be able to start aria2 like a service with
`sudo service aria2server start`.

You must update the `CONF_PATH` variable to match your username.

```bash
#!/bin/bash
# /etc/init.d/aria2server

### BEGIN INIT INFO
# Provides: aria2server
# Required-Start:    $network $local_fs $remote_fs
# Required-Stop:     $network $local_fs $remote_fs
# Default-Start:     2 3 4 5
# Default-Stop:      0 1 6
# Short-Description: aria2 RPC server init script.
# Description: Starts and stops aria2 RPC server.
### END INIT INFO

#VAR
RUN="/usr/bin/aria2c"
CONF_PATH="/home/user/.config/aria2/aria2.conf"
ARIA_PID=$(ps ux | awk "/aria2c --conf-path=${CONF_PATH//\//\\/}/ && !/awk/ {print \$2}")

# Some things that run always
touch /var/lock/aria2cRPC

# Carry out specific functions when asked to by the system
case "$1" in
  start)
    echo "Starting script aria2cRPC "
    if [ -z "$ARIA_PID" ]; then
      nohup $RUN --conf-path=$CONF_PATH
      echo "Started"
    else
      echo "aria2server already started"
    fi
  ;;
  stop)
    echo "Stopping script aria2server"
    if [ ! -z "$ARIA_PID" ]; then
      kill $ARIA_PID
    fi
    echo "OK"
  ;;
  status)
    if [ ! -z "$ARIA_PID" ]; then
      echo "The aria2server is running with PID = "$ARIA_PID
    else
      echo "No process found for aria2server"
    fi
  ;;
  *)
    echo "Usage: /etc/init.d/aria2server {start|stop|status}"
    exit 1
  ;;
esac

exit 0
```

## `aria2p`
For now, `aria2p` does not read any configuration file. Options are simply passed on the command-line.
Based on the previous configuration, you should run `aria2p` like this:

```bash
aria2p --secret "HeLLo" --port 6801 show
```
