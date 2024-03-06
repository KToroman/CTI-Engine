from copy import copy, deepcopy
from multiprocessing import Queue
from threading import Event, Thread, Lock
from typing import List

from src.model.Model import Model
from src.saving.SaveInterface import SaveInterface


class FileSaverThread:
    """Manages the thread which saves projects from model"""
    def __init__(self, model: Model, data_fetcher: SaveInterface, model_lock: Lock):
        self.thread: Thread = None
        self.shutdown: Event = Event()
        self.shutdown.clear()
        self.data_fetcher = data_fetcher
        self.work_queue: List[str] = list()
        self.__model = model
        self.__model_lock = model_lock

    def collect_data(self):
        """is the methode which runs the saving thread"""
        while not self.shutdown.is_set():
            for work in self.work_queue:
                with self.__model_lock:
                    project = deepcopy(self.__model.get_project_by_name(work))
                self.data_fetcher.save_project(project=project)

    def delete_work(self, work: str):
        """this methode deletes a project form the worklist for the saver thread"""
        if work in self.work_queue:
            self.work_queue.remove(work)
            self.data_fetcher.save_project(self.__model.get_project_by_name(work))
            print("[FileSaverThread]    deleted " + work)

    def add_work(self, project_name: str):
        """this methode adds a project to the worklist for the saver thread"""
        print("[FileSaverThread] work added")
        self.work_queue.append(project_name)

    def start(self):
        """this method start the saver thread"""
        print("[FileSaverThread]    started")
        self.thread = Thread(target=self.collect_data)
        self.thread.start()

    def stop(self):
        """this methode stops the save thread"""
        self.shutdown.set()
        self.thread.join()
        print("[FileSaverThread]  stopped")
