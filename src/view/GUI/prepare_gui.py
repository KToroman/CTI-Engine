from multiprocessing import Queue
import sys
from threading import Event

from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QApplication

from src.fetcher.file_fetcher.FileLoader import FileLoader
from src.model.Model import Model
from src.view.GUI.MainWindow import MainWindow
from src.view.GUI.UserInteraction.Displayable import Displayable
from src.view.AppRequestsInterface import AppRequestsInterface
from src.view.UIInterface import UIInterface


def prepare_gui(shutdown_event: Event, status_queue: Queue,
                model_queue: Queue, error_queue: Queue, load_path_queue: Queue,
                active_mode_queue: Queue, cancel_event: Event, restart_event: Event) -> UIInterface:
    q_application = QApplication(sys.argv)
    main_window = MainWindow(q_application=q_application, model_queue=model_queue,
                             status_queue=status_queue, restart_event=restart_event,
                             error_queue=error_queue, load_path_queue=load_path_queue,
                             active_mode_queue=active_mode_queue, cancel_event=cancel_event,
                             shutdown_event=shutdown_event)
    return main_window
