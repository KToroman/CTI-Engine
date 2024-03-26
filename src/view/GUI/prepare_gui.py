from multiprocessing import Queue
import sys
from multiprocessing.synchronize import Event as SyncEvent


from PyQt5.QtWidgets import QApplication

from src.model.Model import Model
from src.model.core.StatusSettings import StatusSettings
from src.view.GUI.MainWindow import MainWindow
from src.view.UIInterface import UIInterface


def prepare_gui(shutdown_event: SyncEvent, status_queue: "Queue[StatusSettings]",
                project_queue: "Queue[str]", error_queue: "Queue[BaseException]",
                load_path_queue: "Queue[str]", active_mode_queue: "Queue[str]", cancel_event: SyncEvent,
                restart_event: SyncEvent, model: Model) -> UIInterface:
    q_application = QApplication(sys.argv)
    main_window = MainWindow(q_application=q_application, project_queue=project_queue,
                             status_queue=status_queue, restart_event=restart_event,
                             error_queue=error_queue, load_path_queue=load_path_queue,
                             active_mode_queue=active_mode_queue, cancel_event=cancel_event,
                             shutdown_event=shutdown_event, model=model)
    return main_window
