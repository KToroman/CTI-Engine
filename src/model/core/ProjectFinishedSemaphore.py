from multiprocessing import Queue
from multiprocessing.synchronize import Event as SyncEvent
from multiprocessing.synchronize import Lock as SyncLock

from multiprocessing import Lock
from typing import List

from PyQt5.QtCore import pyqtSignal


class ProjectFinishedSemaphore:

    def __init__(self, project_dir: str, project_name: str, project_queue: "Queue[str]", visualize_event: pyqtSignal,
                 project_finished_event: SyncEvent, semaphore_list: List["ProjectFinishedSemaphore"]):
        self.__visualize_event = visualize_event
        self.set_lock: SyncLock = Lock()
        self.project_dir: str = project_dir
        self.project_name: str = project_name
        self.__project_queue: "Queue[str]" = project_queue
        self.__project_finished_event = project_finished_event
        self.__semaphore: int = 0
        self.__passive_been_set: bool = False
        self.__semaphore_list = semaphore_list

    def new_project_set(self) -> None:
        if self.__semaphore > -1:
            self.__semaphore -= 1
            self.__semaphore_check()

    def stop_fetcher_set(self) -> None:
        if self.__semaphore > -1:
            self.__semaphore -= 1
            self.__passive_been_set = True
            self.__semaphore_check()

    def hierarchy_fetcher_set(self) -> None:
        if self.__semaphore < 1:
            self.__semaphore += 1
            self.__semaphore_check()

    def __semaphore_check(self) -> None:
        if self.__semaphore == 0:
            self.__semaphore_list.remove(self)
            print("[PROJECT]    Project finished " + self.project_name)
            self.__project_queue.put(self.project_name)
            self.__visualize_event.emit()  # type: ignore[attr-defined]
            self.__project_finished_event.set()
