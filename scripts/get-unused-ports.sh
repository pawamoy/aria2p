#!/usr/bin/env bash
used_ports="$(grep -Eo 'port=[0-9]{4}' tests/test_* | cut -d= -f2 | sort -u)"
first_port="$(echo "${used_ports}" | head -n1)"
last_port="$(echo "${used_ports}" | tail -n1)"

python <<EOF
ports = [int(p) for p in """${used_ports}""".split("\n")]
following = False
for port in range(${first_port}, ${last_port} + 2):
    if port not in ports:
        if following:
            print(port)
            following = False
    else:
        following = True
EOF
