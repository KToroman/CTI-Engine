from typing import Any

from PyQt5.QtCore import QThread
from PyQt5.QtWidgets import QTreeWidgetItem

from src.view.GUI.UserInteraction.TableRow import TableRow


class ItemWrapper(QTreeWidgetItem):

    def __init__(self, name: str, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.name: str = name
        self.row: TableRow

    def set_row(self, row: TableRow) -> None:
        self.row = row
