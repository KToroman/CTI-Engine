from multiprocessing import Queue
from threading import Event, Thread, Lock
from typing import List, Optional

from colorama import Fore

from src.fetcher.hierarchy_fetcher.HierarchyFetcher import HierarchyFetcher


class HierarchyThread:
    def __init__(self, shutdown_event: Event, data_fetcher: HierarchyFetcher, error_queue: Queue):
        self.__thread: Thread
        self.__shutdown = shutdown_event
        self.__data_fetcher = data_fetcher
        self.__work_queue_lock: Lock = Lock()
        self.__work_queue: List[str] = list()

        self.__error_queue = error_queue
        self.__is_done: str = ""

    def __run(self):
        repeat: bool = False
        while not self.__shutdown.is_set():
            if self.__work_queue or repeat:
                try:
                    with self.__work_queue_lock:
                        self.__data_fetcher.project_name = self.__work_queue[0]
                    repeat = self.__data_fetcher.update_project()
                except FileNotFoundError:

                    # self.error_queue.put(FileNotFoundError("could not find the compile-commands.json file"))
                    print(Fore.RED + "[HierarchyThread]   could not find the compile-commands.json file for project: " +
                          Fore.BLUE + self.__work_queue[0] + Fore.RESET)
                    repeat = False
                if self.__data_fetcher.is_done:
                    with self.__work_queue_lock:
                        self.__is_done = self.__work_queue.pop(0)
                    print("[HierarchyThread]    work deleted: " + self.__is_done)
                    repeat = False

    def get_finished_project(self) -> str:
        if self.__is_done != "":
            temp_name = self.__is_done
            self.__is_done = ""
            return temp_name
        return "none"

    def add_work(self, project_name: str):
        with self.__work_queue_lock:
            self.__work_queue.append(project_name)

    def start(self):
        print("[HierarchyThread]    started")
        self.__thread = Thread(target=self.__run)
        self.__thread.start()

    def join(self):
        self.thread.join()
        print("[HierarchyThread]  stopped")
