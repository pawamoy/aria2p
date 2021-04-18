"""Various exceptions for the TUI."""


class Exit(Exception):
    """A simple exception to exit the interactive interface."""


class TUIError(Exception):
    """The base class for TUI errors."""


class ClickedOutOfBounds(TUIError):
    """User clicked outside of the TUI boundaries."""
