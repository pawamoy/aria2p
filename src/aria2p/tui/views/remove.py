from loguru import logger

from aria2p.tui.views.base import View


class RemoveView(View):
    header = "Remove:"
    rows = [
        ("Remove", lambda d: d.remove(force=False, files=False)),
        ("Remove with files", lambda d: d.remove(force=False, files=True)),
        ("Force remove", lambda d: d.remove(force=True, files=False)),
        ("Force remove with files", lambda d: d.remove(force=True, files=True)),
    ]

    def __init__(self, parent_view):
        super().__init__(parent_view)
        self.last_choice = None
        self.focused = 0

    def enter(self):
        if self.last_choice is not None:
            self.focused = self.last_choice

    def exit(self):
        self.wrapper.enter(self.parent_view)
        self.wrapper.refresh = True

    def process_keyboard_event(self, event):
        if event.key_code in self.keybinds.CANCEL:
            logger.debug("Canceling removal")
            self.exit()

        elif event.key_code in self.keybinds.ENTER:
            logger.debug("Validate removal")
            if self.parent_view.follow:
                self.rows[self.focused][1](self.parent_view.follow)
                self.parent_view.follow = None
            else:
                logger.debug("No download was targeted, not removing")
            self.last_choice = self.focused
            self.wrapper.enter(self.parent_view)

            # force complete refresh
            self.wrapper.frame = 0

        elif event.key_code in self.keybinds.MOVE_UP:
            if self.focused > 0:
                self.focused -= 1
                logger.debug(f"Moving side focus up: {self.focused}")
                self.wrapper.refresh = True

        elif event.key_code in self.keybinds.MOVE_DOWN:
            if self.focused < len(self.rows) - 1:
                self.focused += 1
                logger.debug(f"Moving side focus down: {self.focused}")
                self.wrapper.refresh = True

    def process_mouse_event(self, event):
        pass

    def draw(self):
        y = self.parent_view.y_offset
        padding = self.width
        header_string = f"{self.header:<{padding}}"
        len_header = len(header_string)
        self.wrapper.screen.print_at(header_string, 0, y, *self.style.SIDE_COLUMN_HEADER)
        self.wrapper.screen.print_at(" ", len_header, y, *self.style.DEFAULT)
        for i, row in enumerate(self.rows):
            y += 1
            palette = self.style.SIDE_COLUMN_FOCUSED_ROW if i == self.focused else self.style.SIDE_COLUMN_ROW
            row_string = f"{row[0]:<{padding}}"
            len_row = len(row_string)
            self.wrapper.screen.print_at(row_string, 0, y, *palette)
            self.wrapper.screen.print_at(" ", len_row, y, *self.style.DEFAULT)

        for i in range(1, self.wrapper.height - y):
            self.wrapper.screen.print_at(" " * (padding + 1), 0, y + i, *self.style.DEFAULT)

        self.parent_view.draw()

    @property
    def width(self):
        return max(len(self.header), max(len(row[0]) for row in self.rows))

    def resize(self, screen):
        pass

    def update(self):
        pass
