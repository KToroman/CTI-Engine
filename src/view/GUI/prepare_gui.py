from multiprocessing import Queue
import sys
from PyQt5.QtWidgets import QApplication

from src.fetcher.file_fetcher.FileLoader import FileLoader
from src.model.Model import Model
from src.view.GUI.MainWindow import MainWindow
from src.view.GUI.UserInteraction.Displayable import Displayable
from src.view.AppRequestsInterface import AppRequestsInterface


def prepare_gui(app: AppRequestsInterface, visualize_event, status_queue, model_queue, error_queue) -> MainWindow:
    q_application = QApplication(sys.argv)
    main_window = MainWindow(q_application=q_application, app=app, visualize_event=visualize_event, status_queue=status_queue, model_queue=model_queue, error_queue=error_queue)
    return main_window
