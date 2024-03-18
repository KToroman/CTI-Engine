from multiprocessing import Queue
from typing import List

from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QPushButton


class ProjectNameButton(QPushButton):
    def __init__(self, project_buttons: List[QPushButton], show_name: str, project_name: str, project_queue: Queue,
                 visualize_event: pyqtSignal, index_queue: Queue,
                 change_table_signal: pyqtSignal, *__args):
        super().__init__(*__args)
        self.show_name = show_name
        self.project_name = project_name
        self.__project_queue = project_queue
        self.__visualize_event = visualize_event
        self.setText(show_name)
        self.button_list = project_buttons
        self.clicked.connect(lambda: self.__show_project_name_input(self.button_list.index(self)))
        self.index_queue = index_queue
        self.change_table_signal = change_table_signal

    def __show_project_name_input(self, index: int):
        """opens an input dialog to confirm the project you are about to load"""
        for button in self.button_list:
            button.setStyleSheet("")
        self.setStyleSheet("background-color: #00FF00")
        self.index_queue.put(index)
        self.change_table_signal.emit()


