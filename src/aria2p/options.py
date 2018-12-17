class Options:
    def __init__(self, api, struct, gid=None):
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
        return self._struct.get("continue")

    @continue_.setter
    def continue_(self, value):
        if not isinstance(value, str):
            value = str(value)
        if self.api.set_options({"continue": value}, self._gids):
            self._struct["continue"] = value
