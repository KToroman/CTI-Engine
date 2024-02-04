from typing import List
from matplotlib import pyplot as plt
from matplotlib.backends.backend_template import FigureCanvas
from PyQt5.QtWidgets import QVBoxLayout, QWidget
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from src.view.GUI.Graph.Plot import Plot


class GraphWidget(QWidget):

    X_AXIS: str = "Time (in sec)"
    RAM_Y_AXIS: str = "RAM (in mb)"
    CPU_Y_AXIS: str = "CPU (in %)"

    ram_lines: List[plt.plot] = []
    cpu_lines: List[plt.plot] = []

    def __init__(self, parent=None):
        super(GraphWidget, self).__init__(parent)

        self.figure, self.ax = plt.subplots(figsize=(5, 4), dpi=100)
        self.ax2 = self.ax.twinx()

        # Add title and labels for axes
        self.ax.set_xlabel(self.X_AXIS)
        self.ax.set_ylabel(self.RAM_Y_AXIS)
        self.ax2.set_ylabel(self.CPU_Y_AXIS)

        # Add layout
        self.canvas = FigureCanvas(self.figure)
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.canvas)
        self.setLayout(self.layout)
        self.canvas.draw()

    def add_ram_plot(self, plot: Plot):
        """adds ram plot to graph widget"""
        line, = self.ax.plot(plot.x_values, plot.y_values, label=plot.name, color=plot.color)

        # Update graph
        if not self.ax.get_yaxis().get_visible():
            line.set_visible(False)
        self.canvas.draw()

        # Add line to ram list
        self.ram_lines.append(line)

    def add_cpu_plot(self, plot: Plot):
        """adds cpu plot to graph widget"""
        line, = self.ax2.plot(plot.x_values, plot.y_values, label=plot.name, color=plot.color)

        # Update graph
        if not self.ax2.get_yaxis().get_visible():
            line.set_visible(False)
        self.canvas.draw()

        # Add line to cpu list
        self.cpu_lines.append(line)

    def remove_ram_plot(self, plot: Plot):
        """removes ram plot from graph widget"""
        for line in self.ram_lines:
            if line.get_label() == plot.name:
                line.remove()
                self.ram_lines.remove(line)
                self.canvas.draw()
                break

    def remove_cpu_plot(self, plot: Plot):
        """removes cpu plot from graph widget"""
        for line in self.cpu_lines:
            if line.get_label() == plot.name:
                line.remove()
                self.cpu_lines.remove(line)
                self.canvas.draw()
                break

    def toggle_ram(self):
        """shows or hides ram plots"""
        visibility = not self.ax.get_yaxis().get_visible()
        self.ax.get_yaxis().set_visible(visibility)
        self.__update_plot_visibility(self.ram_lines, visibility)
        self.canvas.draw()

    def toggle_cpu(self):
        """shows or hides cpu plots"""
        visibility = not self.ax2.get_yaxis().get_visible()
        self.ax2.get_yaxis().set_visible(visibility)
        self.__update_plot_visibility(self.cpu_lines, visibility)
        self.canvas.draw()

    def __update_plot_visibility(self, lines, visible):
        """updates visibility for given lines"""
        for line in lines:
            line.set_visible(visible)