import multiprocessing
import threading
import time
from multiprocessing import Queue
from typing import List
import time

from PyQt5.QtCore import pyqtSignal, QModelIndex, Qt, QThread, QThreadPool, QRunnable
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QTableWidget, QTableWidgetItem, QInputDialog, QWidget, QHBoxLayout, QHeaderView, \
    QTreeWidget, QTreeWidgetItem, QCheckBox, QPushButton, QVBoxLayout

from src.view.GUI.Graph.Plot import Plot
from src.view.GUI.Threading.InsertValuesWorker import InsertValuesWorker
from src.view.GUI.UserInteraction.Displayable import Displayable
from src.view.GUI.UserInteraction.DisplayableHolder import DisplayableHolder
from src.view.GUI.UserInteraction.ItemWrapper import ItemWrapper
from src.view.GUI.UserInteraction.TableRow import TableRow
from multiprocessing.synchronize import Event as SyncEvent


class TreeWidget(QTreeWidget):
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
        self.items: List[ItemWrapper] = []
        self.setHeaderLabels([self.COLUMN_1_LABEL, self.COLUMN_2_LABEL,
                              self.COLUMN_3_LABEL, self.COLUMN_4_LABEL])
        self.setStyleSheet("::section{Background-color: #4095a1}")
        self.header().setStyleSheet("::section{Background-color: #4095a1}")
        self.header().setStyleSheet("::section{Background-color: #4095a1}")
        self.insertion_point: str = ""
        self.insertion_row: TableRow
        self.active_started: bool = False
        self.all_selected: bool = False
        self.in_row_loop: bool = False

        self.__shutdown: SyncEvent = multiprocessing.Event()
        self.work_queue: Queue = Queue()

        self.thread_pool: QThreadPool = QThreadPool.globalInstance()

        self.header().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.displayed_project: str = ""
        self.setSortingEnabled(True)
        self.sortByColumn(0, Qt.AscendingOrder)
        self.table_list: List[QTreeWidget] = list()

    class CreateRow(QRunnable):
        def __init__(self, parent, item: ItemWrapper, row: TableRow, cell_widget: QWidget, layout: QHBoxLayout) -> None:
            self.__item: ItemWrapper = item
            self.__row: TableRow = row
            self.__cell_widget: QWidget = cell_widget
            self.__layout: QHBoxLayout = layout
            self.__parent: TreeWidget = parent
            super().__init__()

        def run(self):
            pass
            self.__parent.create_row(self.__item, self.__row.displayable,self.__row ,self.__cell_widget, self.__layout)

    def insert_values(self, displayables: List[DisplayableHolder]):
        print("before inserting values")
        print(len(displayables))
        for displayable in displayables:

            self.insert_data(displayable, self)
        print("after inserting values")

    def insert_data(self, displayable_holder: DisplayableHolder, parent):
        if not displayable_holder.get_sub_disp():

            item = ItemWrapper(displayable_holder.displayable.name, parent)
            row = TableRow(displayable_holder.displayable)
            cell_widget = QWidget()
            layout = QHBoxLayout(cell_widget)
            row.name_button.clicked.connect(lambda: self.show_input_dialog_active(row.displayable.name))

            layout.addWidget(row.checkbox)
            layout.addWidget(row.name_button)
            self.setItemWidget(item, 0, cell_widget)
            self.thread_pool.start(self.CreateRow(self, item, row, cell_widget, layout))


            return
        item = ItemWrapper(displayable_holder.displayable.name, parent)
        row = TableRow(displayable_holder.displayable)
        cell_widget = QWidget()
        layout = QHBoxLayout(cell_widget)
        row.name_button.clicked.connect(lambda: self.show_input_dialog_active(row.displayable.name))


        layout.addWidget(row.checkbox)
        layout.addWidget(row.name_button)
        self.setItemWidget(item, 0, cell_widget)
        self.thread_pool.start(self.CreateRow(self, item, row, cell_widget, layout))


        for h in displayable_holder.get_sub_disp():
            self.insert_data(h, item)

    def create_row(self, item: ItemWrapper, displayable: Displayable, row: TableRow, cell_widget: QWidget, layout: QHBoxLayout):
        print("creating row")
        values = [displayable.ram_peak, displayable.cpu_peak, displayable.runtime_plot.y_values[0]]
        print("check0")
        item.setData(1, 0, round((values[0]), 4))
        item.setData(2, 0, round((values[1]), 4))
        item.setData(3, 0, round((values[2]), 4))
        print("check1")
        item.set_row(row)
        if values[2] == 0:
            item.row.checkbox.setDisabled(True)
        print("check2")
        self.items.append(item)
        self.rows.append(row)

    def add_active_data(self, displayable: DisplayableHolder):
        for item in self.items:
            if item.name == self.insertion_point:
                for i in range(item.childCount()):
                    if displayable.displayable.name == item.child(i).name:
                        values = [displayable.displayable.ram_peak, displayable.displayable.cpu_peak,
                                  displayable.displayable.runtime_plot.y_values[0]]
                        item.child(i).setData(1, 0, round((values[0]), 4))
                        item.child(i).setData(2, 0, round((values[1]), 4))
                        item.child(i).setData(3, 0, round((values[2]), 4))
                        if values[2] != 0:
                            item.child(i).row.checkbox.setDisabled(False)
                            item.child(i).row.connected = False
                        if displayable.displayable.failed:
                            item.setStyleSheet("::section{Background-color: #FF3232}")
                    for j in range(item.child(i).childCount()):
                        if displayable.displayable.name == item.child(i).child(j).name:
                            values = [displayable.displayable.ram_peak, displayable.displayable.cpu_peak,
                                      displayable.displayable.runtime_plot.y_values[0]]
                            item.child(i).child(j).setData(1, 0, round((values[0]), 4))
                            item.child(i).child(j).setData(2, 0, round((values[1]), 4))
                            item.child(i).child(j).setData(3, 0, round((values[2]), 4))
                            if values[2] != 0:
                                item.child(i).child(j).row.checkbox.setDisabled(False)
                                item.child(i).row.connected = False
                            if displayable.displayable.failed:
                                item.setStyleSheet("::section{Background-color: #FF3232}")
        for disp in displayable.get_sub_disp():
            self.add_active_data(disp)

    def start_active_measurement(self, name):
        self.active_started = True
        self.insertion_point: str = name
        self.active_mode_queue.put((name))
        self.active_started = True

    def show_input_dialog_active(self, name):
        text, ok = QInputDialog.getText(None, "Active measurement", 'Start active measurement with following file?: ',
                                        text=name)
        if ok: self.start_active_measurement(text)

    def highlight_row(self, name: str):
        for row in self.rows:
            if row.displayable.name == name:
                self.setCurrentItem(self.items[self.rows.index(row)])
                break

    def toggle_all_rows(self):
        """Selects or deselects checkboxes of all rows."""
        last_checkbox: int = self.__find_last_checkbox()
        row_count: int = 1
        self.in_row_loop = True
        for row in self.rows:
            if row.displayable.runtime_plot.y_values[0] != 0:
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
        if real_upper_limit == real_lower_limit == 0:
            self.toggle_all_rows()
            return
        last_checkbox: int = self.__find_last_checkbox()
        if real_upper_limit > last_checkbox:
            real_upper_limit = last_checkbox
        row_count: int = 1
        self.in_row_loop = True
        for row in self.rows:
            if row.displayable.runtime_plot.y_values[0] != 0:
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
            if row.displayable.runtime_plot.y_values[0] != 0:
                try:
                    row.checkbox.isWidgetType()
                    last_checkbox += 1
                except RuntimeError as e:
                    pass
        return last_checkbox

    def clear_tree(self):
        for row in self.rows:
            row.checkbox.disconnect()
            row.checkbox.deleteLater()
            row.name_button.disconnect()
            row.name_button.deleteLater()
        self.rows.clear()
        self.items.clear()
        self.clear()

    def search_item(self, main_window):
        search_text = main_window.line_edit.text().strip()
        if search_text:
            self.clearSelection()
            items = []
            for text in self.items:
                if search_text in text.row.name_button.text():
                    items.append(text)
            for item in items:
                item.setSelected(True)
                parent = item.parent()
                while parent:
                    self.expandItem(parent)
                    parent = parent.parent()
