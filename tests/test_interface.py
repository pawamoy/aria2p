from asciimatics.event import KeyboardEvent
from asciimatics.screen import Screen

from aria2p import interface as tui

from . import Aria2Server


class Event:
    RESIZE = 1
    PASS_N_FRAMES = 2
    PASS_N_TICKS = 3


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

    @property
    def dimensions(self):
        return 60, 80

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
        if isinstance(event, KeyboardEvent):
            return event
        elif event == Event.RESIZE:
            self._has_resized = True
        elif event == Event.PASS_N_FRAMES:
            self._pass_n_frames = self.events.pop(0)
        elif event == Event.PASS_N_TICKS:
            self._pass_n_frames = self.events.pop(0) * tui.Interface.frames
        return None

    def print_at(self, *args, **kwargs):
        pass

    def paint(self, *args, **kwargs):
        pass

    def refresh(self):
        pass


def test_run(monkeypatch):
    interface = run_interface(monkeypatch)
    assert interface.screen
    assert interface.height == 60
    assert interface.width == 80


def test_resize(monkeypatch):
    with Aria2Server(port=7600) as server:
        interface = run_interface(monkeypatch, server.api, events=[Event.RESIZE])
        # assert screen was renewed
        assert not interface.screen.has_resized()


def test_frames_plus_n(monkeypatch):
    with Aria2Server(port=7601) as server:
        n = 10
        interface = run_interface(monkeypatch, server.api, events=[Event.PASS_N_FRAMES, tui.Interface.frames + n - 1])
        assert interface.frame == n


def test_change_sort(monkeypatch):
    with Aria2Server(port=7602) as server:
        interface = run_interface(
            monkeypatch, server.api, events=[Event.PASS_N_FRAMES, 10, KeyboardEvent(ord("<")), Event.PASS_N_TICKS, 1]
        )
        assert interface.sort == tui.Interface.sort - 1


def test_move_focus(monkeypatch):
    with Aria2Server(port=7603) as server:
        interface = run_interface(
            monkeypatch,
            server.api,
            events=[KeyboardEvent(Screen.KEY_UP), Event.PASS_N_TICKS, 1]
            + [KeyboardEvent(Screen.KEY_DOWN)] * 5
            + [Event.PASS_N_TICKS, 1]
            + [KeyboardEvent(Screen.KEY_UP)] * 20,
        )
        assert interface.focused == 0
