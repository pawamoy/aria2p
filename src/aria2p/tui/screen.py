class Column:
    """
    A class to specify a column in the interface.

    It's composed of a header (the string to display on top), a padding (how to align the text),
    and three callable functions to get the text from a Python object, to sort between these objects,
    and to get a color palette based on the text.
    """

    def __init__(self, header, padding, get_text, get_sort, get_palette):
        """
        Initialize the object.

        Arguments:
            header (str): The string to display on top.
            padding (str): How to align the text.
            get_text (func): Function accepting a Download as argument and returning the text to display.
            get_sort (func): Function accepting a Download as argument and returning the attribute used to sort.
            get_palette (func): Function accepting text as argument and returning a palette or a palette identifier.
        """
        self.header = header
        self.padding = padding
        self.get_text = get_text
        self.get_sort = get_sort
        self.get_palette = get_palette


class HorizontalScroll:
    """
    A wrapper around asciimatics' Screen.print_at and Screen.paint methods.

    It allows scroll the rows horizontally, used when moving left and right:
    the first N characters will not be printed.
    """

    def __init__(self, screen, scroll=0):
        """
        Initialize the object.

        Arguments:
            screen (Screen): The asciimatics screen object.
            scroll (int): Base scroll to use when printing. Will decrease by one with each character skipped.
        """
        self.screen = screen
        self.scroll = scroll

    def set_scroll(self, scroll):
        """Set the scroll value."""
        self.scroll = scroll

    def print_at(self, text, x, y, palette):  # noqa: WPS111
        """
        Wrapper print_at method.

        Arguments:
            text (str): Text to print.
            x (int): X axis position / column.
            y (int): Y axis position / row.
            palette (list/tuple): A length-3 tuple or a list of length-3 tuples representing asciimatics palettes.

        Returns:
            int: The number of characters actually printed.
        """
        if self.scroll == 0:
            if isinstance(palette, list):
                self.screen.paint(text, x, y, colour_map=palette)
            else:
                self.screen.print_at(text, x, y, *palette)
            written = len(text)
        else:
            text_length = len(text)
            if text_length > self.scroll:
                new_text = text[self.scroll :]
                written = len(new_text)
                if isinstance(palette, list):
                    new_palette = palette[self.scroll :]
                    self.screen.paint(new_text, x, y, colour_map=new_palette)
                else:
                    self.screen.print_at(new_text, x, y, *palette)
                self.scroll = 0
            else:
                self.scroll -= text_length
                written = 0
        return written
