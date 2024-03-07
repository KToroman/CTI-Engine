from multiprocessing import Event, Queue
from threading import Thread, Lock
from typing import List

from src.fetcher.file_fetcher.FileLoader import FileLoader
from src.model.Model import Model


class FileFetcherThread:
    def __init__(self, error_queue: Queue, model: Model, model_lock: Lock):
        self.__thread: Thread = None
        self.__shutdown: Event = Event()
        self.__shutdown.clear()
        self.__work_queue: List[str] = list()
        self.__work_queue_lock: Lock = Lock()
        self.__error_queue = error_queue
        self.__model = model
        self.__model_lock = model_lock

    def __run(self):
        while not self.__shutdown.is_set():
            work: str
            with self.__work_queue_lock:
                if self.__work_queue:
                    work = self.__work_queue.pop(0)
                else:
                    continue
            try:
                file_loader = FileLoader(work, self.__model, self.__model_lock)
                file_loader.update_project()
            except FileNotFoundError:
                pass

    def add_work(self, work: str):
        with self.__work_queue_lock:
            self.__work_queue.append(work)

    def start(self):
        print("[FileFetcherThread]    started")
        self.__thread = Thread(target=self.__run)
        self.__thread.start()

    def stop(self):
        self.__shutdown.set()
        self.__thread.join()
        print("[FileFetcherThread]  stopped")
