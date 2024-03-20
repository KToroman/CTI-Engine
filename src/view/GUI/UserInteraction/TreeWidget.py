from multiprocessing import Queue
import multiprocessing
import threading
import time
from typing import List

from PyQt5.QtCore import QThreadPool, Qt, QObject, pyqtSignal, QThread
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

    def __init__(self, active_mode_queue: Queue):
        super().__init__()

        self.active_mode_queue = active_mode_queue
        self.setColumnCount(self.NUMBER_OF_COLUMNS)
        self.rows: List[TableRow] = []
        self.items: List[ItemWrapper] = []
        self.setHeaderLabels([self.COLUMN_1_LABEL, self.COLUMN_2_LABEL,
                              self.COLUMN_3_LABEL, self.COLUMN_4_LABEL])
        #self.header().setStyleSheet("::section{background-color: #292c43; }")
        #self.header().setStyleSheet("::section{background-color: #23868B; color: black}")

        self.insertion_point: str = ""
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

    def insert_values(self, displayables: List[DisplayableHolder]):
        print(len(displayables))
        for displayable in displayables:
            self.insert_data(displayable, self)

    def insert_data(self, displayable_holder: DisplayableHolder, parent):
        if len(displayable_holder.get_sub_disp()) > 0:
            print(f"[TreeWidget]     length: {len(displayable_holder.get_sub_disp())}")
        if not displayable_holder.get_sub_disp():
            item = ItemWrapper(displayable_holder.displayable.name, parent)
            self.create_row(item, displayable_holder.displayable)
            return
        item = ItemWrapper(displayable_holder.displayable.name, parent)
        self.create_row(item, displayable_holder.displayable)
        for h in displayable_holder.get_sub_disp():
            self.insert_data(h, item)

    def create_row(self, item: ItemWrapper, displayable: Displayable):
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
            item.setBackground(0, QColor().red())
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
        """entry point for an active measurement."""
        self.active_started = True
        self.insertion_point: str = name
        self.active_mode_queue.put((name))

    def __show_input_dialog_active(self, name):
        """shows an input window, where the user can see and edit the path for the active measurement"""
        text, ok = QInputDialog.getText(None, "Active measurement", 'Start active measurement with following file?: ',
                                        text=name)
        if ok: self.start_active_measurement(text)

    def highlight_row(self, name: str):
        """select the row for the given input string to highlight it in the table"""
        for row in self.rows:
            if row.displayable.name == name:
                self.setCurrentItem(self.items[self.rows.index(row)])
                self.scrollToItem(self.currentItem())
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

    def search_item(self, line_edit: QLineEdit):
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
                parent = item.parent()
                while parent:
                    self.expandItem(parent)
                    parent = parent.parent()


class TreeWidgetWrapper(QObject):
    visualiseSignal = pyqtSignal()
    finished = pyqtSignal()

    def __init__(self, active_mode_queue: Queue, input_queue: Queue, return_queue):
        super().__init__()
        self.tree_widget = TreeWidget(active_mode_queue)
        self.return_queue = return_queue
        self.input_queue: Queue[list[DisplayableHolder]] = input_queue
        self.visualiseSignal.connect(self.visualise)

    def visualise(self):
        print(f"running on {str(QThread.currentThread())}")
        displayables = self.input_queue.get()
        self.tree_widget.insert_values(displayables)
        self.return_queue.put(self.tree_widget)
        self.finished.emit()


QTHREAD = QThread()


def get_new_tree_widget(active_mode_queue: Queue, displayables: list[DisplayableHolder], return_queue, callback):
    global QTHREAD
    print(f"QTHREAD: {str(QTHREAD)}; MAINTHREAD: {str(QApplication.instance().thread())}")
    print(f"outer runing on {str(QThread.currentThread())}")
    input_queue: Queue[list[DisplayableHolder]] = Queue()
    tree_widget_wrapper = TreeWidgetWrapper(active_mode_queue, input_queue, return_queue)
    input_queue.put(displayables)
    tree_widget_wrapper.moveToThread(QTHREAD)
    tree_widget_wrapper.finished.connect(callback)
    QTHREAD.start()
    tree_widget_wrapper.visualiseSignal.emit()
