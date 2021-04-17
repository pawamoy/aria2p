from typing import List

import pyperclip

from aria2p.tui.views.base import View


class AddView(View):
    def __init__(self, parent_view):
        super().__init__(parent_view)
        self.uris: List[str] = []
        self.header = f"Add Download: [ Hit ENTER to download; Hit { ','.join(key.name for key in self.keybinds.ADD_DOWNLOADS) } to download all ]"
        self.focused = -1
        self.row_offset = 0

    def enter(self):
        # build set of copied lines
        copied_lines = set()
        for line in pyperclip.paste().split("\n") + pyperclip.paste(primary=True).split("\n"):
            copied_lines.add(line.strip())
        try:
            copied_lines.remove("")
        except KeyError:
            pass

        # add lines to download uris
        if copied_lines:
            self.uris = list(sorted(copied_lines))
            self.focused = 0

    def exit(self):
        self.wrapper.enter(self.parent_view)
        self.wrapper.refresh = True

    def process_keyboard_event(self, event):
        if event.key_code in self.keybinds.CANCEL + self.keybinds.QUIT:
            self.exit()

        elif event.key_code in self.keybinds.MOVE_UP:
            if self.focused > 0:
                self.focused -= 1

                if self.focused < self.row_offset:
                    self.row_offset = self.focused
                elif self.focused >= self.row_offset + (self.wrapper.height - 1):
                    # happens when shrinking height
                    self.row_offset = self.focused + 1 - (self.wrapper.height - 1)
                self.parent_view.follow = None
                self.wrapper.refresh = True

        elif event.key_code in self.keybinds.MOVE_DOWN:
            if self.focused < len(self.uris) - 1:
                self.focused += 1
                if self.focused - self.row_offset >= (self.wrapper.height - 1):
                    self.row_offset = self.focused + 1 - (self.wrapper.height - 1)
                self.parent_view.follow = None
                self.wrapper.refresh = True

        elif event.key_code in self.keybinds.ENTER:
            if self.focused >= 0:
                if self.wrapper.api.add(self.uris[self.focused]):
                    self.uris.pop(self.focused)
                    if self.focused > len(self.uris) - 1:
                        self.focused -= 1
                    self.wrapper.refresh = True

        elif event.key_code in self.keybinds.ADD_DOWNLOADS:
            for uri in self.uris:
                self.wrapper.api.add(uri)
            self.uris.clear()
            self.exit()


    def draw(self):
        y = self.parent_view.y_offset
        padding = self.wrapper.width
        header_string = f"{self.header:<{padding}}"
        len_header = len(header_string)
        self.wrapper.screen.print_at(header_string, 0, y, *self.style.SIDE_COLUMN_HEADER)
        self.wrapper.screen.print_at(" ", len_header, y, *self.style.DEFAULT)
        y += 1
        self.wrapper.screen.print_at(" " * padding, 0, y, *self.style.DEFAULT)
        separator = "..."

        for i, uri in enumerate(self.uris):
            y += 1
            palette = self.style.FOCUSED_ROW if i == self.focused else self.style.DEFAULT
            if len(uri) > padding:
                # print part of uri string
                uri = f"{uri[:(padding//2)-len(separator)]}{separator}{uri[-(padding//2)+len(separator):]}"
            else:
                uri = f"{uri}"

            self.wrapper.screen.print_at(uri, 0, y, *palette)
            self.wrapper.screen.print_at(" " * (padding - len(uri)), len(uri), y, *self.style.DEFAULT)

        for i in range(1, self.wrapper.height - y):
            self.wrapper.screen.print_at(" " * (padding + 1), 0, y + i, *self.style.DEFAULT)

        self.parent_view.draw()

    def resize(self, screen):
        pass

    def update(self):
        pass
