import time
from pathlib import Path

from asciimatics.event import KeyboardEvent, MouseEvent
from asciimatics.screen import Screen

from aria2p import interface as tui

from . import SESSIONS_DIR, Aria2Server


class Event:
    RESIZE = 1
    PASS_N_FRAMES = 2
    PASS_N_TICKS = 3
    RAISE = 4

    def __init__(self, event_type, value=None):
        self.type = event_type
        self.value = value


tui.Interface.frames = 20  # reduce tests time
pass_frame = Event(Event.PASS_N_FRAMES, 1)
pass_tick = Event(Event.PASS_N_TICKS, 1)
pass_half_tick = Event(Event.PASS_N_FRAMES, tui.Interface.frames / 2)
pass_tick_and_a_half = Event(Event.PASS_N_FRAMES, tui.Interface.frames * 3 / 2)


def get_interface(patcher, api=None, events=None, append_q=True):
    if not events:
        events = []

    if append_q:
        events.append(KeyboardEvent(ord("q")))

    class MockedManagedScreen:
        def __enter__(self):
            return MockedScreen(events)

        def __exit__(self, exc_type, exc_val, exc_tb):
            pass

    patcher.setattr(tui, "ManagedScreen", MockedManagedScreen)
    return tui.Interface(api=api)


def run_interface(patcher, api=None, events=None, append_q=True):
    interface = get_interface(patcher, api, events, append_q)
    interface.run()
    return interface


class MockedScreen:
    def __init__(self, events):
        self.events = events
        self._has_resized = False
        self._pass_n_frames = 0
        self.print_at_calls = []
        self.paint_calls = []
        self.n_refresh = 0

    @property
    def dimensions(self):
        return 30, 80

    def has_resized(self):
        return self._has_resized

    def open(self):
        pass

    def close(self):
        pass

    def get_event(self):
        if self._pass_n_frames > 0:
            self._pass_n_frames -= 1
            return None
        event = self.events.pop(0)
        if isinstance(event, (KeyboardEvent, MouseEvent)):
            return event
        elif isinstance(event, Event):
            if event.type == Event.RESIZE:
                self._has_resized = True
            elif event.type == Event.PASS_N_FRAMES:
                # we remove 1 because this event itself eats a frame
                self._pass_n_frames = event.value - 1
            elif event.type == Event.PASS_N_TICKS:
                # we remove 1 because this event itself eats a frame
                self._pass_n_frames = (event.value * tui.Interface.frames) - 1
            elif event.type == Event.RAISE:
                raise event.value
        return None

    def print_at(self, *args, **kwargs):
        if args[0].strip():
            self.print_at_calls.append({"args": args, "kwargs": kwargs})

    def paint(self, *args, **kwargs):
        if args[0].strip():
            self.paint_calls.append({"args": args, "kwargs": kwargs})

    def refresh(self):
        self.n_refresh += 1


def test_run(monkeypatch):
    interface = run_interface(monkeypatch)
    assert interface.screen
    assert interface.height == 30
    assert interface.width == 80


def test_resize(monkeypatch):
    with Aria2Server(port=7600) as server:
        interface = run_interface(monkeypatch, server.api, events=[Event(Event.RESIZE)])
        # assert screen was renewed
        assert not interface.screen.has_resized()


def test_frames_plus_n(monkeypatch):
    with Aria2Server(port=7601) as server:
        n = 10
        interface = run_interface(
            monkeypatch, server.api, events=[Event(Event.PASS_N_FRAMES, tui.Interface.frames + n)]
        )
        assert interface.frame == n


def test_change_sort(monkeypatch):
    with Aria2Server(port=7602) as server:
        interface = run_interface(monkeypatch, server.api, events=[pass_half_tick, KeyboardEvent(ord("<")), pass_tick])
        assert interface.sort == tui.Interface.sort - 1


def test_move_focus(monkeypatch):
    with Aria2Server(port=7603, session=SESSIONS_DIR / "2-dl-in-queue.txt") as server:
        interface = run_interface(
            monkeypatch,
            server.api,
            events=[KeyboardEvent(Screen.KEY_UP), pass_tick]
            + [KeyboardEvent(Screen.KEY_DOWN)] * 30
            + [pass_tick]
            + [KeyboardEvent(Screen.KEY_UP)] * 5,
        )
    assert interface.focused == 0


def test_show_help(monkeypatch):
    with Aria2Server(port=7604) as server:
        interface = run_interface(
            monkeypatch, server.api, events=[KeyboardEvent(ord("h")), pass_tick, KeyboardEvent(ord("\n"))]
        )
    assert interface.screen.print_at_calls[-1]["args"][0].startswith("Press any key to return.")


def test_horizontal_scrolling(monkeypatch):
    with Aria2Server(port=7605, session=SESSIONS_DIR / "3-magnets.txt") as server:
        run_interface(
            monkeypatch,
            server.api,
            events=[KeyboardEvent(Screen.KEY_LEFT)]
            + [pass_tick]
            + [KeyboardEvent(Screen.KEY_RIGHT)] * 2
            + [pass_tick_and_a_half]
            + [KeyboardEvent(Screen.KEY_RIGHT)] * 20
            + [pass_tick]
            + [KeyboardEvent(Screen.KEY_LEFT)] * 5,
        )


def test_log_exception(monkeypatch):
    with Aria2Server(port=7606, session=SESSIONS_DIR / "2-dl-in-queue.txt") as server:
        interface = get_interface(monkeypatch, server.api, events=[Event(Event.RAISE, LookupError("some message"))])
        assert not interface.run()
    with open(Path("tests") / "logs" / "test_interface" / "test_log_exception.log") as log_file:
        lines = log_file.readlines()
    first_line = None
    for line in lines:
        if "ERROR" in line:
            first_line = line
            break
    last_line = lines[-1]
    assert "some message" in first_line
    assert "LookupError" in last_line


def test_select_sort(monkeypatch):
    with Aria2Server(port=7607, session=SESSIONS_DIR / "3-magnets.txt") as server:
        run_interface(
            monkeypatch,
            server.api,
            events=[
                KeyboardEvent(Screen.KEY_F6),
                pass_tick_and_a_half,
                KeyboardEvent(Screen.KEY_DOWN),
                pass_tick,
                KeyboardEvent(Screen.KEY_DOWN),
                pass_tick,
                KeyboardEvent(ord("\n")),
                pass_tick,
            ],
        )


def test_mouse_event(monkeypatch):
    with Aria2Server(port=7608, session=SESSIONS_DIR / "3-magnets.txt") as server:
        interface = run_interface(
            monkeypatch,
            server.api,
            events=[MouseEvent(x=tui.Interface.x_offset, y=tui.Interface.y_offset, buttons=MouseEvent.LEFT_CLICK)],
        )
    assert interface.sort == 0


def test_vertical_scrolling(monkeypatch):
    with Aria2Server(port=7609, session=SESSIONS_DIR / "50-dls.txt") as server:
        run_interface(
            monkeypatch,
            server.api,
            events=[pass_frame] + [KeyboardEvent(Screen.KEY_DOWN)] * 40 + [KeyboardEvent(Screen.KEY_UP)] * 30,
        )


def test_follow_focused(monkeypatch):
    with Aria2Server(port=7610, session=SESSIONS_DIR / "3-magnets.txt") as server:
        interface = run_interface(
            monkeypatch,
            server.api,
            events=[
                KeyboardEvent(ord("<")),
                KeyboardEvent(ord("<")),
                pass_tick,
                KeyboardEvent(ord("F")),
                KeyboardEvent(ord("I")),
                pass_tick,
            ],
        )
    assert interface.sort == 0
    assert interface.focused == 2


def test_remove_ask(monkeypatch):
    with Aria2Server(port=7611, session=SESSIONS_DIR / "very-small-remote-file.txt") as server:
        download = server.api.get_downloads()[0]
        while not download.is_complete:
            time.sleep(0.1)
            download.update()
        assert download.root_files_paths[0].exists()
        interface = run_interface(
            monkeypatch,
            server.api,
            events=[
                pass_frame,
                KeyboardEvent(Screen.KEY_DELETE),
                pass_tick,
                KeyboardEvent(Screen.KEY_DOWN),
                KeyboardEvent(ord("\n")),
                pass_tick,
            ],
        )
        assert not download.root_files_paths[0].exists()
        assert interface.last_remove_choice == 1
