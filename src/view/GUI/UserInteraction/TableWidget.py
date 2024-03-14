import time
from multiprocessing import Queue
from typing import List
import time

from PyQt5.QtCore import QThreadPool, pyqtSignal
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QTableWidget, QTableWidgetItem, QInputDialog, QWidget, QHBoxLayout, QHeaderView, \
    QTreeWidget, QTreeWidgetItem

from src.view.GUI.Graph.Plot import Plot
from src.view.GUI.UserInteraction.Displayable import Displayable
from src.view.GUI.UserInteraction.TableRow import TableRow


class TableWidget(QTableWidget):
    NUMBER_OF_COLUMNS = 4
    COLUMN_1_LABEL = "Name"
    COLUMN_2_LABEL = "Peak RAM(MB)"
    COLUMN_3_LABEL = "Peak CPU (%)"
    COLUMN_4_LABEL = "Runtime"

    def __init__(self, active_mode_queue: Queue):
        super().__init__()

        self.active_mode_queue = active_mode_queue
        self.setColumnCount(self.NUMBER_OF_COLUMNS)
        self.rows: List[TableRow] = []
        self.setHeaderLabels([self.COLUMN_1_LABEL, self.COLUMN_2_LABEL,
                                        self.COLUMN_3_LABEL, self.COLUMN_4_LABEL])
        self.setStyleSheet("::section{Background-color: #4095a1}")
        #self.horizontalHeader().setStyleSheet("::section{Background-color: #4095a1}")
        #self.verticalHeader().setStyleSheet("::section{Background-color: #4095a1}")
        # self.horizontalHeader().sectionClicked.connect(lambda column: self.sort_table(column - 1))
        self.insertion_point: str = ""
        self.insertion_row: TableRow
        self.active_started: bool = False
        self.all_selected: bool = False
        self.in_row_loop: bool = False

        self.thread_pool: QThreadPool = QThreadPool.globalInstance()

        #self.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.setMaximumWidth(550)
        self.displayed_project: str = ""
        self.setSortingEnabled(True)


    def toggle_all_rows(self):
        """Selects or deselects checkboxes of all rows."""
        last_checkbox: int = self.__find_last_checkbox()
        row_count: int = 1
        self.in_row_loop = True
        for row in self.rows:
            if row.displayable.ram_plot.name != "":
                if row_count == last_checkbox:
                    self.in_row_loop = False
                row_count += 1
                if not self.all_selected:
                    try:
                        row.checkbox.setChecked(True)
                    except RuntimeError as e:
                        pass
                else:
                    try:
                        row.checkbox.setChecked(False)
                    except RuntimeError as r:
                        pass
        self.all_selected = not self.all_selected

    def toggle_custom_amount(self, lower_limit: int, upper_limit: int):
        """Receives two limits and selects checkboxes of rows inbetween them."""
        real_lower_limit: int = min(lower_limit, upper_limit)
        real_upper_limit: int = max(lower_limit, upper_limit)
        last_checkbox: int = self.__find_last_checkbox()
        if real_upper_limit > last_checkbox:
            real_upper_limit = last_checkbox
        row_count: int = 1
        self.in_row_loop = True
        for row in self.rows:
            if row.displayable.ram_plot.name != "":
                if real_lower_limit <= row_count <= real_upper_limit:
                    if row_count == real_upper_limit:
                        self.in_row_loop = False
                    try:
                        row.checkbox.setChecked(False)
                        row.checkbox.setChecked(True)
                    except RuntimeError as e:
                        pass
                    self.in_row_loop = True
                else:
                    if row_count == last_checkbox:
                        self.in_row_loop = False
                    try:
                        row.checkbox.setChecked(False)
                    except RuntimeError as r:
                        pass
                row_count += 1
        self.in_row_loop = False

    def __find_last_checkbox(self) -> int:
        last_checkbox: int = 0
        for row in self.rows:
            if row.displayable.ram_plot.name != "":
                try:
                    row.checkbox.isWidgetType()
                    last_checkbox += 1
                except RuntimeError as e:
                    pass
        return last_checkbox

    def sort_table(self, column: int):
        """Sorts table according to a given parameter."""
        out_list = []
        key_list = [lambda obj: obj.displayable.ram_peak, lambda obj: obj.displayable.cpu_peak, lambda obj:
        obj.displayable.runtime_plot.y_values[0]]
        sorted_objects = sorted(self.rows, key=key_list[column], reverse=True)
        for row in sorted_objects:
            if row.displayable.name.endswith(".o"):
                out_list.append(row)
                for subrow in row.children:
                    out_list.append(subrow)
                    for subsubrow in subrow.children:
                        out_list.append(subsubrow)
        self.rows = out_list
        self.rebuild_table(self.rows)

    def clear_table(self):
        self.clear()
        self.rows.clear()
        self.setRowCount(0)
