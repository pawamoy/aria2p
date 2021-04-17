class View:
    def __init__(self, parent_view=None):
        self.parent_view = parent_view

    @property
    def wrapper(self):
        view = self
        while view.parent_view:
            view = view.parent_view
        return view

    @property
    def style(self):
        return self.wrapper.config.style

    @property
    def keybinds(self):
        return self.wrapper.config.keybinds

    def enter(self):
        pass

    def exit(self):
        pass

    def draw(self):
        pass

    def process_keyboard_event(self):
        pass

    def process_mouse_event(self):
        pass

    def resize(self, screen):
        pass

    def update(self):
        pass
