from typing import List

from src.view.GUI.UserInteraction.Displayable import Displayable
from PyQt5.QtWidgets import QCheckBox, QPushButton


class TableRow:
    """a custom row for the table, that includes data to:
        1. show in the table
        2. access data that is not shown to the user"""
    def __init__(self, displayable: Displayable) -> None:
        self.displayable: Displayable = displayable
        self.children: List[TableRow] = []
        self.checkbox: QCheckBox = QCheckBox()
        if not displayable.ram_plot:
            self.checkbox.setDisabled(True)
        self.toggle_button: QPushButton = QPushButton()
        self.toggle_button.setMaximumWidth(20)
        self.button_name: str = displayable.name
        self.name_button: QPushButton = QPushButton(self.button_name.split(".o")[0].split("/")[-1])
        self.name_button.setFixedWidth(200)
        self.name_button.setToolTip(displayable.name)
        self.connected: bool = False


