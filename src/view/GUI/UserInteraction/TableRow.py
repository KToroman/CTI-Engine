from typing import List

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor

from src.view.GUI.UserInteraction.Displayable import Displayable
from PyQt5.QtWidgets import QCheckBox, QPushButton, QWidget, QHBoxLayout, QTableWidgetItem, QTableWidget


class TableRow(QTableWidget):
    NUMBER_OF_COLUMNS = 5
    COLUMN_1_LABEL = "Name"
    COLUMN_2_LABEL = "Peak RAM(MB)"
    COLUMN_3_LABEL = "Peak CPU (%)"
    COLUMN_4_LABEL = "Runtime"

    def __init__(self, displayable: Displayable, is_child: bool):
        super().__init__()

        self.setColumnCount(self.NUMBER_OF_COLUMNS)
        self.setHorizontalHeaderLabels([self.COLUMN_1_LABEL, self.COLUMN_2_LABEL,
                                        self.COLUMN_3_LABEL, self.COLUMN_4_LABEL])
        self.setStyleSheet("::section{Background-color: #4095a1}")
        self.horizontalHeader().setStyleSheet("::section{Background-color: #4095a1}")
        self.verticalHeader().setStyleSheet("::section{Background-color: #4095a1}")

        self.displayable: Displayable = displayable
        self.is_child = is_child
        self.children: List[TableRow] = []
        self.checkbox: QCheckBox = QCheckBox()

        for column in range(self.columnCount()):
            self.horizontalHeader().sectionClicked.connect(lambda col=column: self.sort_table(col))
        self.insertion_point: str = ""

        if self.is_child:
            self.checkbox.setDisabled(True)

        self.toggle_button: QPushButton = QPushButton()
        self.toggle_button.setMaximumWidth(20)
        self.name_button: QPushButton = QPushButton(displayable.name)
        self.connected: bool = False

    def make_row(self, displayable: Displayable):
        row_pos: int = self.rowCount()
        self.insertRow(row_pos)
        row: TableRow = TableRow(displayable, True)
        self.children.append(row)
        self.fill_row(row, row_pos)
        self.setRowHeight(self.children.index(row), 50)
        self.set_row_color(self.children.index(row), QColor(220, 220, 220))
        if self.is_child:
            self.set_row_color(self.children.index(row), QColor(170, 170, 170))
        return row

    def fill_row(self, row, index):
        if len(row.children) != 0:
            row.toggle_button.setText("v")

        cell_widget = QWidget()
        layout = QHBoxLayout(cell_widget)
        layout.addWidget(row.checkbox)
        layout.addWidget(row.name_button)
        layout.addWidget(row.toggle_button)

        self.setItem(index, 0, QTableWidgetItem(self.setCellWidget(index, 0, cell_widget)))
        item: QTableWidgetItem = QTableWidgetItem()
        item.setData(Qt.DisplayRole, row.displayable.ram_peak)
        item.setData(Qt.UserRole, row.displayable.name)
        self.setItem(index, 1, item)
        item2: QTableWidgetItem = QTableWidgetItem()
        item2.setData(Qt.DisplayRole, row.displayable.cpu_peak)
        self.setItem(index, 2, item2)
        item3: QTableWidgetItem = QTableWidgetItem()
        if row.displayable.runtime_plot.y_values:
            item3.setData(Qt.DisplayRole, row.displayable.runtime_plot.y_values[0])
            self.setItem(index, 3, item3)
        else:
            item3.setData(Qt.DisplayRole, 0)
            self.setItem(index, 3, item3)

    def set_row_color(self, row, color):
        for column in range(self.columnCount()-1):
            item = self.item(row, column)
            item.setBackground(color)
