import sys
from PyQt5.QtWidgets import QApplication

from src.fetcher.file_fetcher.FileLoader import FileLoader
from src.model.Model import Model
from src.model.core.Header import Header
from src.view.GUI.MainWindow import MainWindow
from src.view.GUI.UserInteraction.Displayable import Displayable


def prepare_gui() -> MainWindow:
    q_application = QApplication(sys.argv)
    main_window = MainWindow(q_application)
    model = Model()
    file_loader = FileLoader("/common/homes/students/uvhuj_heusinger/Documents/git/cti-engine-prototype/saves/CTI_ENGINE_SAVE bullet3 2024-02-08", model)
    file_loader.update_project()
    h = Header("MARIE STINKT")
    h.headers.append(Header("Caspar nicht :)"))
    print('loaded')
    main_window.visualize(model)
    q_application.exec()
    return main_window

prepare_gui()
