from multiprocessing import Queue
from multiprocessing.synchronize import Event as SyncEvent
from threading import Lock
from typing import List

from PyQt5.QtCore import pyqtSignal


class ProjectFinishedSemaphore:

    def __init__(self, project_dir: str, project_name: str, project_queue: Queue, visualize_event: pyqtSignal,
                 project_finished_event: SyncEvent, semaphore_list: List):
        self.__visualize_event = visualize_event
        self.set_lock: Lock = Lock()
        self.project_dir = project_dir
        self.project_name = project_name
        self.__project_queue = project_queue
        self.__project_finished_event = project_finished_event
        self.__semaphore: int = 0
        self.__passive_been_set: bool = False
        self.__semaphore_list = semaphore_list

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

    def __semaphore_check(self):
        if self.__semaphore == 0:
            self.__semaphore_list.remove(self)

            self.__project_queue.put(self.project_name)
            print(Fore.GREEN + "project finished " + self.project_name + Fore.RESET)
            self.__visualize_event.emit()
            self.__project_finished_event.set()
