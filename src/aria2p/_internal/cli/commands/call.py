# SPDX-License-Identifier: ISC
#
# ISC License
#
# Copyright (c) 2020, Timothée Mazzucotelli and contributors
#
# Permission to use, copy, modify, and/or distribute this software for any
# purpose with or without fee is hereby granted, provided that the above
# copyright notice and this permission notice appear in all copies.
#
# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
# WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
# ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
# WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
# ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
# OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.

# Command to call RPC methods.

from __future__ import annotations

import json
import sys
from typing import TYPE_CHECKING, Any

from aria2p._internal.client import Client

if TYPE_CHECKING:
    from aria2p._internal.api import API


def get_method(name: str) -> str | None:
    """Return the actual aria2 method name from a differently formatted name.

    Parameters:
        name: A method name.

    Returns:
        The real method name.
    """
    methods = {}

    for method in Client.METHODS:
        methods[method.lower()] = method
        methods[method.split(".")[1].lower()] = method

    name = name.lower()
    name = name.replace("-", "")
    name = name.replace("_", "")

    return methods.get(name)


def call(api: API, method: str, params: str | list[str]) -> int:
    """Call subcommand.

    Parameters:
        api: The API instance to use.
        method: Name of the method to call.
        params: Parameters to use when calling method.

    Returns:
        int: Always 0.
    """
    real_method = get_method(method)

    if real_method is None:
        print(f"aria2p: call: Unknown method {method}.", file=sys.stderr)
        print("  Run 'aria2p call listmethods' to list the available methods.", file=sys.stderr)
        return 1

    call_params: list[Any]
    if isinstance(params, str):
        call_params = json.loads(params)
    elif params is None:
        call_params = []
    else:
        call_params = params

    response = api.client.call(real_method, call_params)
    print(json.dumps(response))

    return 0
