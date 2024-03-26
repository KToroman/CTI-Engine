from PyQt5.QtCore import QRunnable, QMutex
from src.view.GUI.Graph.BarWidget import BarWidget
from src.view.GUI.Graph.GraphWidget import GraphWidget
from src.view.GUI.UserInteraction.Displayable import Displayable


class AddRunnable(QRunnable):

    def __init__(self, ram_graph: GraphWidget,  cpu_graph: GraphWidget, runtime_graph: BarWidget,
                 displayable: Displayable, mutex: QMutex) -> None:
        super().__init__()

        self.ram_graph: GraphWidget = ram_graph
        self.cpu_graph: GraphWidget = cpu_graph
        self.runtime_graph: BarWidget = runtime_graph
        self.displayable: Displayable = displayable
        self.mutex = mutex

    def run(self) -> None:
        self.ram_graph.add_plot(self.displayable.ram_plot)
        self.cpu_graph.add_plot(self.displayable.cpu_plot)
        self.mutex.lock()
        self.runtime_graph.add_bar(self.displayable.runtime_plot)
        self.mutex.unlock()
