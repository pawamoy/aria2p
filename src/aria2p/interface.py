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

from collections import defaultdict
import time
from loguru import logger

from asciimatics.event import KeyboardEvent
from asciimatics.screen import Screen, ManagedScreen

from .api import API


class Exit(Exception):
    pass


class OffsetPrinter:
    def __init__(self, screen, offset):
        self.screen = screen
        self.offset = offset

    def print_at(self, text, *args, **kwargs):
        logger.debug(f"Printing following text with offset={self.offset} and args={args}")
        logger.debug(text)
        if self.offset == 0:
            self.screen.print_at(text, *args, **kwargs)
            written = len(text)
        else:
            text_length = len(text)
            if text_length > self.offset:
                new_text = text[self.offset:]
                written = len(new_text)
                self.screen.print_at(new_text, *args, **kwargs)
                self.offset = 0
            elif text_length == self.offset:
                self.offset = 0
                written = 0
            else:
                self.offset -= text_length
                written = 0
        return written


class GenericInterface:
    columns = []
    sleep = 0.005
    frames = 200  # 200 * 0.005 seconds == 1 second
    selected = 0
    sort = 0
    y_offset = 0
    refresh = False
    width = None
    height = None
    screen = None
    rows = []

    palettes = defaultdict(lambda: (Screen.COLOUR_WHITE, Screen.A_NORMAL, Screen.COLOUR_BLACK))
    palettes["header"] = (Screen.COLOUR_BLACK, Screen.A_NORMAL, Screen.COLOUR_GREEN)
    palettes["focused_header"] = (Screen.COLOUR_BLACK, Screen.A_NORMAL, Screen.COLOUR_CYAN)
    palettes["focused_row"] = (Screen.COLOUR_BLACK, Screen.A_NORMAL, Screen.COLOUR_CYAN)

    def run(self):
        try:
            # outer loop to support screen resize
            while True:
                with ManagedScreen() as screen:
                    self.screen = screen
                    self.height, self.width = screen.dimensions
                    frame = 0
                    # break (and re-enter) when screen has been resized
                    while not screen.has_resized():
                        self.refresh = False
                        self.process_event(screen.get_event())
                        if frame == 0:
                            self.update_rows()
                            self.refresh = True
                        if self.refresh:
                            self.print_headers()
                            self.print_rows()
                            screen.refresh()
                        time.sleep(self.sleep)
                        frame = (frame + 1) % self.frames
        except Exit:
            pass

    def process_event(self, event):
        if event is None:
            return

        if isinstance(event, KeyboardEvent):

            if event.key_code in (ord("q"), ord("Q")):
                # break from both loops when user hits "q"
                raise Exit

            elif event.key_code == ord("<"):
                if self.sort > 0:
                    self.sort -= 1
                    self.refresh = True

            elif event.key_code == ord(">"):
                if self.sort < len(self.columns) - 1:
                    self.sort += 1
                    self.refresh = True

            elif event.key_code == -204:  # up
                if self.selected > 0:
                    self.selected -= 1
                    self.refresh = True

            elif event.key_code == -206:  # down
                if self.selected < min(self.height - 1, len(self.rows)):
                    self.selected += 1
                    self.refresh = True

            elif event.key_code == -203:  # left
                if self.y_offset > 0:
                    self.y_offset = max(0, self.y_offset - 5)
                    self.refresh = True

            elif event.key_code == -205:  # right
                self.y_offset += 5
                self.refresh = True

    def print_headers(self):
        printer = OffsetPrinter(self.screen, self.y_offset)
        x, y, c = 0, 0, 0

        for header, padding, print_field in self.columns:
            palette = self.palettes["focused_header"] if c == self.sort else self.palettes["header"]

            if padding == "100%":
                header_string = f"{header} "
                len_header = len(header)
                fill_up = f"{' ':<{max(0, self.width - x - len_header)}}"
                written = printer.print_at(header_string, x, y, *palette)
                printer.print_at(fill_up, x + written, y, *self.palettes["header"])

            else:
                header_string = f"{header:{padding}} "
                written = printer.print_at(header_string, x, y, *palette)

            x += written
            c += 1

    def print_rows(self):
        for y, row in enumerate(self.rows, 1):

            printer = OffsetPrinter(self.screen, self.y_offset)
            x = 0

            palette = self.palettes["focused_row"] if self.selected == y - 1 else self.palettes["default"]

            for _, padding, get_cell_text in self.columns:
                if padding == "100%":
                    padding = f"<{max(0, self.width - x)}"

                field_string = f"{get_cell_text(row):{padding}} "
                written = printer.print_at(field_string, x, y, *palette)
                x += written

    def update_rows(self):
        raise NotImplementedError


class Interface(GenericInterface):
    sort = 2
    columns = [
        ("GID", ">16", lambda d: d.gid),
        ("STATUS", "<9", lambda d: d.status),
        ("PROGRESS", ">8", lambda d: d.progress_string()),
        ("DOWN_SPEED", ">13", lambda d: d.download_speed_string()),
        ("UP_SPEED", ">13", lambda d: d.upload_speed_string()),
        ("ETA", ">8", lambda d: d.eta_string(precision=2)),
        ("NAME", "100%", lambda d: d.name),
    ]

    def __init__(self, api=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if api is None:
            api = API()
        self.api = api

    def update_rows(self):
        self.rows = self.api.get_downloads()
