from PyQt5.QtCore import QObject

from threading import Event as TEvent
from src.model.Model import Model
#from src.view.GUI.MainWindow import MainWindow

class AppUpdatesWorker(QObject):
    
    def __init__(self, main_window):
        super().__init__()
        self.__main_window = main_window
        self.shutdown_event = TEvent()

    def start(self):
        while not self.shutdown_event.is_set():
            if self.__main_window.visualize_event.is_set():
                if self.__main_window.model_queue.empty():
                    raise BaseException("no model to visualize")
                model: Model = self.__main_window.model_queue.get(True, 1.0)
                self.__main_window.visualize(model)
                #TODO what happens if timeout runs out -> model = None
                if self.__main_window.model_queue.empty():
                    self.__main_window.visualize_event.clear()
            if not self.__main_window.status_queue.empty():
                self.__main_window.update_statusbar(self.__main_window.status_queue.get(True, 1.0))
            if not self.__main_window.error_queue.empty():
                self.__main_window.deploy_error(self.__main_window.error_queue.get(True, 1.0))

    
