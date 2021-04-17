"""This module contains all the code responsible for the HTOP-like interface."""

# Why using asciimatics?
#
# - curses is hard, and not working well on Windows
# - blessings (curses-based) is easier, but does not provide input methods and is not maintained
# - blessed (blessings fork) provides input methods, but they are blocking
# - urwid seems less easy to use than asciimatics, and older
# - clint is not maintained and does not provide input methods
# - prompt_toolkit is designed to build interactive (like, very interactive) command line applications
# - curtsies, pygcurse, unicurses, npyscreen: all based on curses anyway, which does not work well on Windows
#
# Well, asciimatics also provides a "top" example, so...

import os
import sys
import time
from pathlib import Path

from asciimatics.event import KeyboardEvent, MouseEvent
from asciimatics.screen import ManagedScreen
from loguru import logger

from aria2p.api import API
from aria2p.tui.config import load_configuration
from aria2p.tui.errors import Exit
from aria2p.tui.views.base import View
from aria2p.tui.views.main import MainView


class WrapperView(View):
    """
    The main class responsible for drawing the HTOP-like interface.

    It should be instantiated with an API instance, and then ran with its `run` method.

    If you want to re-use this class' code to create an HTOP-like interface for another purpose,
    simply change these few things:

    - columns, columns_order and palettes attributes
    - sort and reverse attributes default values
    - get_data method. It should return a list of objects that can be compared by equality (==, __eq__, __hash__)
    - __init__ method to accept other arguments
    - remove/change the few events with "download" or "self.api" in the process_event method
    """

    def __init__(self, api=None):
        """
        Initialize the object.

        Arguments:
            api (API): An instance of API.
        """
        super().__init__()
        if api is None:
            api = API()

        self.api = api
        self.sleep = 0.005
        self.frames = 200  # 200 * 0.005 seconds == 1 second
        self.frame = 0
        self.refresh = False
        self.screen = None
        self.width = None
        self.height = None
        self.current_view = None
        self.config = load_configuration()

        # reduce curses' 1 second delay when hitting escape to 25 ms
        os.environ.setdefault("ESCDELAY", "25")

        self.enter(MainView(parent_view=self))

    def enter(self, view):
        self.current_view = view
        self.current_view.enter()

    def run(self):
        """The main drawing loop."""
        try:
            # outer loop to support screen resize
            while True:
                with ManagedScreen() as screen:
                    logger.debug(f"Created new screen {screen}")
                    self.resize(screen)
                    self.frame = 0
                    # break (and re-enter) when screen has been resized
                    while not screen.has_resized():
                        # we only refresh when explicitly asked for
                        self.refresh = False

                        # process all events before refreshing screen,
                        # otherwise the reactivity is slowed down a lot with fast inputs
                        event = screen.get_event()
                        while event:
                            logger.debug(f"Got event {event}")
                            # avoid crashing the interface if exceptions occur while processing an event
                            try:
                                self.process_event(event)
                            except Exit:
                                logger.debug(f"Received exit command")
                                return True
                            except Exception as error:
                                # TODO: display error in status bar
                                logger.exception(error)
                            event = screen.get_event()

                        # time to update data and rows
                        if self.frame == 0:
                            logger.debug(f"Tick! Updating data and rows")
                            self.refresh = self.refresh or self.current_view.update()

                        # time to refresh the screen
                        if self.refresh:
                            logger.debug(f"Refresh! Printing text")
                            self.current_view.draw()
                            screen.refresh()

                        # sleep and increment frame
                        time.sleep(self.sleep)
                        self.frame = (self.frame + 1) % self.frames
                    logger.debug("Screen was resized")
        except Exception as error:
            logger.exception(error)
            return False

    def process_event(self, event):
        """
        Process an event.

        For reactivity purpose, this method should not compute expensive stuff, only change the view of the interface,
        changes that will be applied by update_data and update_rows methods.

        Arguments:
            event (KeyboardEvent/MouseEvent): The event to process.
        """
        if isinstance(event, KeyboardEvent):
            self.current_view.process_keyboard_event(event)

        elif isinstance(event, MouseEvent):
            self.current_view.process_mouse_event(event)

    def resize(self, screen):
        """Set the screen object, its scroller wrapper, width, height, and columns bounds."""
        self.screen = screen
        self.height, self.width = screen.dimensions
        self.current_view.resize(screen)
        reapply_pywal_theme()


def reapply_pywal_theme():
    wal_sequences = Path.home() / ".cache" / "wal" / "sequences"
    try:
        with wal_sequences.open("rb") as fd:
            contents = fd.read()
            sys.stdout.buffer.write(contents)
    except Exception:  # nosec
        pass
