from multiprocessing import Queue
import sys
from PyQt5.QtWidgets import QApplication

from src.fetcher.file_fetcher.FileLoader import FileLoader
from src.model.Model import Model
from src.view.GUI.MainWindow import MainWindow
from src.view.GUI.UserInteraction.Displayable import Displayable
from src.view.AppRequestsInterface import AppRequestsInterface


def prepare_gui(app: AppRequestsInterface, path_queue: Queue, active_mode_queue: Queue, error_queue: Queue) -> MainWindow:
    q_application = QApplication(sys.argv)
    main_window = MainWindow(q_application, app, path_queue, active_mode_queue, error_queue)
    return main_window
