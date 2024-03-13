from multiprocessing import Queue
from typing import List
from PyQt5.QtCore import QRunnable, pyqtSignal
from src.view.GUI.UserInteraction.Displayable import Displayable
from src.view.GUI.UserInteraction.TableWidget import TableWidget


class InsertTableWorker(QRunnable):

    def __init__(self, displayable: Displayable, table_signal: pyqtSignal, table: TableWidget):
        super().__init__()

        self.table: TableWidget = table
        self.displayable = displayable
        #self.displayables: List[Displayable] = displayables
        #self.table_signal: pyqtSignal = table_signal
        #self.table_queue: Queue = table_queue

    """def run(self):
        print("[TableWorker]   in run")
        #table = self.table_queue.get()
        for displayable in self.displayables:
            print("[TableWorker]   one displayable")
            self.table.insert_values(displayable)
        print("[TableWorker]   after insert values")
        #self.table.rebuild_table(self.table.rows)
        #print("[TableWorker]   after rebuild table")
        self.table_signal.emit()
"""
    def run(self):

        self.table.insert_values(displayable=self.displayable)
