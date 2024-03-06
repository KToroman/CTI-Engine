from PyQt5.QtCore import QThread

from threading import Event as TEvent
from src.model.Model import Model
#from src.view.GUI.MainWindow import MainWindow

class AppUpdatesThread(QThread):
    
    def __init__(self, main_window, visualize_signal, visualize_lock):
        super().__init__()
        self.__main_window = main_window
        self.shutdown_event = TEvent()
        self.visualize_signal = visualize_signal
        self.visualize_lock = visualize_lock


    def run(self):
        while not self.shutdown_event.is_set():
            if self.__main_window.visualize_event.is_set():                
                if self.__main_window.model_queue.empty():
                  raise BaseException("no model to visualize")

                self.visualize_lock.acquire()
                #self.__main_window.visualize_signal.emit()
                self.visualize_lock.release()
                #TODO what happens if timeout runs out -> model = None
                if self.__main_window.model_queue.empty():
                    self.__main_window.visualize_event.clear()
            if not self.__main_window.status_queue.empty():
                self.__main_window.update_statusbar(self.__main_window.status_queue.get(True, 1.0))
            if not self.__main_window.error_queue.empty():
                self.__main_window.deploy_error(self.__main_window.error_queue.get(True, 1.0))

    
