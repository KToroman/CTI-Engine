from typing import List

from matplotlib.backends.backend_template import FigureCanvas
from PyQt5.QtWidgets import QVBoxLayout, QWidget
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

from src.view.GUI.Graph.Plot import Plot


class BarWidget(QWidget):

    X_AXIS: str = "Sourcefiles"
    Y_AXIS: str = "Runtime"

    categories: List[str] = []
    values: List[float] = []
    colors: List[str] = []
    clear_flag: bool = True

    def __init__(self):
        super(BarWidget, self).__init__()

        self.figure = Figure(figsize=(5, 4), dpi=100)
        self.canvas = FigureCanvas(self.figure)

        layout = QVBoxLayout(self)
        layout.addWidget(self.canvas)
        self.__plot_bar_chart()

    def add_bar(self, plot: Plot):
        """adds bar to bar chart"""
        self.categories.append(plot.name)
        self.values.append(plot.y_values[0])
        self.colors.append(plot.color)

        # Update chart
        self.__plot_bar_chart()

    def remove_bar(self, plot: Plot):
        """removes bar from bar chart"""
        self.categories.remove(plot.name)
        self.values.remove(plot.y_values[0])
        self.colors.remove(plot.color)

        # Update chart
        self.__plot_bar_chart()

    def __plot_bar_chart(self):
        """(re)draws bar chart"""

        # Remove previous axes labels
        self.figure.clear()

        # Create subplot for bar chart
        self.ax = self.figure.add_subplot(111)

        # Create bar chart
        self.ax.bar(self.categories, self.values, color=self.colors)

        # Add title and labels for axes
        self.ax.set_xlabel(self.X_AXIS)
        self.ax.set_ylabel(self.Y_AXIS)

        # Draw diagram on canvas
        self.canvas.draw()

    def toggle_chart(self):
        """shows or hides bar chart"""
        if self.clear_flag:
            self.__plot_bar_chart()
            self.clear_flag = False
        else:
            self.ax.clear()
            self.clear_flag = True
        self.canvas.draw()