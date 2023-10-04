"""Port-related utilities."""

import re
import sys
from collections import defaultdict
from os import listdir
from os.path import isfile, join
from pathlib import Path


def get_ports() -> dict[int, list[int]]:  # noqa: D103
    port_regex = re.compile(r"port=[0-9]{4}")
    test_files = [Path("tests") / f for f in listdir("tests") if isfile(join("tests", f))]
    used_ports = defaultdict(list)
    for test_file in test_files:
        with test_file.open() as test_code:
            for lineno, line in enumerate(test_code, 1):
                match = port_regex.search(line)
                if match:
                    port = int(match.group().replace("port=", ""))
                    used_ports[port].append((str(test_file), lineno, line.strip()))
    return used_ports


def check(ports: dict[int, list[int]]) -> int:  # noqa: D103
    check_ok = True
    for port, matches in ports.items():
        if port in blacklisted_ports:
            check_ok = False
            print(f"--- port {port} is blacklisted, don't use it!")
            print(f"--- reason: {blacklisted_ports[port]}")
            print(f"--- suggestion: port {next_unused(port)}")
            for path, lineno, line in matches:
                print(f"{path}:{lineno}: {line}", file=sys.stderr)
            print()
        if len(matches) > 1:
            check_ok = False
            print(f"--- port {port} used in multiple locations", file=sys.stderr)
            for path, lineno, line in matches:
                print(f"{path}:{lineno}: {line}", file=sys.stderr)
    return 0 if check_ok else 1


def get_unused(ports: dict[int, list[int]]) -> list[int]:  # noqa: D103
    finalists = []
    sorted_ports = sorted(ports.keys())
    following = False
    for candidate in range(sorted_ports[0], sorted_ports[-1] + 2):
        if candidate not in sorted_ports:
            if following and candidate not in blacklisted_ports:
                finalists.append(candidate)
                following = False
        else:
            following = True
    return finalists


def next_unused(port: int) -> int | None:  # noqa: D103
    for next_port in unused_ports:
        if next_port > port:
            return next_port
    return None


if __name__ == "__main__":
    blacklisted_ports = {7616: "Used by TCP/UDP"}
    used_ports = get_ports()
    unused_ports = get_unused(used_ports)
    args = sys.argv
    if len(args) > 1:
        arg = args[1]
        if arg == "check":
            sys.exit(check(used_ports))
        elif arg == "get":
            for port in unused_ports:
                print(port)
            sys.exit(0)
    else:
        print("usage: python scripts/ports.py get|check", file=sys.stderr)
        sys.exit(1)
