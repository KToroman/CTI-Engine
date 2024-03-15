from copy import copy, deepcopy
from multiprocessing import Queue, Lock
from threading import Thread
from multiprocessing.synchronize import Lock as SyncLock

from typing import List
from multiprocessing.synchronize import Event as SyncEvent


from src.model.Model import Model
from src.saving.SaveInterface import SaveInterface


class FileSaverThread:
    """Manages the thread which saves projects from model"""

    def __init__(self, shutdown_event: SyncEvent, model: Model, data_fetcher: SaveInterface, model_lock: SyncLock,
                 finished_project: SyncEvent, work_queue: Queue):
        self.__thread: Thread
        self.__shutdown = shutdown_event
        self.__data_fetcher = data_fetcher

        self.__work_queue = work_queue

        self.__finished_project = finished_project

        self.__work_list: List[str] = list()  # TODO endless capacity not very clean for work queues
        self.__work_list_lock: SyncLock = Lock()

        self.__model = model
        self.__model_lock = model_lock

    def __run(self):
        """is the methode which runs the saving thread"""
        index_counter = 0
        while not self.__shutdown.is_set():
            if not self.__work_queue.empty():
                project = self.__work_queue.get()
            else:
                continue
            self.__data_fetcher.save_project(project=project)

    def add_work(self, project_name: str):
        """this methode adds a project to the worklist for the saver thread"""
        with self.__work_list_lock:
            self.__work_list.append(project_name)

    def __remove_work(self):
        if self.__finished_project.is_set():
            self.__finished_project.clear()
            with self.__work_list_lock:
                work = self.__work_list.pop(0)
            print("[FileSaverThread]    work deleted: " + work)

    def __get_work(self, index: int):
        with self.__work_list_lock:
            if self.__work_list:
                return self.__work_list[index % len(self.__work_list)]
            return "none"

    def start(self):
        """this method start the saver thread"""
        print("[FileSaverThread]    started")
        self.__thread = Thread(target=self.__run)
        self.__thread.start()

    def stop(self):
        self.__thread.join()
