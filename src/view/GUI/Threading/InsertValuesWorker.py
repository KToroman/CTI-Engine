from PyQt5.QtCore import QRunnable, QThreadPool

from src.view.GUI.Graph.BarWidget import BarWidget
from src.view.GUI.Graph.GraphWidget import GraphWidget
from src.view.GUI.UserInteraction.Displayable import Displayable
from src.view.GUI.UserInteraction.DisplayableHolder import DisplayableHolder
from src.view.GUI.UserInteraction.ItemWrapper import ItemWrapper


class InsertValuesWorker(QRunnable):

    def __init__(self, displayable_holder: DisplayableHolder, thread_pool: QThreadPool, parent):
        super().__init__()

        self.displayable_holder: DisplayableHolder = displayable_holder
        self.thread_pool: QThreadPool = thread_pool
        self.parent = parent


    def run(self):
        if not self.displayable_holder.get_sub_disp():
            item = ItemWrapper(self.displayable_holder.displayable.name, self.parent)
            self.__create_row(item, self.displayable_holder.displayable)
            return
        item = ItemWrapper(self.displayable_holder.displayable.name, self.parent)
        #self.__create_row(item, self.displayable_holder.displayable)
        for h in self.displayable_holder.get_sub_disp():
            """insert_values_worker: InsertValuesWorker = InsertValuesWorker(displayable_holder=h, thread_pool=self.thread_pool, parent=item)
            self.thread_pool.start(insert_values_worker)"""
            self.insert_data(h, item)
