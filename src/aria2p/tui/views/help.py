from aria2p.tui.views.base import View
from aria2p.utils import get_version


class HelpView(View):
    def process_keyboard_event(self, event):
        self.wrapper.enter(self.parent_view)
        self.wrapper.refresh = True

    def process_mouse_event(self, event):
        pass

    def draw_keys(self, keys, text, y):
        self.draw_keys_text(" ".join(key.name for key in keys) + ":", text, y)

    def draw_keys_text(self, keys_text, text, y):
        length = 8
        padding = self.wrapper.width - length
        self.wrapper.screen.print_at(f"{keys_text:>{length}}", 0, y, *self.style.BRIGHT_HELP)
        self.wrapper.screen.print_at(f"{text:<{padding}}", length, y, *self.style.DEFAULT)

    def draw(self):
        version = get_version()
        lines = [
            f"aria2p {version} — (C) 2018 Timothée Mazzucotelli and contributors",
            "Released under the ISC license.",
            "",
        ]

        y = 0
        for line in lines:
            self.wrapper.screen.print_at(f"{line:<{self.wrapper.width}}", 0, y, *self.style.BRIGHT_HELP)
            y += 1

        for keys, text in [
            (self.keybinds.HELP, " show this help screen"),
            (self.keybinds.MOVE_UP, " scroll downloads list"),
            (self.keybinds.MOVE_UP_STEP, " scroll downloads list (steps)"),
            (self.keybinds.MOVE_DOWN, " scroll downloads list"),
            (self.keybinds.MOVE_DOWN_STEP, " scroll downloads list (steps)"),
            # not implemented: (self.keybinds.SETUP, " setup"),
            (self.keybinds.TOGGLE_RESUME_PAUSE, " toggle pause/resume"),
            (self.keybinds.TOGGLE_RESUME_PAUSE_ALL, " toggle pause/resume all"),
            (self.keybinds.PRIORITY_UP, " priority up (-)"),
            (self.keybinds.PRIORITY_DOWN, " priority down (+)"),
            (self.keybinds.REVERSE_SORT, " invert sort order"),
            (self.keybinds.NEXT_SORT, " sort next column"),
            (self.keybinds.PREVIOUS_SORT, " sort previous column"),
            (self.keybinds.SELECT_SORT, " select sort column"),
            (self.keybinds.REMOVE_ASK, " remove download"),
            # not implemented: (self.keybinds.TOGGLE_EXPAND_COLLAPSE, " toggle expand/collapse"),
            # not implemented: (self.keybinds.TOGGLE_EXPAND_COLLAPSE_ALL, " toggle expand/collapse all"),
            (self.keybinds.AUTOCLEAR, " autopurge downloads"),
            (self.keybinds.FOLLOW_ROW, " cursor follows download"),
            # not implemented: (self.keybinds.SEARCH, " name search"),
            # not implemented: (self.keybinds.FILTER, " name filtering"),
            # not implemented: (self.keybinds.TOGGLE_SELECT, " toggle select download"),
            # not implemented: (self.keybinds.UN_SELECT_ALL, " unselect all downloads"),
            (self.keybinds.MOVE_HOME, " move focus to first download"),
            (self.keybinds.MOVE_END, " move focus to last download"),
            (self.keybinds.RETRY, " retry failed download"),
            (self.keybinds.RETRY_ALL, " retry all failed download"),
            (self.keybinds.ADD_DOWNLOADS, " add downloads from clipboard"),
            (self.keybinds.QUIT, " quit"),
        ]:
            self.draw_keys(keys, text, y)
            y += 1

        self.wrapper.screen.print_at(" " * self.wrapper.width, 0, y, *self.style.DEFAULT)
        y += 1
        self.wrapper.screen.print_at(f"{'Press any key to return.':<{self.wrapper.width}}", 0, y, *self.style.BRIGHT_HELP)
        y += 1

        for i in range(self.wrapper.height - y):
            self.wrapper.screen.print_at(" " * self.wrapper.width, 0, y + i, *self.style.DEFAULT)

    def resize(self, screen):
        pass

    def update(self):
        pass
