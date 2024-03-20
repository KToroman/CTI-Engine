from PyQt5.QtWidgets import QMainWindow
from src.view.UIInterface import UIInterface


class MainWindowMeta(type(QMainWindow), type(UIInterface)): # type: ignore[misc]
    pass
