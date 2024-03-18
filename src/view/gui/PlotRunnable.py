from PyQt5.QtCore import QRunnable, QMutex

from src.view.gui.graph.BarWidget import BarWidget
from src.view.gui.graph.GraphWidget import GraphWidget
from src.view.gui.user_interaction.Displayable import Displayable


class PlotRunnable(QRunnable):

    def __init__(self, ram_graph: GraphWidget, cpu_graph: GraphWidget, runtime_graph: BarWidget, mutex: QMutex):
        super().__init__()

        self.ram_graph = ram_graph
        self.cpu_graph = cpu_graph
        self.runtime_graph = runtime_graph
        self.mutex: QMutex = mutex

    def run(self):
        self.mutex.lock()
        self.ram_graph.plot_graph()
        self.cpu_graph.plot_graph()
        self.runtime_graph.plot_bar_chart()
        self.mutex.unlock()
