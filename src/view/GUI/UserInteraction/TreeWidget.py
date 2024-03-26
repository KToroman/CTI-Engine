import typing
from multiprocessing import Queue
import multiprocessing
import threading
import time
from typing import List

from PyQt5.QtCore import QThreadPool, Qt, QObject, pyqtSignal, QThread, QPoint
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QInputDialog, QWidget, QHBoxLayout, QHeaderView, QTreeWidget, QLineEdit, QApplication

from src.view.GUI.Graph.Plot import Plot
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

    graph_signal: pyqtSignal = pyqtSignal()
    deselect_signal: pyqtSignal = pyqtSignal()

    def __init__(self, active_mode_queue: "Queue[str]", error_queue: "Queue[BaseException]",
                 error_signale: pyqtSignal) -> None:
        super().__init__()

        self.active_mode_queue: "Queue[str]" = active_mode_queue
        self.setColumnCount(self.NUMBER_OF_COLUMNS)
        self.rows: List[TableRow] = []
        self.items: List[ItemWrapper] = []
        self.setHeaderLabels([self.COLUMN_1_LABEL, self.COLUMN_2_LABEL,
                              self.COLUMN_3_LABEL, self.COLUMN_4_LABEL])
        # self.header().setStyleSheet("::section{background-color: #292c43; }")
        # self.header().setStyleSheet("::section{background-color: #23868B; color: black}")

        self.insertion_point: List[str] = []
        self.active_started: bool = False
        self.all_selected: bool = False
        self.in_row_loop: bool = False
        self.error_queue = error_queue
        self.error_signal = error_signale

        self.__shutdown: SyncEvent = multiprocessing.Event()

        self.thread_pool: QThreadPool = QThreadPool.globalInstance()

        self.header().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.displayed_project: str = ""
        self.setSortingEnabled(True)
        self.sortByColumn(0, Qt.DescendingOrder)
        self.table_list: List[QTreeWidget] = list()
        self.row_count: int = 1
        self.last_checkbox: int = 0
        self.run_count: int = 0
        self.project_name: str = ""
        self.status: str = ""

    def insert_values(self, displayables: List[DisplayableHolder]) -> None:
        for displayable in displayables:
            self.insert_data(displayable, self)

    def insert_data(self, displayable_holder: DisplayableHolder, parent: typing.Any) -> None:
        if not displayable_holder.get_sub_disp():
            item = ItemWrapper(displayable_holder.displayable.name, parent)
            self.create_row(item, displayable_holder.displayable)
            return
        item = ItemWrapper(displayable_holder.displayable.name, parent)
        self.create_row(item, displayable_holder.displayable)
        for h in displayable_holder.get_sub_disp():
            self.insert_data(typing.cast(DisplayableHolder, h), item)

    def create_row(self, item: ItemWrapper, displayable: Displayable) -> None:
        row = TableRow(displayable)
        cell_widget = QWidget()
        layout = QHBoxLayout(cell_widget)
        layout.addWidget(row.checkbox)
        layout.addWidget(row.name_button)
        self.setItemWidget(item, 0, cell_widget)
        values = [displayable.ram_peak, displayable.cpu_peak, displayable.runtime_plot.y_values[0]]
        item.setData(1, 0, round((values[0]), 4))
        item.setData(2, 0, round((values[1]), 4))
        item.setData(3, 0, round((values[2]), 4))
        row.name_button.clicked.connect(lambda: self.__show_input_dialog_active(row.displayable.name))
        item.set_row(row)
        if values[2] == 0:
            item.row.checkbox.setDisabled(True)
        if displayable.failed:
            row.name_button.setStyleSheet("background-color:  #7F1717")
        self.items.append(item)
        self.rows.append(row)

    def add_active_data(self, displayable: DisplayableHolder) -> None:
        for item in self.items:
            if item.row.displayable.parent_list.__len__() != displayable.displayable.parent_list.__len__():
                continue
            if displayable.displayable.name != item.row.displayable.name:
                continue
            equal: bool = True
            for i in range(item.row.displayable.parent_list.__len__()):
                if item.row.displayable.parent_list[i] != displayable.displayable.parent_list[i]:
                    equal = False
            if equal:
                item.row.displayable = displayable.displayable
                values = [displayable.displayable.ram_peak, displayable.displayable.cpu_peak,
                          displayable.displayable.runtime_plot.y_values[0]]
                item.setData(1, 0, round((values[0]), 4))
                item.setData(2, 0, round((values[1]), 4))
                item.setData(3, 0, round((values[2]), 4))
                if values[2] == 0:
                    item.row.checkbox.setDisabled(True)  # type: ignore[attr-defined]
                else:
                    item.row.checkbox.setDisabled(False)  # type: ignore[attr-defined]
                item.row.connected = False  # type: ignore[attr-defined]
                if displayable.displayable.failed:
                    item.row.name_button.setStyleSheet("background-color:  #7F1717")
                    return

    def start_active_measurement(self, name: str) -> None:
        """entry point for an active measurement."""
        if self.status == "measuring" or self.status == "making file hierarchy":
            self.error_queue.put(BaseException("Can not start active measurement while fetching a project. " +
                                               "Please cancel the fetching or wait till project is finished!"))
            self.error_signal.emit()
            return

        self.active_started = True
        self.insertion_point.append(name)
        self.active_mode_queue.put(name)

    def __show_input_dialog_active(self, name: str) -> None:
        """shows an input window, where the user can see and edit the path for the active measurement"""
        text, ok = QInputDialog.getText(None, "Active measurement", 'Start active measurement with following file?: ',
                                        # type: ignore[arg-type]
                                        text=name)
        if ok: self.start_active_measurement(text)

    def highlight_row(self, name: str) -> None:
        """select the row for the given input string to highlight it in the table"""
        for item in self.items:
            if item.row.displayable.parent_list.__len__() != (name.split("#").__len__() - 1):
                continue
            if item.row.displayable.name != name.split("#")[0]:
                continue
            equal: bool = True
            for i in range(item.row.displayable.parent_list.__len__()):
                if item.row.displayable.parent_list[i] != name.split("#")[i+1]:
                    equal = False
            if equal:
                self.setCurrentItem(item)
                self.scrollToItem(self.currentItem())
                break

    def toggle_all_rows(self) -> None:
        """Selects or deselects checkboxes of all rows."""
        self.__find_last_checkbox()
        self.row_count: int = 1
        self.in_row_loop = True
        for item in self.items:
            if item.row.displayable.runtime_plot.y_values[0] != 0:
                if not self.all_selected:
                    item.row.checkbox.setChecked(True)
                else:
                    item.row.checkbox.setChecked(False)
        self.all_selected = not self.all_selected
        self.in_row_loop = False
        self.graph_signal.emit()

    def toggle_custom_amount(self, lower_limit: int, upper_limit: int) -> None:
        """Receives two limits and selects checkboxes of rows inbetween them."""
        self.deselect_signal.emit()
        self.run_count += 1
        if self.run_count <= 2:
            return
        self.run_count = 0
        self.all_selected = False
        real_lower_limit: int = min(lower_limit, upper_limit)
        real_upper_limit: int = max(lower_limit, upper_limit)
        # self.toggle_all_rows()
        self.row_count = 1
        self.__find_last_checkbox()
        if real_upper_limit > self.last_checkbox:
            real_upper_limit = self.last_checkbox
        self.in_row_loop = True
        for i in range(self.topLevelItemCount()):
            item = self.topLevelItem(i)
            if item.row.displayable.runtime_plot.y_values[0] != 0:
                if real_lower_limit <= self.row_count <= real_upper_limit:
                    item.row.checkbox.setChecked(True)
                else:
                    item.row.checkbox.setChecked(False)
                self.row_count += 1
            self.__select_subs(real_lower_limit, real_upper_limit, item)
        self.in_row_loop = False
        self.graph_signal.emit()

    def __select_subs(self, lower_limit: int, upper_limit: int, parent):
        for i in range(parent.childCount()):
            item = parent.child(i)
            if item.row.displayable.runtime_plot.y_values[0] != 0:
                if lower_limit <= self.row_count <= upper_limit:
                    item.row.checkbox.setChecked(True)
                else:
                    item.row.checkbox.setChecked(False)
                self.row_count += 1
            self.__select_subs(lower_limit, upper_limit, item)

    def __find_last_checkbox(self) -> None:
        self.last_checkbox: int = 0
        for i in range(self.topLevelItemCount()):
            item = self.topLevelItem(i)
            if item.row.displayable.runtime_plot.y_values[0] != 0:
                try:
                    #item.row.checkbox.isEnabled()
                    self.last_checkbox += 1
                    self.__get_sub_count(item)
                except RuntimeError as e:
                    pass

    def __get_sub_count(self, parent):
        for i in range(parent.childCount()):
            item = parent.child(i)
            if item.row.displayable.runtime_plot.y_values[0] != 0:
                try:
                    #item.row.checkbox.isEnabled()
                    self.last_checkbox += 1
                    self.__get_sub_count(item)
                except RuntimeError as e:
                    pass




    def search_item(self, line_edit: QLineEdit) -> None:
        """searches the table for a user input in order to select and highlight the found items"""
        search_text = line_edit.text().strip()
        if search_text:
            self.clearSelection()
            items = []
            for text in self.items:
                if search_text in text.row.name_button.text():
                    items.append(text)
            # highlight found items and expand them if they are subrows
            for item in items:
                item.setSelected(True)
                self.scrollToItem(item)
                parent = item.parent()
                while parent:
                    self.expandItem(parent)
                    parent = parent.parent()

