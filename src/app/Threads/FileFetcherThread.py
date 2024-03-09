from multiprocessing import Queue
from threading import Event, Thread, Lock
from typing import List

from colorama import Fore

from src.fetcher.file_fetcher.FileLoader import FileLoader
from src.model.Model import Model


class FileFetcherThread:
    def __init__(self, error_queue: Queue, model: Model, model_lock: Lock, shutdown: Event, work_queue: Queue):
        self.__thread: Thread
        self.__shutdown = shutdown
        self.__work_queue = work_queue
        self.__error_queue = error_queue
        self.__model = model
        self.__model_lock = model_lock

    def __run(self):
        while not self.__shutdown.is_set():
            work: str
            if not self.__work_queue.empty():
                work = self.__work_queue.get()
            else:
                continue
            try:
                file_loader = FileLoader(work, self.__model, self.__model_lock)
                file_loader.update_project()
            except FileNotFoundError:
                print(Fore.RED + "No file found for path: " + Fore.BLUE + work + Fore.RESET)

    def start(self):
        print("[FileFetcherThread]    started")
        self.__thread = Thread(target=self.__run)
        self.__thread.start()

    def stop(self):
        self.__thread.join()
        print("[FileFetcherThread]  stopped")
