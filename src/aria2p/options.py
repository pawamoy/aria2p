"""
This module defines the Options class, which holds information retrieved with the ``get_option`` or
``get_global_option`` methods of the client.
"""

from copy import deepcopy


class Options:
    """
    This class holds information retrieved with the ``get_option`` or ``get_global_option`` methods of the client.

    Instances are given a reference to an :class:`aria2p.API` instance to be able to change their values both locally
    and remotely, by using the API client and calling remote methods to change options.

    Please refer to aria2c documentation or man pages to see all the available options.
    """

    def __init__(self, api, struct, download=None):
        """
        Initialization method.

        Args:
            api (:class:`aria2p.API`): the reference to an :class:`api.API` instance.
            struct (dict): a dictionary Python object returned by the JSON-RPC client.
            download (:class:`aria2p.Download`): an optional ``Download`` object
              to inform about the owner, or None to tell they are global options.
        """
        __setattr = super().__setattr__
        __setattr("api", api)
        __setattr("download", download)
        __setattr("_struct", struct)

    @property
    def are_global(self):
        return self.download is None

    def set_owner(self, download=None):
        super().__setattr__("download", download)

    def get_download(self):
        if self._downloads:
            return self._downloads[0]
        return None

    def get_struct(self):
        return deepcopy(self._struct)

    def __getattr__(self, item):
        return self._struct.get(item.replace("_", "-"))

    def __setattr__(self, key, value):
        if not isinstance(value, str):
            value = str(value)
        key = key.replace("_", "-")
        if self.download:
            success = self.api.set_options({key: value}, [self.download])[0]
        else:
            success = self.api.set_global_options({key: value})
        if success:
            self._struct[key] = value

    # Append _ to continue because it is a reserved keyword
    @property
    def continue_(self):
        """Because ``continue`` is a reserved keyword in Python."""
        return self.__getattr__("continue")

    @continue_.setter
    def continue_(self, value):
        self.__setattr__("continue", value)
