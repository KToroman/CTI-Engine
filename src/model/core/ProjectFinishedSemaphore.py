from multiprocessing import Queue
from multiprocessing.synchronize import Event as SyncEvent
from threading import Lock

from PyQt5.QtCore import pyqtSignal


class ProjectFinishedSemaphore:

    def __init__(self, project_name: str, project_queue: Queue, visualize_event: pyqtSignal,
                 project_finished_event: SyncEvent):
        self.__visualize_event = visualize_event
        self.set_lock: Lock = Lock()
        self.project_name = project_name
        self.__project_queue = project_queue
        self.__project_finished_event = project_finished_event
        self.__semaphore: int = 0
        self.__passive_been_set: bool = False

    def new_project_set(self):
        if self.__semaphore > -1:
            self.__semaphore -= 1
            self.__semaphore_check()

    def stop_fetcher_set(self):
        if self.__semaphore > -1:
            self.__semaphore -= 1
            self.__passive_been_set = True
            self.__semaphore_check()

    def hierarchy_fetcher_set(self):
        if self.__semaphore < 1:
            self.__semaphore += 1
            self.__semaphore_check()

    def restore_fetcher_set(self):
        if self.__passive_been_set:
            self.__semaphore += 1
            self.__passive_been_set = False

    def __semaphore_check(self):
        if self.__semaphore == 0:
            self.__project_queue.put(self.project_name)
            print("project finished " + self.project_name)
            self.__visualize_event.emit()
            self.__project_finished_event.set()
