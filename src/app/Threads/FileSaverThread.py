from copy import copy, deepcopy
from multiprocessing import Queue, Lock
from threading import Thread
from multiprocessing.synchronize import Lock as SyncLock
import time

from typing import List, Optional
from multiprocessing.synchronize import Event as SyncEvent

from click import Option

from src.model.DataBaseEntry import DataBaseEntry
from src.model.Model import Model
from src.saving.SaveInterface import SaveInterface


class FileSaverThread:
    """Manages the thread which saves projects from model"""

    def __init__(
        self,
        shutdown_event: SyncEvent,
        model: Model,
        saver: SaveInterface,
        model_lock: SyncLock,
        finished_project: SyncEvent,
        work_queue: "Queue[str]",
    ) -> None:
        self.__thread: Thread
        self.__shutdown = shutdown_event
        self.__saver: SaveInterface = saver

        self.__work_queue = work_queue

        self.__finished_project = finished_project

        self.__work_list: List[str] = (
            list()
        )  # TODO endless capacity not very clean for work queues

        self.__model = model
        self.__model_lock = model_lock

    def __run(self) -> None:
        work_list_index: int = 0
        """is the methode which runs the saving thread"""
        while not self.__shutdown.is_set():
            if not self.__work_queue.empty():
                self.__work_list.append(self.__work_queue.get())
            work = self.__get_work(work_list_index)
            if work is None:
                continue
            work_list_index += 1
            self.__remove_work()
            project = self.__model.get_project_by_name(work)
            self.__saver.save_project(project)
            time.sleep(10)

    def add_work(self, project_name: str) -> None:
        """this methode adds a project to the worklist for the saver thread"""

        self.__work_list.append(project_name)

    def __remove_work(self) -> None:
        if self.__finished_project.is_set():
            self.__finished_project.clear()
            work = self.__work_list.pop(0)

    def __get_work(self, index: int) -> Optional[str]:
        if self.__work_list:
            return self.__work_list[index % len(self.__work_list)]
        return None

    def start(self) -> None:
        """this method start the saver thread"""
        self.__thread = Thread(target=self.__run)
        self.__thread.start()

    def stop(self) -> None:
        self.__thread.join()
