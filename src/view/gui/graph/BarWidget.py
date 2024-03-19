from typing import List
from PyQt5.QtCore import pyqtSignal, pyqtSlot
from matplotlib.backend_bases import PickEvent
from matplotlib.backends.backend_template import FigureCanvas
from PyQt5.QtWidgets import QVBoxLayout, QWidget
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

from src.view.gui.graph.CustomToolbar import CustomToolbar
from src.view.gui.graph.Plot import Plot


class BarWidget(QWidget):

    X_AXIS: str = "Sourcefiles"
    Y_AXIS: str = "Runtime (in sec)"
    click_signal: pyqtSignal = pyqtSignal()

    def __init__(self):
        super(BarWidget, self).__init__()

        self.categories: List[str] = []
        self.values: List[float] = []
        self.colors: List[str] = []
        self.clear_flag: bool = True
        self.bar_clicked: str = ""

        self.figure = Figure(figsize=(5, 4), dpi=100)
        self.canvas = FigureCanvas(self.figure)

        layout = QVBoxLayout(self)
        self.toolbar = CustomToolbar(self.canvas, self)
        layout.addWidget(self.toolbar)
        layout.addWidget(self.canvas)
        self.plot_bar_chart()

        # Connect pick events for the bar chart
        self.canvas.mpl_connect('pick_event', self.on_pick)

    def add_bar(self, plot: Plot):
        """Adds bar to bar chart."""
        self.categories.append(plot.name)
        self.values.append(plot.y_values[0])
        self.colors.append(plot.color)

        # Update chart
        #self.__plot_bar_chart()

    def remove_bar(self, plot: Plot):
        """Removes bar from bar chart."""
        self.categories.remove(plot.name)
        self.values.remove(plot.y_values[0])
        self.colors.remove(plot.color)

        # Update chart
        #self.__plot_bar_chart()

    def plot_bar_chart(self):
        """(Re)draws bar chart."""

        # Remove previous axes labels
        self.figure.clear()
        #self.figure.set_facecolor("#61b3bf")
        # Create subplot for bar chart
        self.ax = self.figure.add_subplot(111)
        # Create bar chart
        bars = self.ax.bar(self.categories, self.values, color=self.colors, label=self.categories)
        self.ax.set_xticks([])
        # Add title and labels for axes
        self.ax.set_xlabel(self.X_AXIS)
        self.ax.set_ylabel(self.Y_AXIS)

        # Draw diagram on canvas
        self.canvas.draw()

        # Set the clickable property for each bar
        for bar in bars:
            bar.set_picker(True)

    def on_pick(self, event: PickEvent):
        """Reacts to click on bar."""
        self.bar_clicked = event.artist.get_label().__str__()
        self.click_signal.emit()