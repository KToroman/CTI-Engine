from multiprocessing import Queue, Event
from multiprocessing.synchronize import Event as SyncEvent
from PyQt5.QtCore import pyqtSignal

from src.model.core.StatusSettings import StatusSettings
from src.view.UIInterface import UIInterface
from src.view.GUI.MainWindowMeta import MainWindowMeta
from PyQt5.QtWidgets import QWidget, QApplication


class CommandLineUI(QWidget, UIInterface, metaclass=MainWindowMeta):

    visualize_signal = pyqtSignal()
    status_signal = pyqtSignal()
    error_signal = pyqtSignal()

    def __init__(self, qapp: QApplication, error_queue: "Queue[BaseException]", shutdown_event: SyncEvent):
        self.qapp: QApplication = qapp
        self.__error_queue: "Queue[BaseException]" = error_queue
        self.shutdown_event: SyncEvent = shutdown_event
        self.project_queue: "Queue[str]" = Queue()
        self.status_queue: "Queue[StatusSettings]" = Queue()
        super().__init__()

    def deploy_error(self) -> None:
        if not self.__error_queue.empty():
            error = (self.__error_queue.get())
            print("[ERROR] " + str(error))

    def update_statusbar(self) -> None:
        pass

    def execute(self) -> None:
        while not self.shutdown_event.is_set():
            if not self.__error_queue.empty():
                self.deploy_error()
