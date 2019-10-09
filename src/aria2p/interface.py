"""
This module contains all the top-like interface code.
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

import time
from collections import defaultdict

from asciimatics.event import KeyboardEvent, MouseEvent
from asciimatics.screen import ManagedScreen, Screen
from loguru import logger

from .api import API


class Exit(Exception):
    pass


class Column:
    def __init__(self, header, padding, get_text, get_sort, get_palette):
        self.header = header
        self.padding = padding
        self.get_text = get_text
        self.get_sort = get_sort
        self.get_palette = get_palette


class OffsetPrinter:
    def __init__(self, screen, offset=0):
        self.screen = screen
        self.offset = offset

    def set_offset(self, offset):
        self.offset = offset

    def print_at(self, text, x, y, palette):
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


class GenericInterface:
    columns = {}
    columns_order = []
    sleep = 0.005
    frames = 200  # 200 * 0.005 seconds == 1 second
    frame = 0
    selected = 0
    sort = 0
    reverse = False
    x_offset = 0
    row_offset = 0
    refresh = False
    width = None
    height = None
    screen = None
    rows = []
    printer = None
    _bounds = []

    palettes = defaultdict(lambda: (Screen.COLOUR_WHITE, Screen.A_NORMAL, Screen.COLOUR_BLACK))
    palettes["header"] = (Screen.COLOUR_BLACK, Screen.A_NORMAL, Screen.COLOUR_GREEN)
    palettes["focused_header"] = (Screen.COLOUR_BLACK, Screen.A_NORMAL, Screen.COLOUR_CYAN)
    palettes["focused_row"] = (Screen.COLOUR_BLACK, Screen.A_NORMAL, Screen.COLOUR_CYAN)

    def run(self):
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

                        # time to update the rows
                        if self.frame == 0:
                            self.update_rows()
                            self.refresh = True

                        # time to refresh the screen
                        if self.refresh:
                            # sort if needed, unless it was just done at frame 0 when updating rows
                            if (self.sort, self.reverse) != previous_sort and self.frame != 0:
                                self.sort_rows()

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
        if event is None:
            return

        if isinstance(event, KeyboardEvent):

            if event.key_code in (ord("q"), ord("Q")):
                # break from both loops when user hits "q"
                raise Exit()

            elif event.key_code == ord("<"):
                if self.sort > 0:
                    self.sort -= 1
                    self.refresh = True

            elif event.key_code == ord(">"):
                if self.sort < len(self.columns) - 1:
                    self.sort += 1
                    self.refresh = True

            elif event.key_code in (ord("r"), ord("R")):
                self.reverse = not self.reverse
                self.refresh = True

            elif event.key_code == Screen.KEY_UP:
                if self.selected > 0:
                    self.selected -= 1
                    if self.selected < self.row_offset:
                        self.row_offset = self.selected
                    elif self.selected >= self.row_offset + (self.height - 1):
                        # happens when shrinking height
                        self.row_offset = self.selected + 1 - (self.height - 1)
                    self.refresh = True

            elif event.key_code == Screen.KEY_DOWN:
                if self.selected < len(self.rows) - 1:
                    self.selected += 1
                    if self.selected - self.row_offset >= (self.height - 1):
                        self.row_offset = self.selected + 1 - (self.height - 1)
                    self.refresh = True

            elif event.key_code == Screen.KEY_LEFT:
                if self.x_offset > 0:
                    self.x_offset = max(0, self.x_offset - 5)
                    self.refresh = True

            elif event.key_code == Screen.KEY_RIGHT:
                self.x_offset += 5
                self.refresh = True

        elif isinstance(event, MouseEvent):

            if event.buttons & MouseEvent.LEFT_CLICK:
                if event.y == 0:
                    new_sort = self.get_column_at_x(event.x)
                    if new_sort == self.sort:
                        self.reverse = not self.reverse
                    else:
                        self.sort = new_sort
                else:
                    self.selected = min(event.y - 1 + self.row_offset, len(self.rows) - 1)
                self.refresh = True

            # elif event.buttons & MouseEvent.RIGHT_CLICK:
            #     pass  # TODO: expand/collapse

    def print_headers(self):
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
        y = 1
        for row in self.rows[self.row_offset : self.row_offset + self.height]:

            self.printer.set_offset(self.x_offset)
            x = 0

            for i, column_name in enumerate(self.columns_order):
                column = self.columns[column_name]
                padding = f"<{max(0, self.width - x)}" if column.padding == "100%" else column.padding

                if self.selected == y - 1 + self.row_offset:
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
        for i, bound in enumerate(self._bounds):
            if bound[0] <= x <= bound[1]:
                return i

    def set_screen(self, screen):
        self.screen = screen
        self.height, self.width = screen.dimensions
        self.printer = OffsetPrinter(screen)
        self._bounds = []
        for column_name in self.columns_order:
            column = self.columns[column_name]
            if column.padding == "100%":
                self._bounds.append((self._bounds[-1][1] + 1, self.width))
            else:
                padding = int(column.padding.lstrip("<>=^"))
                if not self._bounds:
                    self._bounds = [(0, padding)]
                else:
                    self._bounds.append((self._bounds[-1][1] + 1, self._bounds[-1][1] + 1 + padding))

    def update_rows(self):
        raise NotImplementedError

    def sort_rows(self):
        raise NotImplementedError


class Palette:
    @staticmethod
    def status(value):
        return "status_" + value

    @staticmethod
    def name(value):
        if value.startswith("[METADATA]"):
            return (
                [(Screen.COLOUR_GREEN, Screen.A_UNDERLINE, Screen.COLOUR_BLACK)] * 10
                + [Interface.palettes["metadata"]] * (len(value.strip()) - 10)
                + [Interface.palettes["row"]]
            )
        return "name"


class Interface(GenericInterface):
    sort = 2
    reverse = True
    palettes = GenericInterface.palettes
    palettes["status_active"] = (Screen.COLOUR_CYAN, Screen.A_NORMAL, Screen.COLOUR_BLACK)
    palettes["status_paused"] = (Screen.COLOUR_YELLOW, Screen.A_NORMAL, Screen.COLOUR_BLACK)
    palettes["status_waiting"] = (Screen.COLOUR_WHITE, Screen.A_BOLD, Screen.COLOUR_BLACK)
    palettes["status_error"] = (Screen.COLOUR_RED, Screen.A_BOLD, Screen.COLOUR_BLACK)
    palettes["status_complete"] = (Screen.COLOUR_GREEN, Screen.A_NORMAL, Screen.COLOUR_BLACK)
    palettes["metadata"] = (Screen.COLOUR_WHITE, Screen.A_UNDERLINE, Screen.COLOUR_BLACK)
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

    def __init__(self, api=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if api is None:
            api = API()
        self.api = api
        self.downloads = []

    def update_rows(self):
        self.downloads = self.api.get_downloads()
        self.sort_rows()

    def sort_rows(self):
        text_getters = [self.columns[c].get_text for c in self.columns_order]
        sort_function = self.columns[self.columns_order[self.sort]].get_sort
        n_columns = len(self.columns_order)
        self.rows = [
            tuple(text_getters[i](d) for i in range(n_columns))
            for d in sorted(self.downloads, key=sort_function, reverse=self.reverse)
        ]
