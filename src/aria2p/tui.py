from __future__ import annotations

import random

from rich import box
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from textual.app import App
from textual.widget import Widget

from aria2p import API
from aria2p.braille import BrailleStream


class Stats(Widget):
    def on_mount(self):
        # self.width = 0
        # self.height = 0

        self.stats_stream = BrailleStream(50, 1, 0, 10000)
        self.panel = Panel(
            "",
            title="[b]stats[/]",
            title_align="left",
            border_style="white",
            box=box.SQUARE,
        )

        # immediately collect data to refresh info_box_width
        self.collect_data()
        self.set_interval(0.5, self.collect_data)

    def collect_data(self):
        # self.fan_stream.maxval = fan_current
        self.stats_stream.add_value(random.randint(0, 10000))

        t = Table(expand=True, show_header=False, padding=0, box=None)
        # Add ratio 1 to expand that column as much as possible
        t.add_column("graph", no_wrap=True, ratio=1)

        graph = Text(
            self.stats_stream.graph[-1],
            style="cyan",
        )
        t.add_row(graph, "")

        self.panel.renderable = t

        # textual method
        self.refresh()

    def render(self):
        return self.panel

    async def on_resize(self, event):
        self.width = event.width
        self.height = event.height
        # reset graph widths
        graph_width = self.width - 5
        self.stats_stream.reset_width(graph_width)
        # reset graph heights
        total_height = self.height - 2
        self.stats_stream.reset_height(total_height)


class DownloadList(Widget):
    def on_mount(self):
        self.collect_data()
        self.set_interval(0.5, self.collect_data)

    def collect_data(self):
        downloads = API().get_downloads()

        table = Table(
            show_header=True,
            header_style="bold",
            box=None,
            padding=(0, 1),
            expand=True,
        )
        # set ration=1 on all columns that should be expanded
        # <https://github.com/Textualize/rich/issues/2030>
        table.add_column(Text("gid", justify="right"), no_wrap=True, justify="right")
        table.add_column("status", style="green", no_wrap=True, ratio=1)
        table.add_column("progress", no_wrap=True, ratio=2)
        table.add_column(
            Text("size", justify="left"),
            style="green",
            no_wrap=True,
            justify="right",
        )
        table.add_column("down speed", no_wrap=True)
        table.add_column(Text("up speed", justify="left"), style="green", no_wrap=True, justify="right")
        table.add_column(
            Text("eta", style="u", justify="left"),
            no_wrap=True,
            justify="right",
        )
        table.add_column(
            Text("name", justify="left"),
            no_wrap=True,
            justify="right",
        )

        for download in downloads:
            table.add_row(
                download.gid,
                download.status,
                download.progress_string(),
                download.total_length_string(),
                download.download_speed_string(),
                download.upload_speed_string(),
                download.eta_string(precision=2),
                download.name,
            )

        self.panel = Panel(
            table,
            title=f"[b]downloads[/] - {len(downloads)}",
            title_align="left",
            # border_style="cyan",
            border_style="white",
            box=box.SQUARE,
        )

        self.refresh()

    def render(self) -> Panel:
        return self.panel

    async def on_resize(self, event):
        self.width = event.width
        self.height = event.height


class MainApp(App):
    async def on_load(self) -> None:
        """Bind keys here."""
        await self.bind("q", "quit", "Quit")
        await self.bind("t", "tweet", "Tweet")
        await self.bind("r", "None", "Record")

    async def on_mount(self) -> None:
        # await self.view.dock(Stats())
        await self.view.dock(DownloadList())
        # grid = await self.view.dock_grid(edge="left")

        # grid.add_row(fraction=1, name="r1")
        # grid.add_row(fraction=1, name="r2")
        # grid.add_areas(
        #     area1="left,r1",
        #     area2="left,r2",
        # )
        # grid.place(
        #     area1=Stats(),
        #     area2=DownloadList(),
        # )


if __name__ == "__main__":
    MainApp.run(title="aria2p")
