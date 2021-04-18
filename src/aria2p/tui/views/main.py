"""The main view module."""

from typing import List, Sequence, Tuple, Union

import requests
from asciimatics.event import Event, MouseEvent
from asciimatics.screen import Screen
from loguru import logger

from aria2p.downloads import Download
from aria2p.tui.errors import ClickedOutOfBounds, Exit
from aria2p.tui.helpers import Column, HorizontalScroll
from aria2p.tui.views.add import AddView
from aria2p.tui.views.base import View
from aria2p.tui.views.help import HelpView
from aria2p.tui.views.remove import RemoveView
from aria2p.tui.views.select_sort import SelectSortView

PaletteType = Union[str, List[Tuple[int, int, int]]]


class MainView(View):
    """The main view showing the downloads in a HTOP-like interface."""

    def __init__(self, parent_view):  # noqa: D107
        super().__init__(parent_view)
        self.focused = 0
        self.sort = 2
        self.reverse = True
        self.x_scroll = 0
        self.x_offset = 0
        self.y_offset = 0
        self.row_offset = 0
        self.data: List[Download] = []
        self.rows: List[Sequence[str]] = []
        self.follow = None
        self.bounds: List[Sequence[int]] = []
        self.scroller = None

        self.previous_sort = self.current_sort

        self.columns_order = ["gid", "status", "progress", "size", "down_speed", "up_speed", "eta", "name"]
        self.columns = {
            "gid": Column(
                header="GID",
                padding=">16",
                get_text=lambda download: download.gid,
                get_sort=lambda download: download.gid,
            ),
            "status": Column(
                header="STATUS",
                padding="<9",
                get_text=lambda download: download.status,
                get_sort=lambda download: download.status,
                get_palette=self.palette_status,
            ),
            "progress": Column(
                header="PROGRESS",
                padding=">8",
                get_text=lambda download: download.progress_string(),
                get_sort=lambda download: download.progress,
            ),
            "size": Column(
                header="SIZE",
                padding=">11",
                get_text=lambda download: download.total_length_string(),
                get_sort=lambda download: download.total_length,
            ),
            "down_speed": Column(
                header="DOWN_SPEED",
                padding=">13",
                get_text=lambda download: download.download_speed_string(),
                get_sort=lambda download: download.download_speed,
            ),
            "up_speed": Column(
                header="UP_SPEED",
                padding=">13",
                get_text=lambda download: download.upload_speed_string(),
                get_sort=lambda download: download.upload_speed,
            ),
            "eta": Column(
                header="ETA",
                padding=">8",
                get_text=lambda download: download.eta_string(precision=2),
                get_sort=lambda download: download.eta,
            ),
            "name": Column(
                header="NAME",
                padding="100%",
                get_text=lambda download: download.name,
                get_sort=lambda download: download.name,
                get_palette=self.palette_name,
            ),
        }

        self.help_view = HelpView(parent_view=self)
        self.remove_ask_view = RemoveView(parent_view=self)
        self.select_sort_view = SelectSortView(parent_view=self)
        self.add_downloads_view = AddView(parent_view=self)

    def enter(self) -> None:  # noqa: D102
        self.x_offset = 0

    def palette_status(self, value: str) -> str:
        """
        Return the palette for a STATUS cell.

        Arguments:
            value: The value of the STATUS cell.

        Returns:
            The palette name (later transformed into a proper palette).
        """
        return "STATUS_" + value.upper()

    def palette_name(self, value: str) -> PaletteType:
        """
        Return the palette for a NAME cell.

        Arguments:
            value: The value of the NAME cell.

        Returns:
            The 3 colors palette or its name.
        """
        if value.startswith("[METADATA]"):
            return (
                [(Screen.COLOUR_GREEN, Screen.A_UNDERLINE, Screen.COLOUR_BLACK)] * 10
                + [self.style.METADATA] * (len(value.strip()) - 10)
                + [self.style.DEFAULT]
            )
        return "DEFAULT"

    def current_sort(self) -> Tuple[int, bool]:
        """
        Return the current sort.

        Returns:
            A tuple containing the sort index and the reverse boolean.
        """
        return self.sort, self.reverse

    def follow_focused(self) -> bool:
        """
        Follow the currently focused download.

        Returns:
            Success or failure.
        """
        if self.focused < len(self.data):
            self.follow = self.data[self.focused]
            return True
        return False

    def get_column_at_x(self, x: int):  # noqa: WPS111
        """
        Return the column index given an abscissa.

        Arguments:
            x: The abscissa.

        Raises:
            ValueError: When the user clicked outside of boundaries.

        Returns:
            The column index.
        """
        for column_number, bound in enumerate(self.bounds):
            if bound[0] <= x <= bound[1]:
                return column_number
        raise ClickedOutOfBounds("clicked outside of boundaries")

    def process_keyboard_event(self, event: Event) -> None:  # noqa: D102
        if event.key_code in self.keybinds.MOVE_UP:
            if self.focused > 0:
                self.focused -= 1
                logger.debug(f"Move focus up: {self.focused}")

                if self.focused < self.row_offset:
                    self.row_offset = self.focused
                elif self.focused >= self.row_offset + (self.wrapper.height - 1):
                    # happens when shrinking height
                    self.row_offset = self.focused + 1 - (self.wrapper.height - 1)
                self.follow = None
                self.wrapper.refresh = True

        elif event.key_code in self.keybinds.MOVE_DOWN:
            if self.focused < len(self.rows) - 1:
                self.focused += 1
                logger.debug(f"Move focus down: {self.focused}")
                if self.focused - self.row_offset >= (self.wrapper.height - 1):
                    self.row_offset = self.focused + 1 - (self.wrapper.height - 1)
                self.follow = None
                self.wrapper.refresh = True

        elif event.key_code in self.keybinds.MOVE_LEFT:
            if self.x_scroll > 0:
                self.x_scroll = max(0, self.x_scroll - 5)
                self.wrapper.refresh = True

        elif event.key_code in self.keybinds.MOVE_RIGHT:
            self.x_scroll += 5
            self.wrapper.refresh = True

        elif event.key_code in self.keybinds.HELP:
            self.wrapper.enter(self.help_view)
            self.wrapper.refresh = True

        elif event.key_code in self.keybinds.SETUP:
            pass  # TODO

        elif event.key_code in self.keybinds.TOGGLE_RESUME_PAUSE:
            download = self.data[self.focused]
            if download.is_active or download.is_waiting:
                logger.debug(f"Pausing download {download.gid}")
                download.pause()
            elif download.is_paused:
                logger.debug(f"Resuming download {download.gid}")
                download.resume()

        elif event.key_code in self.keybinds.PRIORITY_UP:
            download = self.data[self.focused]
            if not download.is_active:
                download.move_up()
                self.follow = download

        elif event.key_code in self.keybinds.PRIORITY_DOWN:
            download = self.data[self.focused]
            if not download.is_active:
                download.move_down()
                self.follow = download

        elif event.key_code in self.keybinds.REVERSE_SORT:
            self.reverse = not self.reverse
            self.wrapper.refresh = True

        elif event.key_code in self.keybinds.NEXT_SORT:
            if self.sort < len(self.columns) - 1:
                self.sort += 1
                self.wrapper.refresh = True

        elif event.key_code in self.keybinds.PREVIOUS_SORT:
            if self.sort > 0:
                self.sort -= 1
                self.wrapper.refresh = True

        elif event.key_code in self.keybinds.SELECT_SORT:
            self.wrapper.enter(self.select_sort_view)
            self.select_sort_view.focused = self.sort
            self.x_offset = self.select_sort_view.width + 1
            self.wrapper.refresh = True

        elif event.key_code in self.keybinds.REMOVE_ASK:
            logger.debug("Triggered removal")
            logger.debug(f"self.focused = {self.focused}")
            logger.debug(f"len(self.data) = {len(self.data)}")
            if self.follow_focused():
                self.x_offset = self.remove_ask_view.width + 1
                self.wrapper.enter(self.remove_ask_view)
                self.wrapper.refresh = True
            else:
                logger.debug("Could not focus download")

        elif event.key_code in self.keybinds.TOGGLE_EXPAND_COLLAPSE:
            pass  # TODO

        elif event.key_code in self.keybinds.TOGGLE_EXPAND_COLLAPSE_ALL:
            pass  # TODO

        elif event.key_code in self.keybinds.AUTOCLEAR:
            self.wrapper.api.purge()

        elif event.key_code in self.keybinds.FOLLOW_ROW:
            self.follow_focused()

        elif event.key_code in self.keybinds.SEARCH:
            pass  # TODO

        elif event.key_code in self.keybinds.FILTER:
            pass  # TODO

        elif event.key_code in self.keybinds.TOGGLE_SELECT:
            pass  # TODO

        elif event.key_code in self.keybinds.UN_SELECT_ALL:
            pass  # TODO

        elif event.key_code in self.keybinds.MOVE_HOME:
            if self.focused > 0:
                self.focused = 0
                logger.debug(f"Move focus home: {self.focused}")

                if self.focused < self.row_offset:
                    self.row_offset = self.focused
                elif self.focused >= self.row_offset + (self.wrapper.height - 1):
                    # happens when shrinking height
                    self.row_offset = self.focused + 1 - (self.wrapper.height - 1)
                self.follow = None
                self.wrapper.refresh = True

        elif event.key_code in self.keybinds.MOVE_END:
            if self.focused < len(self.rows) - 1:
                self.focused = len(self.rows) - 1
                logger.debug(f"Move focus end: {self.focused}")

                if self.focused - self.row_offset >= (self.wrapper.height - 1):
                    self.row_offset = self.focused + 1 - (self.wrapper.height - 1)
                self.follow = None
                self.wrapper.refresh = True

        elif event.key_code in self.keybinds.MOVE_UP_STEP:
            if self.focused > 0:
                self.focused -= len(self.rows) // 5

                if self.focused < 0:
                    self.focused = 0
                logger.debug(f"Move focus up (step): {self.focused}")

                if self.focused < self.row_offset:
                    self.row_offset = self.focused
                elif self.focused >= self.row_offset + (self.wrapper.height - 1):
                    # happens when shrinking height
                    self.row_offset = self.focused + 1 - (self.wrapper.height - 1)

                self.follow = None
                self.wrapper.refresh = True

        elif event.key_code in self.keybinds.MOVE_DOWN_STEP:
            if self.focused < len(self.rows) - 1:
                self.focused += len(self.rows) // 5

                if self.focused > len(self.rows) - 1:
                    self.focused = len(self.rows) - 1
                logger.debug(f"Move focus down (step): {self.focused}")

                if self.focused - self.row_offset >= (self.wrapper.height - 1):
                    self.row_offset = self.focused + 1 - (self.wrapper.height - 1)
                self.follow = None
                self.wrapper.refresh = True

        elif event.key_code in self.keybinds.TOGGLE_RESUME_PAUSE_ALL:
            stats = self.wrapper.api.get_stats()
            if stats.num_active:
                self.wrapper.api.pause_all()
            else:
                self.wrapper.api.resume_all()

        elif event.key_code in self.keybinds.RETRY:
            download = self.data[self.focused]
            self.wrapper.api.retry_downloads([download])

        elif event.key_code in self.keybinds.RETRY_ALL:
            downloads = self.data[:]
            self.wrapper.api.retry_downloads(downloads)

        elif event.key_code in self.keybinds.ADD_DOWNLOADS:
            self.wrapper.enter(self.add_downloads_view)
            self.wrapper.refresh = True
            self.x_offset = self.wrapper.width

        elif event.key_code in self.keybinds.QUIT:
            raise Exit()

    def process_mouse_event(self, event: Event) -> None:  # noqa: D102
        if event.buttons & MouseEvent.LEFT_CLICK:
            if event.y == 0:
                new_sort = self.get_column_at_x(event.x)
                if new_sort == self.sort:
                    self.reverse = not self.reverse
                else:
                    self.sort = new_sort
            else:
                self.focused = min(event.y - 1 + self.row_offset, len(self.rows) - 1)
            self.wrapper.refresh = True

        # elif event.buttons & MouseEvent.RIGHT_CLICK:
        #     pass  # TODO: expand/collapse

    def draw(self) -> None:  # noqa: D102
        # sort if needed, unless it was just done at frame 0 when updating
        if self.current_sort != self.previous_sort and self.wrapper.frame != 0:
            self.sort_data()
            self.update_rows()
        self.previous_sort = self.current_sort

        self.draw_headers()
        self.draw_rows()

    def draw_headers(self) -> None:
        """Draw the headers (columns names)."""
        self.scroller.set_scroll(self.x_scroll)
        x, y = self.x_offset, self.y_offset  # noqa: WPS111

        for column_index, column_name in enumerate(self.columns_order):
            column = self.columns[column_name]
            palette = self.style.FOCUSED_HEADER if column_index == self.sort else self.style.HEADER

            if column.padding == "100%":
                header_string = column.header
                fill_up = " " * max(0, self.wrapper.width - x - len(header_string))
                written = self.scroller.print_at(header_string, x, y, palette)
                self.scroller.print_at(fill_up, x + written, y, self.style.HEADER)

            else:
                header_string = f"{column.header:{column.padding}} "
                written = self.scroller.print_at(header_string, x, y, palette)

            x += written  # noqa: WPS111

    def draw_rows(self) -> None:
        """Draw the rows."""
        y = self.y_offset + 1  # noqa: WPS111
        for row in self.rows[self.row_offset : self.row_offset + self.wrapper.height]:

            self.scroller.set_scroll(self.x_scroll)
            x = self.x_offset  # noqa: WPS111

            for column_index, column_name in enumerate(self.columns_order):
                column = self.columns[column_name]
                padding = f"<{max(0, self.wrapper.width - x)}" if column.padding == "100%" else column.padding

                if self.focused == y - self.y_offset - 1 + self.row_offset:
                    palette = self.style.FOCUSED_ROW
                else:
                    palette = column.get_palette(row[column_index])
                    if isinstance(palette, str):
                        palette = self.style[palette]

                field_string = f"{row[column_index]:{padding}} "
                written = self.scroller.print_at(field_string, x, y, palette)
                x += written  # noqa: WPS111

            y += 1  # noqa: WPS111

        # fill with blank lines
        for blank_line in range(self.wrapper.height - y):
            self.wrapper.screen.print_at(" " * self.wrapper.width, self.x_offset, y + blank_line, *self.style.DEFAULT)

    def resize(self, screen: Screen) -> None:
        """
        Resize contents.

        Arguments:
            screen: The new screen instance.
        """
        self.update_bounds()
        self.update_scroller(screen)

    def update_bounds(self) -> None:
        """Update the columns boundaries."""
        self.bounds = []
        for column_name in self.columns_order:
            column = self.columns[column_name]
            if column.padding == "100%":  # last column
                self.bounds.append((self.bounds[-1][1] + 1, self.wrapper.width))
            else:
                padding = int(column.padding.lstrip("<>=^"))
                if not self.bounds:
                    self.bounds = [(0, padding)]
                else:
                    self.bounds.append((self.bounds[-1][1] + 1, self.bounds[-1][1] + 1 + padding))

    def update_scroller(self, screen: Screen) -> None:
        """
        Update the horizontal scroller.

        Arguments:
            screen: The new screen.
        """
        self.scroller = HorizontalScroll(screen)

    def update(self) -> bool:  # noqa: D102
        self.update_data()
        self.update_rows()

        # too hard yet to say if something changed
        return True

    def get_data(self) -> List[Download]:
        """
        Return a list of downloads from aria2c.

        Returns:
            The current list of downloads.
        """
        return self.wrapper.api.get_downloads()

    def update_data(self) -> None:
        """Set the interface data and rows contents."""
        try:
            self.data = self.get_data()
            self.sort_data()
        except requests.exceptions.Timeout:
            logger.debug("Request timeout")

    def sort_data(self) -> None:
        """Sort data according to interface view."""
        sort_function = self.columns[self.columns_order[self.sort]].get_sort
        self.data = sorted(self.data, key=sort_function, reverse=self.reverse)

    def update_rows(self) -> None:
        """Update rows contents according to data and interface view."""
        text_getters = [self.columns[column_name].get_text for column_name in self.columns_order]
        n_columns = len(self.columns_order)
        self.rows = [tuple(text_getter(item) for text_getter in text_getters) for item in self.data]
        if self.follow:
            self.focused = self.data.index(self.follow)
