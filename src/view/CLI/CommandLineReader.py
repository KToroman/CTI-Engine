import sys

import click
from PyQt5.QtWidgets import QApplication

from src.view.GUI.MainWindow import MainWindow
from src.view.UIInterface import UIInterface


def prepare_gui() -> MainWindow:
    q_application = QApplication(sys.argv)
    return MainWindow(q_application)

if __name__ == '__main__':
    gui = prepare_gui()
    sys.exit(gui.close())