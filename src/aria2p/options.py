"""
This module defines the Options class, which holds information retrieved with the ``get_option`` or
``get_global_option`` methods of the client.
"""


class Options:
    """
    This class holds information retrieved with the ``get_option`` or ``get_global_option`` methods of the client.

    Instances are given a reference to an :class:`api.API` instance to be able to change their values both locally
    and remotely, by using the API client and calling remote methods to change options.

    Please refer to aria2c documentation or man pages to see all the available options.
    """

    def __init__(self, api, struct, gid=None):
        """
        Initialization method.

        Args:
            api (:class:`api.API`): the reference to an :class:`api.API` instance.
            struct (dict): a dictionary Python object returned by the JSON-RPC client.
            gid (str): an optional GID to inform about the owner (:class:`downloads.Download`), or None to tell they
                are global options.
        """
        __setattr = super().__setattr__
        __setattr("api", api)
        __setattr("_gids", [gid] if gid else [])
        __setattr("_struct", struct)

    def __getattr__(self, item):
        return self._struct.get(item.replace("_", "-"))

    def __setattr__(self, key, value):
        if not isinstance(value, str):
            value = str(value)
        key = key.replace("_", "-")
        if self.api.set_options({key: value}, self._gids):
            self._struct[key] = value

    # Append _ to continue because it is a reserved keyword
    @property
    def continue_(self):
        """Because ``continue`` is a reserved keyword in Python."""
        return self._struct.get("continue")

    @continue_.setter
    def continue_(self, value):
        if not isinstance(value, str):
            value = str(value)
        if self.api.set_options({"continue": value}, self._gids):
            self._struct["continue"] = value
