from aria2p.tui.views.base import View


class SelectSortView(View):
    def __init__(self, parent_view):
        super().__init__(parent_view)
        self.header = "Select sort:"
        self.rows = self.parent_view.columns_order
        self.focused = 0

    def exit(self):
        self.wrapper.enter(self.parent_view)
        self.wrapper.refresh = True

    def process_keyboard_event(self, event):
        if event.key_code in self.keybinds.CANCEL:
            self.exit()

        elif event.key_code in self.keybinds.ENTER:
            self.parent_view.sort = self.focused
            self.exit()

        elif event.key_code in self.keybinds.MOVE_UP:
            if self.focused > 0:
                self.focused -= 1
                self.wrapper.refresh = True

        elif event.key_code in self.keybinds.MOVE_DOWN:
            if self.focused < len(self.rows) - 1:
                self.focused += 1
                self.wrapper.refresh = True

    def draw(self):
        y = self.parent_view.y_offset  # noqa: WPS111
        padding = self.width
        header_string = f"{self.header:<{padding}}"
        len_header = len(header_string)
        self.wrapper.screen.print_at(header_string, 0, y, *self.style.HEADER)
        self.wrapper.screen.print_at(" ", len_header, y, *self.style.DEFAULT)
        for row_number, row in enumerate(self.rows):
            y += 1
            palette = self.style.FOCUSED_ROW if row_number == self.focused else self.style.DEFAULT
            row_string = f"{row:<{padding}}"
            len_row = len(row_string)
            self.wrapper.screen.print_at(row_string, 0, y, *palette)
            self.wrapper.screen.print_at(" ", len_row, y, *self.style.DEFAULT)

        # fill with blank lines
        for row_offset in range(1, self.wrapper.height - y):
            self.wrapper.screen.print_at(" " * (padding + 1), 0, y + row_offset, *self.style.DEFAULT)

        self.parent_view.draw()

    @property
    def width(self):
        return max(len(column_name) for column_name in self.parent_view.columns_order + [self.header])
