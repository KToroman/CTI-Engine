from PyQt5.QtCore import QRunnable

from src.view.GUI.Graph.BarWidget import BarWidget
from src.view.GUI.Graph.GraphWidget import GraphWidget
from src.view.GUI.UserInteraction.Displayable import Displayable


class AddRunnable(QRunnable):

    def __init__(self, ram_graph: GraphWidget,  cpu_graph: GraphWidget, runtime_graph: BarWidget,
                 displayable: Displayable):
        super().__init__()

        self.ram_graph = ram_graph
        self.cpu_graph = cpu_graph
        self.runtime_graph = runtime_graph
        self.displayable = displayable


    def run(self):
        self.ram_graph.add_plot(self.displayable.ram_plot)
        self.cpu_graph.add_plot(self.displayable.cpu_plot)
        self.runtime_graph.add_bar(self.displayable.runtime_plot)
