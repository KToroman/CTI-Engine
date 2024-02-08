import sys
from PyQt5.QtWidgets import QApplication

from src.fetcher.file_fetcher.FileLoader import FileLoader
from src.model.Model import Model
from src.view.GUI.MainWindow import MainWindow
from src.view.GUI.UserInteraction.Displayable import Displayable


def prepare_gui() -> MainWindow:
    q_application = QApplication(sys.argv)
    main_window = MainWindow(q_application)
    q_application.exec()
    return main_window
