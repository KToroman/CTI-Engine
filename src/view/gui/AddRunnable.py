from PyQt5.QtCore import QRunnable, QMutex

from src.view.gui.graph.BarWidget import BarWidget
from src.view.gui.graph.GraphWidget import GraphWidget
from src.view.gui.user_interaction.Displayable import Displayable


class AddRunnable(QRunnable):

    def __init__(self, ram_graph: GraphWidget,  cpu_graph: GraphWidget, runtime_graph: BarWidget,
                 displayable: Displayable, mutex: QMutex):
        super().__init__()

        self.ram_graph = ram_graph
        self.cpu_graph = cpu_graph
        self.runtime_graph = runtime_graph
        self.displayable = displayable
        self.mutex: QMutex = mutex


    def run(self):
        self.mutex.lock()
        print("adding graphs in runnable")
        self.ram_graph.add_plot(self.displayable.ram_plot)
        self.cpu_graph.add_plot(self.displayable.cpu_plot)
        self.runtime_graph.add_bar(self.displayable.runtime_plot)
        self.mutex.unlock()
