from typing import List

from Displayable import Displayable
from PyQt5.QtWidgets import QCheckBox, QPushButton, QWidget, QHBoxLayout, QTableWidgetItem


class TableRow:
    def __init__(self, displayable: Displayable):
        self.displayable: Displayable = displayable
        self.children : List[TableRow] = []
        self.custom_cell: CustomCellWidget = CustomCellWidget(self.displayable.name)

    def add_child(self, child):
        self.children.append(child)


# A custom cell for the table, containing the checkbox, the name and a button to show hidden subrows
class CustomCellWidget(QWidget):
    def __init__(self, name: str):
        super().__init__()
        self.checkbox: QCheckBox = QCheckBox()
        self.toggle_button: QPushButton = QPushButton("v")
        self.toggle_button.setMaximumWidth(20)
        self.name_button : QPushButton = QPushButton(name)
        self.label: QTableWidgetItem = QTableWidgetItem()
        self.label.setText(name)

        self.layout: QHBoxLayout = QHBoxLayout()
        self.layout.addWidget(self.checkbox)
        self.layout.addWidget(self.toggle_button)
        self.layout.addWidget(self.name_button)
        self.setLayout(self.layout)
