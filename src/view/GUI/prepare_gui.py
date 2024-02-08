import sys
from PyQt5.QtWidgets import QApplication

from src.fetcher.file_fetcher.FileLoader import FileLoader
from src.model.Model import Model
from src.view.GUI.MainWindow import MainWindow
from src.view.GUI.UserInteraction.Displayable import Displayable


def prepare_gui() -> MainWindow:
    q_application = QApplication(sys.argv)
    main_window = MainWindow(q_application)
    model = Model()
    file_loader = FileLoader("/common/homes/students/uvhuj_heusinger/Documents/git/cti-engine-prototype/saves/CTI_ENGINE_SAVE simox 2024-02-07", model)
    file_loader.update_project()
    print('loaded')
    main_window.visualize(model)
    return main_window

prepare_gui()
