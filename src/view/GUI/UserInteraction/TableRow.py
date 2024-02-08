from typing import List

from src.view.GUI.UserInteraction.Displayable import Displayable
from PyQt5.QtWidgets import QCheckBox, QPushButton, QWidget, QHBoxLayout, QTableWidgetItem


class TableRow:
    def __init__(self, displayable: Displayable, is_child: bool):
        self.displayable: Displayable = displayable
        self.is_child = is_child
        self.children: List[TableRow] = []
        self.checkbox: QCheckBox = QCheckBox()
        if self.is_child:
            self.checkbox.setDisabled(True)
        self.toggle_button: QPushButton = QPushButton()
        self.toggle_button.setMaximumWidth(20)
        self.name_button: QPushButton = QPushButton(displayable.name)
        self.connected: bool = False


