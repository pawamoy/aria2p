"""
This module contains all the top-like interface related code.

Why using asciimatics?

- curses is hard, and not working well on Windows
- blessings (curses-based) is easier, but does not provide input methods and is not maintained
- blessed (blessings fork) provides input methods, but they are blocking
- urwid seems less easy to use than asciimatics, and older
- clint is not maintained and does not provide input methods
- prompt_toolkit is designed to build interactive (like, very interactive) command line applications
- curtsies, pygcurse, unicurses: meh

Well, asciimatics also provides a "top" example, so...
"""

from collections import defaultdict

from asciimatics.event import KeyboardEvent
from asciimatics.exceptions import ResizeScreenError, StopApplication
from asciimatics.scene import Scene
from asciimatics.screen import Screen
from asciimatics.widgets import Frame, Label, Layout, MultiColumnListBox, Widget


def bring_up(api):
    class DemoFrame(Frame):
        def __init__(self, screen):
            super(DemoFrame, self).__init__(screen, screen.height, screen.width, has_border=False, name="aria2p")
            # Internal state required for doing periodic updates
            self._last_frame = 0
            self._sort = 2
            self._reverse = True

            # Create the basic form layout...
            layout = Layout([1], fill_frame=True)
            self._list = MultiColumnListBox(
                Widget.FILL_FRAME,
                [">16", "<9", ">8", ">13", ">13", ">8", "100%"],
                [],
                titles=["GID", "STATUS", "PROGRESS", "DOWN_SPEED", "UP_SPEED", "ETA", "NAME"],
                name="mc_list",
            )
            self.add_layout(layout)
            layout.add_widget(self._list)
            layout.add_widget(Label("Press `<`/`>` to change sort, `r` to toggle order, or `q` to quit."))
            self.fix()

            # Add my own colour palette
            self.palette = defaultdict(lambda: (Screen.COLOUR_WHITE, Screen.A_NORMAL, Screen.COLOUR_BLACK))
            self.palette["title"] = (Screen.COLOUR_WHITE, Screen.A_BOLD, Screen.COLOUR_GREEN)
            self.palette["selected_focus_field"] = (Screen.COLOUR_WHITE, Screen.A_NORMAL, Screen.COLOUR_CYAN)

            # sorted_column_title = (Screen.COLOUR_CYAN, Screen.A_BOLD, Screen.COLOUR_WHITE)

        def process_event(self, event):
            # Do the key handling for this Frame.
            if isinstance(event, KeyboardEvent):
                refresh = True
                if event.key_code in [ord("q"), ord("Q"), Screen.ctrl("c")]:
                    raise StopApplication("User quit")
                elif event.key_code in [ord("r"), ord("R")]:
                    self._reverse = not self._reverse
                elif event.key_code == ord("<"):
                    self._sort = max(0, self._sort - 1)
                elif event.key_code == ord(">"):
                    self._sort = min(len(self._list._columns) - 1, self._sort + 1)
                else:
                    refresh = False

                if refresh:
                    # Force a refresh for improved responsiveness
                    self._last_frame = 0

            # Now pass on to lower levels for normal handling of the event.
            return super(DemoFrame, self).process_event(event)

        def _update(self, frame_no):
            # Refresh the list view if needed
            if frame_no - self._last_frame >= self.frame_update_count or self._last_frame == 0:
                self._last_frame = frame_no

                # Create the data to go in the multi-column list...
                last_selection = self._list.value
                last_start = self._list.start_line
                list_data = []
                downloads = api.get_downloads()

                for download in downloads:
                    data = [
                        download.gid,
                        download.status,
                        download.progress_string(),
                        download.download_speed_string(),
                        download.upload_speed_string(),
                        download.eta_string(precision=2),
                        download.name,
                    ]
                    list_data.append(data)

                # Apply current sort and reformat for humans
                list_data = sorted(list_data, key=lambda f: f[self._sort], reverse=self._reverse)
                new_data = [(x, i) for i, x in enumerate(list_data)]

                # Update the list and try to reset the last selection.
                self._list.options = new_data
                self._list.value = last_selection
                self._list.start_line = last_start

            # Now redraw as normal
            super(DemoFrame, self)._update(frame_no)

        @property
        def frame_update_count(self):
            # Refresh once every 1 seconds by default.
            return 25

    def demo(screen):
        screen.play([Scene([DemoFrame(screen)], -1)], stop_on_resize=True)

    while True:
        try:
            Screen.wrapper(demo, catch_interrupt=True)
            break
        except ResizeScreenError:
            pass
