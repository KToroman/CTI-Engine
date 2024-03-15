from PyQt5.QtWidgets import QTreeWidgetItem

from src.view.GUI.UserInteraction.TableRow import TableRow


class ItemWrapper(QTreeWidgetItem):

    def __init__(self, name: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name: str = name
        self.row: TableRow

    def set_row(self, row: TableRow):
        self.row = row

    def setStyleSheet(self, style: str):
        print("[itemWrapper]   should make red")
        self.setStyleSheet(style)



