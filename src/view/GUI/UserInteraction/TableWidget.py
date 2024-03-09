from typing import List

from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QTableWidget, QTableWidgetItem, QInputDialog, QWidget, QHBoxLayout, QCheckBox

from src.view.GUI.Graph.Plot import Plot
from src.view.GUI.UserInteraction.Displayable import Displayable
from src.view.GUI.UserInteraction.TableRow import TableRow
from src.view.AppRequestsInterface import AppRequestsInterface


class TableWidget(QTableWidget):
    NUMBER_OF_COLUMNS = 4
    COLUMN_1_LABEL = "Name"
    COLUMN_2_LABEL = "Peak RAM(MB)"
    COLUMN_3_LABEL = "Peak CPU (%)"
    COLUMN_4_LABEL = "Runtime"

    def __init__(self, active_mode_queue):
        super().__init__()

        self.active_mode_queue = active_mode_queue
        self.setColumnCount(self.NUMBER_OF_COLUMNS)
        self.rows: List[TableRow] = []
        self.setHorizontalHeaderLabels([self.COLUMN_1_LABEL, self.COLUMN_2_LABEL,
                                        self.COLUMN_3_LABEL, self.COLUMN_4_LABEL])
        self.setStyleSheet("::section{Background-color: #4095a1}")
        self.horizontalHeader().setStyleSheet("::section{Background-color: #4095a1}")
        self.verticalHeader().setStyleSheet("::section{Background-color: #4095a1}")
        self.horizontalHeader().sectionClicked.connect(lambda column: self.sort_table(column - 1))
        self.insertion_point: str = ""
        self.active_started: bool = False
        self.all_selected: bool = False

    def insert_values(self, displayable: Displayable):
        row_pos: int = self.rowCount()
        self.insertRow(row_pos)

        row: TableRow = TableRow(displayable)
        self.rows.append(row)
        self.fill_row(row, row_pos)

        for header in displayable.headers:
            plot_mock: Plot = Plot("", "", [], [0])
            displayable_mock: Displayable = Displayable(header, plot_mock, plot_mock, plot_mock, 0, 0, [], [])
            last_caller_row: TableRow = self.add_subrow(row, displayable_mock)
            for subheader in displayable.secondary_headers[displayable.headers.index(header)]:
                displayable_mock_2: Displayable = Displayable(subheader, plot_mock, plot_mock, plot_mock, 0, 0, [], [])
                self.add_subrow(last_caller_row, displayable_mock_2)

    def rebuild_table(self, row_list: List[TableRow]):
        self.clear()
        self.setHorizontalHeaderLabels([self.COLUMN_1_LABEL, self.COLUMN_2_LABEL,
                                        self.COLUMN_3_LABEL, self.COLUMN_4_LABEL])
        for new_row in row_list:
            if new_row.displayable.name.endswith(".o"):
                self.format_subrows(new_row, row_list.index(new_row), QColor(255, 255, 255), False)
                for subrow in new_row.children:
                    self.format_subrows(subrow, row_list.index(subrow), QColor(220, 220, 220), True)
                    for subsubrow in subrow.children:
                        self.format_subrows(subsubrow, row_list.index(subsubrow), QColor(170, 170, 170), True)

    def format_subrows(self, row: TableRow, row_index: int, color: QColor, hidden: bool):

        self.setRowHeight(row_index, 65)
        self.fill_row(row, row_index)
        self.set_row_color(row_index, color)
        self.setRowHidden(row_index, hidden)

    def add_subrow(self, caller_row: TableRow, displayable: Displayable) -> TableRow:
        caller_row: TableRow = caller_row
        sub_row: TableRow = TableRow(displayable)
        sub_row.checkbox.setDisabled(True)
        caller_row.children.append(sub_row)
        self.rows.insert(self.rows.index(caller_row) + 1, sub_row)
        self.insertRow(self.rowCount())
        return sub_row

    def set_row_color(self, row, color):
        for column in range(self.columnCount()):
            item = self.item(row, column)
            item.setBackground(color)

    def fill_row(self, row, index):
        cell_contents = [row.checkbox, row.name_button, row.toggle_button]
        for widget in cell_contents:
            if widget == row.checkbox:
                continue
            try:
                widget.disconnect()
            except TypeError:
                pass
        row.toggle_button.clicked.connect(lambda: self.toggle_row_vis(row))
        row.name_button.clicked.connect(lambda: self.show_input_dialog_active(row.displayable.name))
        if len(row.children) != 0:
            row.toggle_button.setText("v")
        else:
            row.toggle_button.setText("")
        cell_widget = QWidget()
        layout = QHBoxLayout(cell_widget)
        for item in cell_contents:
            layout.addWidget(item)
        cell_items = [self.setCellWidget(index, 0, cell_widget), str(round(row.displayable.ram_peak, 4)),
                      str(round(row.displayable.cpu_peak, 4)), str(round(row.displayable.runtime_plot.y_values[0], 4))]
        counter: int = 0
        for item in cell_items:
            self.setItem(index, counter, QTableWidgetItem(item))
            counter += 1

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
        self.active_mode_queue.put(name)

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
        """Selects or deselects checkboxes of all rows."""
        for row in self.rows:
            if row.displayable.ram_plot.name != "":
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
        real_lower_limit = min(lower_limit, upper_limit)
        real_upper_limit = max(lower_limit, upper_limit)
        row_index = 1
        for row in self.rows:
            if row.displayable.ram_plot.name != "":
                if real_lower_limit <= row_index <= real_upper_limit:
                    try:
                        row.checkbox.setChecked(True)
                    except RuntimeError as e:
                        pass
                else:
                    try:
                        row.checkbox.setChecked(False)
                    except RuntimeError as r:
                        pass
                row_index += 1

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

