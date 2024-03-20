

from typing import List

from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QIcon
from matplotlib import pyplot as plt
from PyQt5.QtWidgets import QVBoxLayout, QWidget
from matplotlib.backend_bases import PickEvent
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas # type: ignore[attr-defined]
from matplotlib.lines import Line2D

from src.view.GUI.Graph.CustomToolbar import CustomToolbar
from src.view.GUI.Graph.Plot import Plot


class GraphWidget(QWidget):

    X_AXIS: str = "Time (in sec)"
    click_signal: pyqtSignal = pyqtSignal()

    def __init__(self, axis_label: str, parent: QWidget | None = None) -> None:
        super(GraphWidget, self).__init__(parent)

        self.lines: List[Line2D] = []
        self.plot_clicked: str = ""

        self.figure, self.ax = plt.subplots(figsize=(5, 4), dpi=90)

        # Add title and labels for axes
        self.ax.set_xlabel(self.X_AXIS)
        self.ax.set_ylabel(axis_label)

        # Add layout
        self.canvas: FigureCanvas = FigureCanvas(self.figure)  # type: ignore[no-untyped-call]
        self.layout: QVBoxLayout = QVBoxLayout()  # type: ignore[assignment]
        self.toolbar: CustomToolbar = CustomToolbar(self.canvas, self)  # type: ignore[no-untyped-call]
        self.layout.addWidget(self.toolbar)
        self.layout.addWidget(self.canvas)
        self.setLayout(self.layout)
        self.canvas.draw()  # type: ignore[no-untyped-call]

        # Connect pick events for the entire figure
        self.canvas.mpl_connect('pick_event', self.on_pick)  # type: ignore[arg-type]

    def add_plot(self, plot: Plot) -> None:
        """adds plot to graph widget"""
        line, = self.ax.plot(plot.x_values, plot.y_values, label=plot.name, color=plot.color, linewidth=1.5)
        line.set_picker(True)

        # Add line to cpu list
        self.lines.append(line)

    def remove_plot(self, plot: Plot) -> None:
        """removes plot from graph widget"""
        for line in self.lines:
            if line.get_label() == plot.name:
                line.remove()
                self.lines.remove(line)
                break

    def plot_graph(self) -> None:
        self.ax.relim()
        self.ax.autoscale()
        self.canvas.draw()  # type: ignore[no-untyped-call]

    def on_pick(self, event: PickEvent) -> None:
        """reacts to click on graph"""
        self.plot_clicked = event.artist.get_label().__str__()
        self.click_signal.emit()

    def set_stylesheet(self, style: str) -> None:
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
