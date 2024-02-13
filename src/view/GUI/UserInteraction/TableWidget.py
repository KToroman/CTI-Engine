import copy
import time
from threading import Thread
import time
from random import randrange
from typing import List

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QTableWidget, QTableWidgetItem, QInputDialog, QWidget, QHBoxLayout, QCheckBox

from src.view.GUI.Graph.Plot import Plot
# from src.view.AppRequestsInterface import AppRequestsInterface
from src.view.GUI.UserInteraction.Displayable import Displayable
from src.view.GUI.UserInteraction.DisplayableHolder import DisplayableHolder
from src.view.GUI.UserInteraction.DisplayableInterface import DisplayableInterface
from src.view.GUI.UserInteraction.TableRow import TableRow
from src.view.AppRequestsInterface import AppRequestsInterface


class TableWidget(QTableWidget):
    NUMBER_OF_COLUMNS = 4
    COLUMN_1_LABEL = "Name"
    COLUMN_2_LABEL = "Peak RAM(MB)"
    COLUMN_3_LABEL = "Peak CPU (%)"
    COLUMN_4_LABEL = "Runtime"

    def __init__(self, app: AppRequestsInterface):
        super().__init__()
        self.app_request_interface = app
        self.setColumnCount(self.NUMBER_OF_COLUMNS)
        self.rows: List[TableRow] = []
        self.setHorizontalHeaderLabels([self.COLUMN_1_LABEL, self.COLUMN_2_LABEL,
                                        self.COLUMN_3_LABEL, self.COLUMN_4_LABEL])
        self.setStyleSheet("::section{Background-color: #4095a1}")
        self.horizontalHeader().setStyleSheet("::section{Background-color: #4095a1}")
        self.verticalHeader().setStyleSheet("::section{Background-color: #4095a1}")
        for column in range(self.columnCount()):
            self.horizontalHeader().sectionClicked.connect(lambda col=column: self.sort_table(col))
        self.insertion_point: str = ""
        self.active_started: bool = False
        self.all_selected: bool = False
        # self.app_request_interface = AppRequestsInterface()

    def insert_data_row(self, displayable_holder: DisplayableInterface, row: TableRow):
        if not displayable_holder.get_sub_disp():
            self.make_row(displayable_holder.get_disp(), row)
            return
        p_row = self.make_row(displayable_holder.get_disp(), row)
        for h in displayable_holder.get_sub_disp():
            self.insert_data_row(h, p_row)

    def make_row(self, displayable: Displayable, caller_row: TableRow) -> TableRow:
        if caller_row is None:
            row_pos: int = self.rowCount()
            self.insertRow(row_pos)
            row: TableRow = TableRow(displayable, False)
            self.rows.append(row)
            self.fill_row(row, row_pos)
            self.setRowHeight(self.rows.index(row), 40)
            row.toggle_button.clicked.connect(lambda: self.toggle_row_vis(row))
            row.name_button.clicked.connect(lambda: self.show_input_dialog_active(row.displayable.name))
            return row

        sub_row: TableRow = TableRow(displayable, True)
        caller_row.children.append(sub_row)
        self.rows.insert(self.rows.index(caller_row) + caller_row.children.index(sub_row) + 1, sub_row)
        self.insertRow(self.rows.index(caller_row) + caller_row.children.index(sub_row) + 1)
        self.fill_row(sub_row, self.rows.index(caller_row) + caller_row.children.index(sub_row) + 1)
        self.setRowHeight(self.rows.index(sub_row), 30)
        sub_row.toggle_button.clicked.connect(lambda: self.toggle_row_vis(sub_row))
        sub_row.name_button.clicked.connect(lambda: self.show_input_dialog_active(sub_row.displayable.name))

        caller_row.toggle_button.clicked.connect(lambda: self.toggle_row_vis(caller_row))
        caller_row.name_button.clicked.connect(lambda: self.show_input_dialog_active(caller_row.displayable.name))

        self.set_row_color(self.rows.index(sub_row), QColor(220, 220, 220))
        if caller_row.is_child:
            self.set_row_color(self.rows.index(sub_row), QColor(170, 170, 170))

        return sub_row

    def insert_values(self, displayable_holder: DisplayableHolder):
        self.insert_data_row(displayable_holder, None)

    def set_row_color(self, row, color):
        for column in range(self.columnCount()):
            item = self.item(row, column)
            item.setBackground(color)

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

    def fill_subrow(self, displayable: Displayable):
        for row in self.rows:
            if row.displayable.name == displayable.name:
                row.displayable = displayable

    def toggle_row_vis(self, row):
        for subrow in row.children:
            if len(subrow.children) != 0:
                self.hide_rows(subrow)
            pos = self.rows.index(subrow)
            if self.isRowHidden(pos):
                self.setRowHidden(pos, False)
                row.toggle_button.setText("^")
            else:
                self.setRowHidden(pos, True)
                row.toggle_button.setText("v")

    def hide_rows(self, row):
        for subrow in row.children:
            self.hide_rows(subrow)
            pos = self.rows.index(subrow)
            self.setRowHidden(pos, True)
            row.toggle_button.setText("v")

    def start_active_measurement(self, name):
        self.insertion_point: str = name

        # Test nur als Beispiel

    def show_input_dialog_active(self, name):
        text, ok = QInputDialog.getText(None, "Active measurement", 'Start active measurement with following file?: ',
                                        text=name)
        if ok: self.start_active_measurement(text)

    def highlight_row(self, name: str):
        row_id: int = 0
        for row in self.rows:
            if row.displayable.name == name:
                self.selectRow(row_id)
                break
            row_id = row_id + 1

    def toggle_all_rows(self):
        for row in self.rows:
            if not self.all_selected and not row.is_child:
                row.checkbox.setChecked(True)
            else:
                row.checkbox.setChecked(False)
        self.all_selected = not self.all_selected

    def sort_table(self, column: int):
        self.sortItems(column, order=2)
        for row_index in range(self.rowCount()):
            if self.item(row_index, 1):
                current = self.item(row_index, 1).data(Qt.UserRole)
                for row in self.rows:
                    if current == row.displayable.name:
                        self.rows.remove(row)
                        self.rows.insert(row_index, row)
                        break
