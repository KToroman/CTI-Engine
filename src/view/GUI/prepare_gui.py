from multiprocessing import Queue
import sys
from PyQt5.QtWidgets import QApplication

from src.fetcher.file_fetcher.FileLoader import FileLoader
from src.model.Model import Model
from src.view.GUI.MainWindow import MainWindow
from src.view.GUI.UserInteraction.Displayable import Displayable
from src.view.AppRequestsInterface import AppRequestsInterface


def prepare_gui(visualize_signal, status_queue, status_signal, model_queue, error_queue, error_signal,
                 load_path_queue, active_mode_queue, cancel_event, restart_event) -> MainWindow:
    q_application = QApplication(sys.argv)
    main_window = MainWindow(q_application=q_application, visualize_signal=visualize_signal, model_queue=model_queue,
                             status_signal=status_signal, status_queue=status_queue, restart_event=restart_event,
                             error_signal=error_signal, error_queue=error_queue, load_path_queue=load_path_queue,
                             active_mode_queue=active_mode_queue, cancel_event=cancel_event)
    return main_window
