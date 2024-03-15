from multiprocessing import Queue
from typing import List

from PyQt5.QtCore import QThreadPool, Qt
from PyQt5.QtWidgets import QInputDialog, QWidget, QHBoxLayout, QHeaderView, QTreeWidget, QLineEdit

from src.view.GUI.Graph.Plot import Plot
from src.view.GUI.UserInteraction.Displayable import Displayable
from src.view.GUI.UserInteraction.ItemWrapper import ItemWrapper
from src.view.GUI.UserInteraction.TableRow import TableRow


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
        self.header().setStyleSheet("::section{Background-color: #4095a1}")
        self.insertion_point: str = ""
        self.active_started: bool = False
        self.all_selected: bool = False
        self.in_row_loop: bool = False

        self.thread_pool: QThreadPool = QThreadPool.globalInstance()

        self.header().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.displayed_project: str = ""
        self.setSortingEnabled(True)
        self.sortByColumn(0, Qt.AscendingOrder)

    def insert_values(self, displayables: List[Displayable]):
        """insert values for the given data points, that are being saved in displayable objects"""
        for displayable in displayables:
            item: ItemWrapper = ItemWrapper(displayable.name, self)
            self.__create_row(item, displayable)
            for header in displayable.headers:
                sub_item = ItemWrapper(header, item)
                self.fill_subrow(sub_item, header)
                for subheader in displayable.secondary_headers[displayable.headers.index(header)]:
                    subsub_item = ItemWrapper(subheader, sub_item)
                    self.fill_subrow(subsub_item, subheader)

    def __create_row(self, item: ItemWrapper, displayable: Displayable):
        """configures the row that will be displayed in the table"""
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
        self.rows.append(row)
        item.set_row(row)
        self.items.append(item)

    def fill_subrow(self, item, name):
        plot_mock: Plot = Plot("", "", [], [0])
        displayable_mock = Displayable(name, plot_mock, plot_mock, plot_mock, 0, 0, [], [])
        self.__create_row(item, displayable_mock)
        item.row.checkbox.setDisabled(True)

    def add_active_data(self, displayable: Displayable):
        for item in self.items:
            if item.name == self.insertion_point:
                for i in range(item.childCount()):
                    if displayable.name == item.child(i).name:
                        values = [displayable.ram_peak, displayable.cpu_peak, displayable.runtime_plot.y_values[0]]
                        item.child(i).setData(1, 0, round((values[0]), 4))
                        item.child(i).setData(2, 0, round((values[1]), 4))
                        item.child(i).setData(3, 0, round((values[2]), 4))
                        item.child(i).row.checkbox.setDisabled(False)
                    for j in range(item.child(i).childCount()):
                        if displayable.name == item.child(i).child(j).name:
                            values = [displayable.ram_peak, displayable.cpu_peak, displayable.runtime_plot.y_values[0]]
                            item.child(i).child(j).setData(1, 0, round((values[0]), 4))
                            item.child(i).child(j).setData(2, 0, round((values[1]), 4))
                            item.child(i).child(j).setData(3, 0, round((values[2]), 4))
                            item.child(i).child(j).row.checkbox.setDisabled(False)

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
                break

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

