"""Module containing the base class for views."""

from typing import Optional

from asciimatics.event import Event

from aria2p.tui.config import Config


class View:
    """The base class for views."""

    def __init__(self, parent_view: Optional["View"] = None) -> None:
        """
        Initialize the object.

        Arguments:
            parent_view: The view's parent view.
        """
        self.parent_view = parent_view

    @property
    def wrapper(self) -> "View":
        """
        Return the root view (the TUI wrapper).

        Returns:
            The wrapper view.
        """
        view = self
        while view.parent_view:
            view = view.parent_view
        return view

    @property
    def style(self) -> Config:
        """
        Return the style configuration.

        Returns:
            The style configuration.
        """
        return self.wrapper.config.style

    @property
    def keybinds(self) -> Config:
        """
        Return the configured key bindings.

        Returns:
            The configured key bindings.
        """
        return self.wrapper.config.keybinds

    def enter(self) -> None:
        """Enter this view."""

    def exit(self) -> None:  # noqa: A003
        """Exit this view."""

    def draw(self) -> None:
        """Draw this view's contents."""

    def process_keyboard_event(self, event: Event) -> None:
        """
        Process a keyboard event.

        Arguments:
            event: The event to process.
        """

    def process_mouse_event(self, event: Event) -> None:
        """
        Process a mouse event.

        Arguments:
            event: The event to process.
        """

    def resize(self, screen) -> None:
        """
        Update after a screen resize.

        Arguments:
            screen: The new screen.
        """

    def update(self) -> bool:
        """
        Update this view's data/contents.

        Returns:
            Whether the data/contents changed.
        """  # noqa: DAR202
