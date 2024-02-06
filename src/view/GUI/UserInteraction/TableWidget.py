from typing import List

from PyQt5.QtWidgets import QTableWidget, QTableWidgetItem, QInputDialog, QWidget, QHBoxLayout

#from src.view.AppRequestsInterface import AppRequestsInterface
from src.view.GUI.UserInteraction.Displayable import Displayable
from src.view.GUI.UserInteraction.TableRow import TableRow


class TableWidget(QTableWidget):
    NUMBER_OF_COLUMNS = 4
    COLUMN_1_LABEL = "Name"
    COLUMN_2_LABEL = "Peak RAM(%)"
    COLUMN_3_LABEL = "Peak CPU (MB)"
    COLUMN_4_LABEL = "Runtime"

    def __init__(self):
        super().__init__()
        self.setColumnCount(self.NUMBER_OF_COLUMNS)
        self.rows: List[TableRow] = []
        self.setHorizontalHeaderLabels([self.COLUMN_1_LABEL, self.COLUMN_2_LABEL,
                                        self.COLUMN_3_LABEL, self.COLUMN_4_LABEL])
        self.insertion_point: str = ""
        self.active_started: bool = False
        # self.app_request_interface = AppRequestsInterface()

    def insert_values(self, displayable: Displayable):
        row_pos: int = self.rowCount()
        self.insertRow(row_pos)

        row: TableRow = TableRow(displayable)
        self.rows.append(row)

        self.fill_row(row, row_pos)
        self.setRowHeight(self.rows.index(row), 40)

        row.toggle_button.clicked.connect(lambda: self.toggle_row_vis(row))
        row.name_button.clicked.connect(lambda: self.show_input_dialog_active(row.displayable.name))

    def add_subrow(self, displayable: Displayable):
        for row in self.rows:
            if row.displayable.name == self.insertion_point:
                caller_row: TableRow = row
                sub_row: TableRow = TableRow(displayable)
                caller_row.children.append(sub_row)
                self.rows.insert(self.rows.index(row) + 1, sub_row)
                self.insertRow(self.rowCount())
                sub_row.toggle_button.clicked.connect(lambda: self.toggle_row_vis(sub_row))
                sub_row.name_button.clicked.connect(lambda: self.show_input_dialog_active(sub_row.displayable.name))
                break
        self.clear()
        self.setHorizontalHeaderLabels([self.COLUMN_1_LABEL, self.COLUMN_2_LABEL,
                                        self.COLUMN_3_LABEL, self.COLUMN_4_LABEL])
        for new_row in self.rows:
            self.setRowHeight(self.rows.index(new_row), 40)
            self.fill_row(new_row, self.rows.index(new_row))

    def fill_row(self, row, index):
        if len(row.children) != 0:
            row.toggle_button.setText("^")

        cell_widget = QWidget()
        layout = QHBoxLayout(cell_widget)
        layout.addWidget(row.checkbox)
        layout.addWidget(row.name_button)
        layout.addWidget(row.toggle_button)
        self.setItem(index, 0,
                     QTableWidgetItem(self.setCellWidget(index, 0, cell_widget)))
        self.setItem(index, 1, QTableWidgetItem(str(row.displayable.ram_peak)))
        self.setItem(index, 2, QTableWidgetItem(str(row.displayable.cpu_peak)))
        self.setItem(index, 3, QTableWidgetItem("Dummy"))  # row.displayable.runtime_plot.y_values[0]

    def toggle_row_vis(self, row):
        for subrow in row.children:
            if len(subrow.children) != 0:
                self.hide_rows(subrow)
            pos = self.rows.index(subrow)
            if self.isRowHidden(pos):
                self.setRowHidden(pos, False)
            else:
                self.setRowHidden(pos, True)

        if row.toggle_button.text() == "v":
            row.toggle_button.setText("^")
        elif row.toggle_button.text() == "^":
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
        dis = Displayable("test1", ..., ..., ..., 1, 123, 123)
        dis1 = Displayable("test2", ..., ..., ..., 1, 123, 123)

        if name == "test1":
            self.add_subrow(dis1)
        else:
            self.add_subrow(dis)
        # self.app_request_interface.start_active_measurement(name)

    def show_input_dialog_active(self, name):
        text, ok = QInputDialog.getText(None, "Active measurement", 'Start active measurement with following file?: ',
                                        text=name)
        if ok: self.start_active_measurement(name)
