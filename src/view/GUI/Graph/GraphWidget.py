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
        line, = self.ax.plot(plot.x_values, plot.y_values, label=plot.name)

        # Update graph
        self.ax.legend()
        self.canvas.draw()

        # Add line to ram list
        self.ram_lines.append(line)

    def add_cpu_plot(self, plot: Plot):
        line, = self.ax2.plot(plot.x_values, plot.y_values, label=plot.name)

        # Update graph
        self.ax2.legend()
        self.canvas.draw()

        # Add line to cpu list
        self.cpu_lines.append(line)

    def remove_ram_plot(self, plot: Plot):
        # Find ram line belonging to Plot and remove said ram line
        for line in self.ram_lines:
            if line.get_label() == plot.name:
                line.remove()
                self.ram_lines.remove(line)
                self.ax.legend()
                self.canvas.draw()
                break

    def remove_cpu_plot(self, plot: Plot):
        # Find cpu line belonging to Plot and remove said cpu line
        for line in self.cpu_lines:
            if line.get_label() == plot.name:
                line.remove()
                self.cpu_lines.remove(line)
                self.ax2.legend()
                self.canvas.draw()
                break
