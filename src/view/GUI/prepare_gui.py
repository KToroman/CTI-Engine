import sys
from PyQt5.QtWidgets import QApplication

from src.view.GUI.MainWindow import MainWindow
from src.view.GUI.UserInteraction.Displayable import Displayable


def prepare_gui() -> MainWindow:
    q_application = QApplication(sys.argv)
    main_window = MainWindow(q_application)

    header = ["a", "b", "c"]
    secondary_header = [["d", "e", "f"], ["h", "i", "j"], ["x", "y", "z"]]
    header2 = ["ö", "ü", "ä"]
    secondary_header2 = [["k", "l", "m"], ["n", "o", "p"], ["9", "4", "z"]]
    dis = Displayable("test1", ..., ..., ..., 1, 123, header, secondary_header)
    dis1 = Displayable("test2", ..., ..., ..., 1, 1111, header2, secondary_header2)
    main_window.table_widget.insert_values(dis)
    main_window.table_widget.insert_values(dis1)
    q_application.exec()
    return main_window

prepare_gui()
