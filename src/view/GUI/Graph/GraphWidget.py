

from typing import List

from PyQt5.QtCore import pyqtSignal
from matplotlib import pyplot as plt
from PyQt5.QtWidgets import QVBoxLayout, QWidget
from matplotlib.backend_bases import PickEvent
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

from src.view.GUI.Graph.CustomToolbar import CustomToolbar
from src.view.GUI.Graph.Plot import Plot


class GraphWidget(QWidget):

    X_AXIS: str = "Time (in sec)"
    click_signal: pyqtSignal = pyqtSignal()

    def __init__(self, axis_label: str, parent=None):
        super(GraphWidget, self).__init__(parent)

        self.lines: List[plt.plot] = []
        self.plot_clicked: str = ""

        self.figure, self.ax = plt.subplots(figsize=(5, 4), dpi=90)

        # Add title and labels for axes
        self.ax.set_xlabel(self.X_AXIS)
        self.ax.set_ylabel(axis_label)

        # Add layout
        self.canvas = FigureCanvas(self.figure)
        self.layout = QVBoxLayout()
        self.toolbar = CustomToolbar(self.canvas, self)
        self.layout.addWidget(self.toolbar)
        self.layout.addWidget(self.canvas)
        self.setLayout(self.layout)
        self.canvas.draw()

        # Connect pick events for the entire figure
        self.canvas.mpl_connect('pick_event', self.on_pick)

    def add_plot(self, plot: Plot):
        """adds plot to graph widget"""
        line, = self.ax.plot(plot.x_values, plot.y_values, label=plot.name, color=plot.color, linewidth=1.5)
        line.set_picker(True)

        # Add line to cpu list
        self.lines.append(line)

    def remove_plot(self, plot: Plot):
        """removes plot from graph widget"""
        for line in self.lines:
            if line.get_label() == plot.name:
                line.remove()
                self.lines.remove(line)
                break

    def plot_graph(self):
        self.ax.relim()
        self.ax.autoscale()
        self.canvas.draw()

    def on_pick(self, event: PickEvent):
        """reacts to click on graph"""
        self.plot_clicked = event.artist.get_label().__str__()
        self.click_signal.emit()

    def set_stylesheet(self, style: str):
        if style == "Dark Mode":
            self.figure.set_facecolor("#3f4361")
            self.ax.set_facecolor("#292c43")
            self.ax.tick_params(colors="#FFFFFF")  # Farbe der Zahlen an der x-Achse
            self.ax.xaxis.label.set_color("#FFFFFF")  # Farbe der x-Achsenbeschriftung
            self.ax.yaxis.label.set_color("#FFFFFF")  # Farbe der y-Achsenbeschriftung
        if style == "Light Mode":
            self.figure.set_facecolor("#FFFFFF")
            self.ax.set_facecolor("#FFFFFF")
            self.ax.tick_params(colors="#000000")  # Farbe der Zahlen an der x-Achse
            self.ax.xaxis.label.set_color("#000000")  # Farbe der x-Achsenbeschriftung
            self.ax.yaxis.label.set_color("#000000")  # Farbe der y-Achsenbeschriftung
        self.canvas.draw()
