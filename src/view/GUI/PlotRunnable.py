from PyQt5.QtCore import QRunnable

from src.view.GUI.Graph.BarWidget import BarWidget
from src.view.GUI.Graph.GraphWidget import GraphWidget
from src.view.GUI.UserInteraction.Displayable import Displayable


class PlotRunnable(QRunnable):

    def __init__(self, ram_graph: GraphWidget,  cpu_graph: GraphWidget, runtime_graph: BarWidget):
        super().__init__()

        self.ram_graph = ram_graph
        self.cpu_graph = cpu_graph
        self.runtime_graph = runtime_graph


    def run(self):
        self.ram_graph.plot_graph()
        self.cpu_graph.plot_graph()
        self.runtime_graph.plot_bar_chart()