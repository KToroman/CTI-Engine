from copy import copy, deepcopy
from multiprocessing import Queue
from threading import Event, Thread, Lock
from typing import List

from src.model.Model import Model
from src.saving.SaveInterface import SaveInterface


class FileSaverThread:
    """Manages the thread which saves projects from model"""

    def __init__(self, shutdown_event: Event, model: Model, data_fetcher: SaveInterface, model_lock: Lock, is_fetching_passive: Event):
        self.__thread: Thread
        self.__shutdown = shutdown_event
        self.__data_fetcher = data_fetcher

        self.__work_queue: List[str] = list() # TODO endless capacity not very clean for work queues
        self.__work_queue_lock: Lock = Lock()

        self.__model = model
        self.__model_lock = model_lock

        self.__is_fetching_passive = is_fetching_passive

        self.__delete_list: List[str] = list()
        self.__delete_list_lock: Lock = Lock()

        self.__finished: str = ""
        self.__finished_lock: Lock = Lock()

    def __run(self):
        """is the methode which runs the saving thread"""
        index_counter = 0
        while not self.__shutdown.is_set():
            work = self.__get_work(index_counter)
            if work == "none":
                continue
            index_counter += 1
            self.__remove_work(work)
            with self.__model_lock:
                project = deepcopy(self.__model.get_project_by_name(work))
            self.__data_fetcher.save_project(project=project)

    def delete_work(self, work: str):
        if work != "none":
            with self.__delete_list_lock:
                self.__delete_list.append(work)

    def add_work(self, project_name: str):
        """this methode adds a project to the worklist for the saver thread"""
        with self.__work_queue_lock:
            self.__work_queue.append(project_name)

    def finished_project(self) -> str:
        if self.__finished != "":
            temp = self.__finished
            self.__finished = ""
            return temp
        return "none"

    def __get_curr_model_dir(self, project_dir: str) -> bool:
        with self.__model_lock:
            if project_dir == self.__model.get_current_working_directory():
                return True
            return False

    def __remove_work(self, work: str):
        with self.__delete_list_lock:
            if work in self.__delete_list and (not self.__get_curr_model_dir(work) or
                                               not self.__is_fetching_passive.is_set()):
                with self.__work_queue_lock:
                    self.__work_queue.remove(work)
                with self.__finished_lock:
                    self.__finished = work
                print("[FileSaverThread]    work deleted: " + work)

    def __get_work(self, index: int):
        with self.__work_queue_lock:
            if self.__work_queue:
                return self.__work_queue[index % len(self.__work_queue)]
            return "none"

    def start(self):
        """this method start the saver thread"""
        print("[FileSaverThread]    started")
        self.__thread = Thread(target=self.__run)
        self.__thread.start()

    def join(self):
        self.thread.join()
