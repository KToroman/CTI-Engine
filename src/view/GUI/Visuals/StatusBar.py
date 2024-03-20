import time
from typing import Optional

from PyQt5 import QtCore
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QLabel, QWidget, QHBoxLayout, QBoxLayout, QVBoxLayout, QGridLayout
from src.model.core.StatusSettings import StatusSettings


class StatusBar(QWidget):
    """StatusBar is used to display the program's status."""
    WINDOW_SIZE: int = 20
    SIZE_X: int = 300
    SIZE_Y: int = 100

    SPACING: int = 10
    STATUS_TEXT: str = "Status: "

    def __init__(self) -> None:
        super().__init__()
        # Create Components of StatusBar

        self.counter: int = 0
        self.last_update: int = 0

        self.project_name: QLabel = QLabel(self)
        self.project_name.setText("[]")
        self.setFixedSize(self.SIZE_X, self.SIZE_Y)
        self.status_message: QLabel = QLabel(self)
        self.color_window: QLabel = QLabel(self)
        self.color_window.setFixedSize(self.WINDOW_SIZE, self.WINDOW_SIZE)
        # Setup Layout for StatusBar
        layout: QVBoxLayout = QVBoxLayout()
        layout.addWidget(self.project_name)
        layout_1: QHBoxLayout = QHBoxLayout()
        layout_1.addWidget(self.color_window)
        layout_1.addWidget(self.status_message)
        layout_1.addStretch(4)
        layout_1.setSpacing(self.SPACING)
        layout_1.setAlignment(Qt.AlignHCenter)
        layout.setSpacing(0)
        layout.addLayout(layout_1)
        layout_1.setAlignment(Qt.AlignRight)
        self.show_list: list[str] = ["|", "/", "-", "\\"]
        self.dot_list: list[str] = ["", ".", "..", "..."]

        self.setLayout(layout)

        self.layout().setAlignment(Qt.AlignTop)
        # Initialize StatusBar to WAITING
        self.__name: str|None = ""
        self.name_counter: int = 0
        self.build_string = ""
        self.update_status(StatusSettings.WAITING, "")

    def update_status(self, status: StatusSettings, project_name: Optional[str]) -> None:
        """Updates the statusbar according to a given setting."""
        if project_name != self.__name:
            self.build_string = ""
            self.__name = project_name
            self.name_counter = 0
        if self.__name is None:
            raise Exception
        if self.name_counter < len(self.__name):
            self.build_string += self.__name[self.name_counter]
            self.name_counter += 1
        if self.__name == "":
            self.build_string = " " + self.show_list[self.counter % self.show_list.__len__()] + " "
        self.project_name.setText(f"[{self.build_string}]")

        dots = self.dot_list[self.counter % self.dot_list.__len__()]

        self.counter += 1

        self.status_message.setText(status.value[0] + dots)
        self.color_window.setStyleSheet(f"background-color: {status.value[1]}")
        self.update()
