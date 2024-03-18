from PyQt5.QtCore import QRunnable, QMutex

from src.view.GUI.Graph.BarWidget import BarWidget
from src.view.GUI.Graph.GraphWidget import GraphWidget
from src.view.GUI.UserInteraction.Displayable import Displayable


class PlotRunnable(QRunnable):

    def __init__(self, ram_graph: GraphWidget,  cpu_graph: GraphWidget, runtime_graph: BarWidget, mutex: QMutex):
        super().__init__()

        self.ram_graph: GraphWidget = ram_graph
        self.cpu_graph: GraphWidget = cpu_graph
        self.runtime_graph: BarWidget = runtime_graph
        self.mutex: QMutex = mutex


    def run(self):
        self.mutex.lock()
        self.ram_graph.plot_graph()
        self.cpu_graph.plot_graph()
        self.runtime_graph.plot_bar_chart()
        self.mutex.unlock()
