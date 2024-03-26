from multiprocessing import Queue
from typing import List, Any

from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QPushButton


class ProjectNameButton(QPushButton):
    def __init__(self, project_buttons: List[QPushButton], show_name: str, project_name: str,
                 project_queue: "Queue[str]", visualize_event: pyqtSignal, index_queue: "Queue[int]",
                 change_table_signal: pyqtSignal, *__args: Any) -> None:
        super().__init__(*__args)
        self.show_name: str = show_name
        self.project_name: str = project_name
        self.__project_queue: "Queue[str]" = project_queue
        self.__visualize_event: pyqtSignal = visualize_event  # type: ignore[assignment]
        self.setText(show_name)
        self.button_list: List[QPushButton] = project_buttons
        self.clicked.connect(lambda: self.__show_project_name_input(self.button_list.index(self)))
        self.index_queue: "Queue[int]" = index_queue
        self.change_table_signal: pyqtSignal = change_table_signal  # type: ignore[assignment]
        self.setToolTip(project_name)
        self.setMinimumWidth(40)

    def __show_project_name_input(self, index: int) -> None:
        """opens an input dialog to confirm the project you are about to load"""
        for button in self.button_list:
            button.setStyleSheet("")
        self.setStyleSheet("background-color: #00FF00")
        self.index_queue.put(index)
        self.change_table_signal.emit()  # type: ignore[attr-defined]


