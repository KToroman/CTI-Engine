from typing import List

from PyQt5.QtWidgets import QTableWidget, QTableWidgetItem

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

    def add_row(self, row: TableRow):
        row_position: int = self.rowCount()
        self.insertRow(row_position)

        self.setItem(row_position, 0, QTableWidgetItem(
            self.setCellWidget(row_position, 0, row.custom_cell)))
        self.setItem(row_position, 1, QTableWidgetItem(
            str(row.displayable.ram_peak)))
        self.setItem(row_position, 2, QTableWidgetItem(
            str(row.displayable.cpu_peak)))
        self.setItem(row_position, 3, QTableWidgetItem(
            str(row.displayable.runtime)))
