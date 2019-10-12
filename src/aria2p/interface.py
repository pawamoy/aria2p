"""
This module contains all the code responsible for the HTOP-like interface.
"""

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

# pylint: disable=invalid-name

import time
from collections import defaultdict

from asciimatics.event import KeyboardEvent, MouseEvent
from asciimatics.screen import ManagedScreen, Screen
from loguru import logger

from .api import API


class Keys:
    """The actions and their shortcuts keys."""

    HELP = [ord("h"), Screen.KEY_F1]
    SETUP = [Screen.KEY_F2]
    TOGGLE_RESUME_PAUSE = [ord(" ")]
    PRIORITY_UP = [ord("u"), ord("["), Screen.KEY_F7]
    PRIORITY_DOWN = [ord("d"), ord("]"), Screen.KEY_F8]
    REVERSE_SORT = [ord("I")]
    NEXT_SORT = [ord("n"), ord(">")]
    PREVIOUS_SORT = [ord("p"), ord("<")]
    SELECT_SORT = [Screen.KEY_F6]
    REMOVE_ASK = [Screen.KEY_DELETE, Screen.KEY_F9]
    TOGGLE_EXPAND_COLLAPSE = [ord("x")]
    TOGGLE_EXPAND_COLLAPSE_ALL = [ord("X")]
    AUTOCLEAR = [ord("c")]
    FOLLOW_ROW = [ord("F")]
    SEARCH = [ord("/"), Screen.KEY_F3]
    FILTER = [ord("\\"), Screen.KEY_F4]
    TOGGLE_SELECT = [ord("s")]
    UN_SELECT_ALL = [ord("U")]
    QUIT = [ord("q"), ord("Q"), Screen.KEY_F10]
    MOVE_UP = [Screen.KEY_UP]
    MOVE_DOWN = [Screen.KEY_DOWN]
    MOVE_LEFT = [Screen.KEY_LEFT]
    MOVE_RIGHT = [Screen.KEY_RIGHT]


class Exit(Exception):
    """A simple exception to exit the interactive interface."""


class Column:
    """
    A class to specify a column in the interface.

    It's composed of a header (the string to display on top), a padding (how to align the text),
    and three callable functions to get the text from a Download object, to sort between downloads,
    and to get a color palette based on the text.
    """

    def __init__(self, header, padding, get_text, get_sort, get_palette):
        """
        Initialization method.

        Args:
            header (str): The string to display on top.
            padding (str): How to align the text.
            get_text (func): Function accepting a Download as argument and returning the text to display.
            get_sort (func): Function accepting a Download as argument and returning the attribute used to sort.
            get_palette (func): Function accepting text as argument and returning a palette or a palette identifier.
        """
        self.header = header
        self.padding = padding
        self.get_text = get_text
        self.get_sort = get_sort
        self.get_palette = get_palette


class OffsetPrinter:
    """
    A wrapper around asciimatics' Screen.print_at and Screen.paint methods.

    It allows to print the rows with an horizontal offset, used when moving left and right:
    the first OFFSET characters will not be printed.
    """

    def __init__(self, screen, offset=0):
        """
        Initialization method.

        Args:
            screen (Screen): The asciimatics screen object.
            offset (int): Base offset to use when printing. Will decrease by one with each character skipped.
        """
        self.screen = screen
        self.offset = offset

    def set_offset(self, offset):
        """Set the offset."""
        self.offset = offset

    def print_at(self, text, x, y, palette):
        """
        Wrapper print_at method.

        Args:
            text (str): Text to print.
            x (int): X axis position / column.
            y (int): Y axis position / row.
            palette (list/tuple): A length-3 tuple or a list of length-3 tuples representing asciimatics palettes.

        Returns:
            int: The number of characters actually printed.
        """
        logger.debug(f"Printing following text with offset={self.offset}")
        logger.debug(text)
        if self.offset == 0:
            if isinstance(palette, list):
                self.screen.paint(text, x, y, colour_map=palette)
            else:
                self.screen.print_at(text, x, y, *palette)
            written = len(text)
        else:
            text_length = len(text)
            if text_length > self.offset:
                new_text = text[self.offset :]
                written = len(new_text)
                if isinstance(palette, list):
                    new_palette = palette[self.offset :]
                    self.screen.paint(new_text, x, y, colour_map=new_palette)
                else:
                    self.screen.print_at(new_text, x, y, *palette)
                self.offset = 0
            elif text_length == self.offset:
                self.offset = 0
                written = 0
            else:
                self.offset -= text_length
                written = 0
        return written


class Palette:
    """A simple class to hold palettes getters."""

    @staticmethod
    def status(value):
        """Return the palette for a STATUS cell."""
        return "status_" + value

    @staticmethod
    def name(value):
        """Return the palette for a NAME cell."""
        if value.startswith("[METADATA]"):
            return (
                [(Screen.COLOUR_GREEN, Screen.A_UNDERLINE, Screen.COLOUR_BLACK)] * 10
                + [Interface.palettes["metadata"]] * (len(value.strip()) - 10)
                + [Interface.palettes["row"]]
            )
        return "name"


# TODO: allow drawing of a separate column on the left, for interactive picking of options,
# for example when removing a download: asking whether to force and/or remove files as well.
# I.e. adding a global horizontal offset.

# TODO: allow other interfaces to be drawn, like the setup menu or the help menu
# TODO: allow vertical offset to be able to draw chart and stats above the table.


class Interface:
    """
    The main class responsible of drawing the HTOP-like interface.

    It should be instantiated with an API instance, and then ran with its ``run`` method.

    If you want to re-use this class' code to create an HTOP-like interface for another purpose,
    simply change these few things:

    - columns, columns_order and palettes attributes
    - sort and reverse attributes default values
    - get_data method. It should return a list of objects that can be compared by equality (==, __eq__, __hash__)
    - __init__ method to accept other arguments
    - remove/change the few events with "download" or "self.api" in the process_event method
    """

    sleep = 0.005
    frames = 200  # 200 * 0.005 seconds == 1 second
    frame = 0
    focused = 0
    sort = 2
    reverse = True
    x_offset = 0
    row_offset = 0
    refresh = False
    width = None
    height = None
    screen = None
    data = []
    rows = []
    printer = None
    follow = None
    bounds = []

    palettes = defaultdict(lambda: (Screen.COLOUR_WHITE, Screen.A_NORMAL, Screen.COLOUR_BLACK))
    palettes.update(
        {
            "header": (Screen.COLOUR_BLACK, Screen.A_NORMAL, Screen.COLOUR_GREEN),
            "focused_header": (Screen.COLOUR_BLACK, Screen.A_NORMAL, Screen.COLOUR_CYAN),
            "focused_row": (Screen.COLOUR_BLACK, Screen.A_NORMAL, Screen.COLOUR_CYAN),
            "status_active": (Screen.COLOUR_CYAN, Screen.A_NORMAL, Screen.COLOUR_BLACK),
            "status_paused": (Screen.COLOUR_YELLOW, Screen.A_NORMAL, Screen.COLOUR_BLACK),
            "status_waiting": (Screen.COLOUR_WHITE, Screen.A_BOLD, Screen.COLOUR_BLACK),
            "status_error": (Screen.COLOUR_RED, Screen.A_BOLD, Screen.COLOUR_BLACK),
            "status_complete": (Screen.COLOUR_GREEN, Screen.A_NORMAL, Screen.COLOUR_BLACK),
            "metadata": (Screen.COLOUR_WHITE, Screen.A_UNDERLINE, Screen.COLOUR_BLACK),
        }
    )

    columns_order = ["gid", "status", "progress", "size", "down_speed", "up_speed", "eta", "name"]
    columns = {
        "gid": Column(
            header="GID", padding=">16", get_text=lambda d: d.gid, get_sort=lambda d: d.gid, get_palette=lambda d: "gid"
        ),
        "status": Column(
            header="STATUS",
            padding="<9",
            get_text=lambda d: d.status,
            get_sort=lambda d: d.status,
            get_palette=Palette.status,
        ),
        "progress": Column(
            header="PROGRESS",
            padding=">8",
            get_text=lambda d: d.progress_string(),
            get_sort=lambda d: d.progress,
            get_palette=lambda s: "progress",
        ),
        "size": Column(
            header="SIZE",
            padding=">11",
            get_text=lambda d: d.total_length_string(),
            get_sort=lambda d: d.total_length,
            get_palette=lambda s: "size",
        ),
        "down_speed": Column(
            header="DOWN_SPEED",
            padding=">13",
            get_text=lambda d: d.download_speed_string(),
            get_sort=lambda d: d.download_speed,
            get_palette=lambda s: "down_speed",
        ),
        "up_speed": Column(
            header="UP_SPEED",
            padding=">13",
            get_text=lambda d: d.upload_speed_string(),
            get_sort=lambda d: d.upload_speed,
            get_palette=lambda s: "up_speed",
        ),
        "eta": Column(
            header="ETA",
            padding=">8",
            get_text=lambda d: d.eta_string(precision=2),
            get_sort=lambda d: d.eta,
            get_palette=lambda s: "eta",
        ),
        "name": Column(
            header="NAME",
            padding="100%",
            get_text=lambda d: d.name,
            get_sort=lambda d: d.name,
            get_palette=Palette.name,
        ),
    }

    def __init__(self, api=None):
        """
        Initialization method.

        Args:
            api (API): An instance of API.
        """
        if api is None:
            api = API()
        self.api = api

    def run(self):
        """The main drawing loop."""
        try:
            # outer loop to support screen resize
            while True:
                with ManagedScreen() as screen:
                    self.set_screen(screen)
                    self.frame = 0
                    # break (and re-enter) when screen has been resized
                    while not screen.has_resized():
                        # keep previous sort in memory to know if we have to re-sort the rows
                        # once all events are processed (to avoid useless/redundant sort passes)
                        previous_sort = (self.sort, self.reverse)

                        # we only refresh when explicitly asked for
                        self.refresh = False

                        # process all events before refreshing screen,
                        # otherwise the reactivity is slowed down a lot with fast inputs
                        event = screen.get_event()
                        while event:
                            self.process_event(event)
                            event = screen.get_event()

                        # time to update data and rows
                        if self.frame == 0:
                            self.update_data()
                            self.refresh = True

                        # time to refresh the screen
                        if self.refresh:
                            # sort if needed, unless it was just done at frame 0 when updating rows
                            if (self.sort, self.reverse) != previous_sort and self.frame != 0:
                                self.update_rows()

                            # actual printing and screen refresh
                            self.print_headers()
                            self.print_rows()
                            screen.refresh()

                        # sleep and increment frame
                        time.sleep(self.sleep)
                        self.frame = (self.frame + 1) % self.frames
        except Exit:
            pass

    def process_event(self, event):
        """
        Process an event.

        For reactivity purpose, this method should not compute expensive stuff, only change the state of the interface,
        changes that will be applied by update_data and update_rows methods.

        Args:
            event (KeyboardEvent/MouseEvent): The event to process.
        """
        if event is None:
            return

        if isinstance(event, KeyboardEvent):

            if event.key_code in Keys.MOVE_UP:
                if self.focused > 0:
                    self.focused -= 1
                    if self.focused < self.row_offset:
                        self.row_offset = self.focused
                    elif self.focused >= self.row_offset + (self.height - 1):
                        # happens when shrinking height
                        self.row_offset = self.focused + 1 - (self.height - 1)
                    self.follow = None
                    self.refresh = True

            elif event.key_code in Keys.MOVE_DOWN:
                if self.focused < len(self.rows) - 1:
                    self.focused += 1
                    if self.focused - self.row_offset >= (self.height - 1):
                        self.row_offset = self.focused + 1 - (self.height - 1)
                    self.follow = None
                    self.refresh = True

            elif event.key_code in Keys.MOVE_LEFT:
                if self.x_offset > 0:
                    self.x_offset = max(0, self.x_offset - 5)
                    self.refresh = True

            elif event.key_code in Keys.MOVE_RIGHT:
                self.x_offset += 5
                self.refresh = True

            elif event.key_code in Keys.HELP:
                pass  # TODO

            elif event.key_code in Keys.SETUP:
                pass  # TODO

            elif event.key_code in Keys.TOGGLE_RESUME_PAUSE:
                download = self.data[self.focused]
                if download.is_active or download.is_waiting:
                    download.pause()
                elif download.is_paused:
                    download.resume()

            elif event.key_code in Keys.PRIORITY_UP:
                download = self.data[self.focused]
                if not download.is_active:
                    download.move_up()
                    self.follow = download

            elif event.key_code in Keys.PRIORITY_DOWN:
                download = self.data[self.focused]
                if not download.is_active:
                    download.move_down()
                    self.follow = download

            elif event.key_code in Keys.REVERSE_SORT:
                self.reverse = not self.reverse
                self.refresh = True

            elif event.key_code in Keys.NEXT_SORT:
                if self.sort < len(self.columns) - 1:
                    self.sort += 1
                    self.refresh = True

            elif event.key_code in Keys.PREVIOUS_SORT:
                if self.sort > 0:
                    self.sort -= 1
                    self.refresh = True

            elif event.key_code in Keys.SELECT_SORT:
                pass  # TODO

            elif event.key_code in Keys.REMOVE_ASK:
                pass  # TODO

            elif event.key_code in Keys.TOGGLE_EXPAND_COLLAPSE:
                pass  # TODO

            elif event.key_code in Keys.TOGGLE_EXPAND_COLLAPSE_ALL:
                pass  # TODO

            elif event.key_code in Keys.AUTOCLEAR:
                self.api.autopurge()

            elif event.key_code in Keys.FOLLOW_ROW:
                self.follow = self.data[self.focused]

            elif event.key_code in Keys.SEARCH:
                pass  # TODO

            elif event.key_code in Keys.FILTER:
                pass  # TODO

            elif event.key_code in Keys.TOGGLE_SELECT:
                pass  # TODO

            elif event.key_code in Keys.UN_SELECT_ALL:
                pass  # TODO

            elif event.key_code in Keys.QUIT:
                raise Exit()

        elif isinstance(event, MouseEvent):

            if event.buttons & MouseEvent.LEFT_CLICK:
                if event.y == 0:
                    new_sort = self.get_column_at_x(event.x)
                    if new_sort == self.sort:
                        self.reverse = not self.reverse
                    else:
                        self.sort = new_sort
                else:
                    self.focused = min(event.y - 1 + self.row_offset, len(self.rows) - 1)
                self.refresh = True

            # elif event.buttons & MouseEvent.RIGHT_CLICK:
            #     pass  # TODO: expand/collapse

    def print_headers(self):
        """Print the headers (columns names)."""
        self.printer.set_offset(self.x_offset)
        x, y, c = 0, 0, 0

        for column_name in self.columns_order:
            column = self.columns[column_name]
            palette = self.palettes["focused_header"] if c == self.sort else self.palettes["header"]

            if column.padding == "100%":
                header_string = f"{column.header}"
                fill_up = " " * max(0, self.width - x - len(header_string))
                written = self.printer.print_at(header_string, x, y, palette)
                self.printer.print_at(fill_up, x + written, y, self.palettes["header"])

            else:
                header_string = f"{column.header:{column.padding}} "
                written = self.printer.print_at(header_string, x, y, palette)

            x += written
            c += 1

    def print_rows(self):
        """Print the rows."""
        y = 1
        for row in self.rows[self.row_offset : self.row_offset + self.height]:

            self.printer.set_offset(self.x_offset)
            x = 0

            for i, column_name in enumerate(self.columns_order):
                column = self.columns[column_name]
                padding = f"<{max(0, self.width - x)}" if column.padding == "100%" else column.padding

                if self.focused == y - 1 + self.row_offset:
                    palette = self.palettes["focused_row"]
                else:
                    palette = column.get_palette(row[i])
                    if isinstance(palette, str):
                        palette = self.palettes[palette]

                field_string = f"{row[i]:{padding}} "
                written = self.printer.print_at(field_string, x, y, palette)
                x += written

            y += 1

        for i in range(self.height - y):
            self.screen.print_at(" " * self.width, 0, y + i)

    def get_column_at_x(self, x):
        """For an horizontal position X, return the column index."""
        for i, bound in enumerate(self.bounds):
            if bound[0] <= x <= bound[1]:
                return i
        raise ValueError

    def set_screen(self, screen):
        """Set the screen object, its printer wrapper, width, height, and columns bounds."""
        self.screen = screen
        self.height, self.width = screen.dimensions
        self.printer = OffsetPrinter(screen)
        self.bounds = []
        for column_name in self.columns_order:
            column = self.columns[column_name]
            if column.padding == "100%":
                self.bounds.append((self.bounds[-1][1] + 1, self.width))
            else:
                padding = int(column.padding.lstrip("<>=^"))
                if not self.bounds:
                    self.bounds = [(0, padding)]
                else:
                    self.bounds.append((self.bounds[-1][1] + 1, self.bounds[-1][1] + 1 + padding))

    def get_data(self):
        """Return a list of objects."""
        return self.api.get_downloads()

    def update_data(self):
        """Set the interface data and rows contents."""
        self.data = self.sort_data(self.get_data())
        self.update_rows()

    def sort_data(self, data):
        """Sort data according to interface state."""
        sort_function = self.columns[self.columns_order[self.sort]].get_sort
        return sorted(data, key=sort_function, reverse=self.reverse)

    def update_rows(self):
        """Update rows contents according to interface state."""
        text_getters = [self.columns[c].get_text for c in self.columns_order]
        n_columns = len(self.columns_order)
        self.rows = [tuple(text_getters[i](item) for i in range(n_columns)) for item in self.data]
        if self.follow:
            self.focused = self.data.index(self.follow)
