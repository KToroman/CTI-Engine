import typing
from typing import List
from PyQt5.QtCore import pyqtSignal
from matplotlib.backend_bases import PickEvent
from matplotlib.backends.backend_template import FigureCanvas
from PyQt5.QtWidgets import QVBoxLayout, QWidget
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas  # type: ignore[attr-defined]

from src.view.GUI.Graph.Toolbars.ToolbarRuntime import ToolbarRuntime
from src.view.GUI.Graph.Plot import Plot


class BarWidget(QWidget):
    X_AXIS: str = "Sourcefiles"
    Y_AXIS: str = "Runtime (in sec)"
    click_signal: pyqtSignal = pyqtSignal()

    def __init__(self) -> None:
        super(BarWidget, self).__init__()

        self.categories: List[str] = []
        self.values: List[float] = []
        self.colors: List[str] = []
        self.count: List[int] = []
        self.clear_flag: bool = True
        self.bar_clicked: str = ""
        self.figure: Figure = Figure(figsize=(5, 4), dpi=100)
        self.canvas: FigureCanvas = FigureCanvas(self.figure)
        self.counter: int = 0
        self.style: str = ""  # type: ignore

        layout: QVBoxLayout = QVBoxLayout(self)
        self.toolbar: ToolbarRuntime = ToolbarRuntime(self.canvas, self)  # type: ignore[no-untyped-call]
        layout.addWidget(self.toolbar)
        layout.addWidget(typing.cast(QWidget, self.canvas))
        self.plot_bar_chart()

        # Connect pick events for the bar chart
        self.canvas.mpl_connect('pick_event', self.on_pick)  # type: ignore[arg-type]

    def add_bar(self, plot: Plot) -> None:
        """Adds bar to bar chart."""
        self.categories.append(plot.name)
        self.values.append(plot.y_values[0])
        self.colors.append(plot.color)
        self.count.append(self.counter)
        self.counter += 1

    def remove_bar(self, plot: Plot) -> None:
        """Removes bar from bar chart."""
        if plot.name in self.categories:
            self.categories.remove(plot.name)
        if plot.y_values[0] in self.values:
            self.values.remove(plot.y_values[0])
        if plot.color in self.colors:
            self.colors.remove(plot.color)
        if self.count:
            self.count.pop(-1)
            self.counter -= 1

    def plot_bar_chart(self) -> None:
        """(Re)draws bar chart."""
        # Remove previous axes labels
        self.figure.clear()
        # Create subplot for bar chart
        self.ax = self.figure.add_subplot(111)
        # Create bar chart
        # bars = self.ax.bar(self.categories, self.values, color=self.colors, label=self.categories)
        bars = self.ax.bar(self.count, self.values, color=self.colors, label=self.categories)
        self.ax.set_xticks([])
        # Add title and labels for axes
        self.ax.set_xlabel(self.X_AXIS)
        self.ax.set_ylabel(self.Y_AXIS)

        self.set_stylesheet(self.style)

        # Set the clickable property for each bar
        for bar in bars:
            bar.set_picker(True)

    def on_pick(self, event: PickEvent) -> None:
        """Reacts to click on bar."""

        self.bar_clicked = event.artist.get_label().__str__()
        self.click_signal.emit()

    def set_stylesheet(self, style: str) -> None:
        self.style = style
        if style == "Dark Mode Purple":
            self.figure.set_facecolor("#3f4361")
            self.ax.set_facecolor("#292c43")
            self.ax.tick_params(colors="#B0B3B8")
            self.ax.xaxis.label.set_color("#E4E6EB")
            self.ax.yaxis.label.set_color("#E4E6EB")
        if style == "Dark Mode":
            self.figure.set_facecolor("#18191A")
            self.ax.set_facecolor("#242526")
            self.ax.tick_params(colors="#B0B3B8")
            self.ax.xaxis.label.set_color("#E4E6EB")
            self.ax.yaxis.label.set_color("#E4E6EB")
        if style == "Light Mode":
            self.figure.set_facecolor("#D4D9EB")
            self.ax.set_facecolor("#E4E6EB")
            self.ax.tick_params(colors="#000000")
            self.ax.xaxis.label.set_color("#000000")
            self.ax.yaxis.label.set_color("#000000")
        self.canvas.draw()  # type: ignore[no-untyped-call]
