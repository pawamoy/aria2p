import time
from pathlib import Path

from asciimatics.event import KeyboardEvent, MouseEvent
from asciimatics.screen import Screen

from aria2p import interface as tui

from . import SESSIONS_DIR, Aria2Server

tui.Interface.frames = 20  # reduce tests time


class SpecialEvent:
    RESIZE = 1
    PASS_N_FRAMES = 2
    PASS_N_TICKS = 3
    RAISE = 4

    def __init__(self, event_type, value=None):
        self.type = event_type
        self.value = value


class Event:
    resize = SpecialEvent(SpecialEvent.RESIZE)
    pass_frame = SpecialEvent(SpecialEvent.PASS_N_FRAMES, 1)
    pass_tick = SpecialEvent(SpecialEvent.PASS_N_TICKS, 1)
    pass_half_tick = SpecialEvent(SpecialEvent.PASS_N_FRAMES, tui.Interface.frames / 2)
    pass_tick_and_a_half = SpecialEvent(SpecialEvent.PASS_N_FRAMES, tui.Interface.frames * 3 / 2)
    up = KeyboardEvent(Screen.KEY_UP)
    down = KeyboardEvent(Screen.KEY_DOWN)
    left = KeyboardEvent(Screen.KEY_LEFT)
    right = KeyboardEvent(Screen.KEY_RIGHT)
    delete = KeyboardEvent(Screen.KEY_DELETE)
    esc = KeyboardEvent(Screen.KEY_ESCAPE)
    f1 = KeyboardEvent(Screen.KEY_F1)
    f2 = KeyboardEvent(Screen.KEY_F2)
    f3 = KeyboardEvent(Screen.KEY_F3)
    f4 = KeyboardEvent(Screen.KEY_F4)
    f5 = KeyboardEvent(Screen.KEY_F5)
    f6 = KeyboardEvent(Screen.KEY_F6)
    f7 = KeyboardEvent(Screen.KEY_F7)
    f8 = KeyboardEvent(Screen.KEY_F8)
    f9 = KeyboardEvent(Screen.KEY_F9)
    f10 = KeyboardEvent(Screen.KEY_F10)
    f11 = KeyboardEvent(Screen.KEY_F11)
    f12 = KeyboardEvent(Screen.KEY_F12)
    enter = KeyboardEvent(ord("\n"))
    space = KeyboardEvent(ord(" "))

    @staticmethod
    def hit(letter):
        return KeyboardEvent(ord(letter))

    @staticmethod
    def exc(value):
        return SpecialEvent(SpecialEvent.RAISE, value)

    @staticmethod
    def pass_frames(value):
        return SpecialEvent(SpecialEvent.PASS_N_FRAMES, value)

    @staticmethod
    def pass_ticks(value):
        return SpecialEvent(SpecialEvent.PASS_N_TICKS, value)


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


def run_interface(patcher, api=None, events=None, append_q=True, **kwargs):
    interface = get_interface(patcher, api, events, append_q)
    for key, value in kwargs.items():
        setattr(interface, key, value)
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
        elif isinstance(event, SpecialEvent):
            if event.type == SpecialEvent.RESIZE:
                self._has_resized = True
            elif event.type == SpecialEvent.PASS_N_FRAMES:
                # we remove 1 because this event itself eats a frame
                self._pass_n_frames = event.value - 1
            elif event.type == SpecialEvent.PASS_N_TICKS:
                # we remove 1 because this event itself eats a frame
                self._pass_n_frames = (event.value * tui.Interface.frames) - 1
            elif event.type == SpecialEvent.RAISE:
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
        interface = run_interface(monkeypatch, server.api, events=[Event.resize])
        # assert screen was renewed
        assert not interface.screen.has_resized()


def test_frames_plus_n(monkeypatch):
    with Aria2Server(port=7601) as server:
        n = 10
        interface = run_interface(monkeypatch, server.api, events=[Event.pass_frames(tui.Interface.frames + n)])
        assert interface.frame == n


def test_change_sort(monkeypatch):
    with Aria2Server(port=7602) as server:
        interface = run_interface(
            monkeypatch,
            server.api,
            events=[
                Event.hit(">"),
                Event.pass_half_tick,
                Event.hit("<"),
                Event.pass_half_tick,
                Event.hit("<"),
                Event.pass_tick,
            ],
        )
        assert interface.sort == tui.Interface.sort - 1


def test_move_focus(monkeypatch):
    with Aria2Server(port=7603, session=SESSIONS_DIR / "2-dl-in-queue.txt") as server:
        interface = run_interface(
            monkeypatch,
            server.api,
            events=[Event.up, Event.pass_tick] + [Event.down] * 30 + [Event.pass_tick] + [Event.up] * 5,
        )
    assert interface.focused == 0


def test_show_help(monkeypatch):
    with Aria2Server(port=7604) as server:
        interface = run_interface(monkeypatch, server.api, events=[Event.hit("h"), Event.pass_tick, Event.enter])
    assert interface.screen.print_at_calls[-1]["args"][0].startswith("Press any key to return.")


def test_horizontal_scrolling(monkeypatch):
    with Aria2Server(port=7605, session=SESSIONS_DIR / "3-magnets.txt") as server:
        run_interface(
            monkeypatch,
            server.api,
            events=[Event.left]
            + [Event.pass_tick]
            + [Event.right] * 2
            + [Event.pass_tick_and_a_half]
            + [Event.right] * 20
            + [Event.pass_tick]
            + [Event.left] * 5,
        )


def test_log_exception(monkeypatch):
    with Aria2Server(port=7606, session=SESSIONS_DIR / "2-dl-in-queue.txt") as server:
        interface = get_interface(monkeypatch, server.api, events=[Event.exc(LookupError("some message"))])
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
                Event.f6,
                Event.pass_tick_and_a_half,
                Event.down,
                Event.pass_tick,
                Event.down,
                Event.pass_tick,
                Event.enter,
                Event.pass_tick,
            ],
        )


def test_mouse_event(monkeypatch):
    reverse = tui.Interface.reverse
    with Aria2Server(port=7608, session=SESSIONS_DIR / "3-magnets.txt") as server:
        interface = run_interface(
            monkeypatch,
            server.api,
            events=[MouseEvent(x=tui.Interface.x_offset, y=tui.Interface.y_offset, buttons=MouseEvent.LEFT_CLICK)] * 2,
        )
    assert interface.sort == 0
    assert interface.reverse is not reverse


def test_vertical_scrolling(monkeypatch):
    with Aria2Server(port=7609, session=SESSIONS_DIR / "50-dls.txt") as server:
        run_interface(monkeypatch, server.api, events=[Event.pass_frame] + [Event.down] * 40 + [Event.up] * 30)


def test_follow_focused(monkeypatch):
    with Aria2Server(port=7610, session=SESSIONS_DIR / "3-magnets.txt") as server:
        interface = run_interface(
            monkeypatch,
            server.api,
            events=[Event.hit("<"), Event.hit("<"), Event.pass_tick, Event.hit("F"), Event.hit("I"), Event.pass_tick],
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
            events=[Event.pass_frame, Event.delete, Event.pass_tick, Event.down, Event.enter, Event.pass_tick],
        )
        assert not download.root_files_paths[0].exists()
        assert interface.last_remove_choice == 1


def test_setup(monkeypatch):
    with Aria2Server(port=7612, session=SESSIONS_DIR / "2-dl-in-queue.txt") as server:
        run_interface(monkeypatch, server.api, events=[Event.pass_frame, Event.f2, Event.pass_tick])


def test_toggle_resume_pause(monkeypatch):
    with Aria2Server(port=7613, session=SESSIONS_DIR / "2-dl-in-queue.txt") as server:
        interface = run_interface(
            monkeypatch,
            server.api,
            events=[
                Event.pass_frame,
                Event.space,
                Event.down,
                Event.space,
                Event.pass_tick,
                Event.space,
                Event.pass_tick,
            ],
            sort=7,
        )

        time.sleep(0.5)
        interface.data[0].update()
        assert interface.data[0].is_active
        interface.data[1].update()
        assert interface.data[1].is_paused


def test_priority(monkeypatch):
    with Aria2Server(port=7614, session=SESSIONS_DIR / "2-dl-in-queue.txt") as server:
        run_interface(
            monkeypatch,
            server.api,
            events=[
                Event.pass_frame,
                Event.hit("["),
                Event.pass_tick,
                Event.hit("]"),
                Event.pass_tick,
                Event.hit("]"),
                Event.pass_tick,
            ],
            sort=7,
        )


def test_sort_edges(monkeypatch):
    with Aria2Server(port=7615, session=SESSIONS_DIR / "2-dl-in-queue.txt") as server:
        run_interface(monkeypatch, server.api, events=[Event.hit("<")], sort=0)
        run_interface(monkeypatch, server.api, events=[Event.hit(">")], sort=7)


def test_remember_last_remove(monkeypatch):
    with Aria2Server(port=7621, session=SESSIONS_DIR / "2-dl-in-queue.txt") as server:
        interface = run_interface(
            monkeypatch,
            server.api,
            events=[
                Event.pass_frame,
                Event.delete,
                Event.down,
                Event.enter,
                Event.delete,
                Event.esc,
            ],
        )
    assert interface.last_remove_choice == 1
    assert interface.side_focused == 1


def test_autoclear(monkeypatch):
    with Aria2Server(port=7617, session=SESSIONS_DIR / "very-small-remote-file.txt") as server:
        download = server.api.get_downloads()[0]
        while not download.is_complete:
            time.sleep(0.1)
            download.update()
        interface = run_interface(monkeypatch, server.api, events=[Event.pass_frame, Event.hit("c"), Event.pass_tick])
    assert not interface.data


def test_side_column_edges(monkeypatch):
    with Aria2Server(port=7618, session=SESSIONS_DIR / "2-dl-in-queue.txt") as server:
        run_interface(
            monkeypatch,
            server.api,
            events=[
                Event.pass_frame,
                Event.delete,
                Event.down,
                Event.up,
                Event.up,
                Event.down,
                Event.down,
                Event.down,
                Event.down,
                Event.esc,
            ],
        )
        run_interface(
            monkeypatch,
            server.api,
            events=[Event.pass_frame, Event.f6]
            + [Event.up] * len(tui.Interface.columns_order)
            + [Event.down] * len(tui.Interface.columns_order)
            + [Event.esc],
        )


def test_click_row(monkeypatch):
    with Aria2Server(port=7619, session=SESSIONS_DIR / "2-dl-in-queue.txt") as server:
        interface = run_interface(
            monkeypatch, server.api, events=[Event.pass_frame, MouseEvent(x=10, y=2, buttons=MouseEvent.LEFT_CLICK)]
        )
    assert interface.focused == 1


def test_click_out_bounds(monkeypatch):
    with Aria2Server(port=7620) as server:
        run_interface(
            monkeypatch, server.api, events=[Event.pass_frame, MouseEvent(x=1000, y=0, buttons=MouseEvent.LEFT_CLICK)]
        )
    with open(Path("tests") / "logs" / "test_interface" / "test_click_out_bounds.log") as log_file:
        lines = log_file.readlines()
    error_line = None
    for line in lines:
        if "ERROR" in line:
            error_line = line
            break
    assert error_line
    assert "clicked outside of boundaries" in error_line
