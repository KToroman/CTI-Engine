from typing import List

from src.view.GUI.UserInteraction.Displayable import Displayable
from PyQt5.QtWidgets import QCheckBox, QPushButton, QWidget, QHBoxLayout, QTableWidgetItem


class TableRow:
    def __init__(self, displayable: Displayable):
        self.displayable: Displayable = displayable
        self.children: List[TableRow] = []
        self.checkbox: QCheckBox = QCheckBox()
        if not displayable.ram_plot:
            self.checkbox.setDisabled(True)
        self.toggle_button: QPushButton = QPushButton()
        self.toggle_button.setMaximumWidth(20)
        self.button_name = displayable.name.split('/')
        self.name_button: QPushButton = QPushButton(self.button_name[-1] + '/'
                                                    + self.button_name[len(self.button_name) - 2])
        self.name_button.setFixedWidth(150)
        self.name_button.setToolTip(displayable.name)
        self.connected: bool = False


