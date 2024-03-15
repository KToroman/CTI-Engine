from PyQt5.QtWidgets import QTreeWidgetItem


class ItemWrapper(QTreeWidgetItem):

    def __init__(self, name: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name: str = name
