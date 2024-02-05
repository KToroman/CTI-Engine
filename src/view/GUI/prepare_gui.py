import sys
from PyQt5.QtWidgets import QApplication

from src.view.GUI.MainWindow import MainWindow

def prepare_gui() -> MainWindow:
    q_application = QApplication(sys.argv)
    main_window = MainWindow(q_application)
    q_application.exec()
    return main_window
