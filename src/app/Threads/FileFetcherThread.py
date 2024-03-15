from multiprocessing import Queue, Lock
from threading import Thread
from multiprocessing.synchronize import Event as SyncEvent
from multiprocessing.synchronize import Lock as SyncLock

from PyQt5.QtCore import pyqtSignal
from src.fetcher.file_fetcher.FileLoader import FileLoader
from src.model.Model import Model


class FileFetcherThread:
    def __init__(self, error_queue: Queue, model: Model, model_lock: SyncLock, shutdown: SyncEvent, load_path_queue: Queue,
                 load_event: SyncEvent, project_queue: Queue, visualize_event: pyqtSignal):
        self.__thread: Thread
        self.__shutdown = shutdown
        self.__work_queue = load_path_queue
        self.__error_queue = error_queue
        self.__model = model
        self.__model_lock = model_lock
        self.__load_event = load_event

        self.__project_queue = project_queue
        self.__visualize_event = visualize_event

    def __run(self):
        while not self.__shutdown.is_set():
            work: str
            if not self.__work_queue.empty():
                self.__load_event.set()
                work = self.__work_queue.get()
            else:
                continue
            try:
                file_loader = FileLoader(work, self.__model, self.__model_lock, self.__visualize_event,
                                         self.__project_queue)
                file_loader.update_project()
            except FileNotFoundError as e:
                self.__error_queue.put(e)
                print("[FlieFetcherThread]   No file found for path: " )
            self.__load_event.clear()


    def start(self):
        print("[FileFetcherThread]    started")
        self.__thread = Thread(target=self.__run)
        self.__thread.start()

    def stop(self):
        self.__thread.join()
        print("[FileFetcherThread]  stopped")
