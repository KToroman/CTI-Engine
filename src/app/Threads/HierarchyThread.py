from multiprocessing import Queue
from threading import Event, Thread, Lock
from typing import List, Optional

from colorama import Fore

from src.fetcher.hierarchy_fetcher.HierarchyFetcher import HierarchyFetcher


class HierarchyThread:
    def __init__(self, shutdown_event: Event, data_fetcher: HierarchyFetcher, error_queue: Queue, work_queue: Queue):

        self.__thread: Thread
        self.__shutdown = shutdown_event
        self.__data_fetcher = data_fetcher
        self.__work_queue = work_queue
        self.__error_queue = error_queue
        self.__current_work: str = ""

    def __run(self):
        repeat: bool = False
        while not self.__shutdown.is_set():
            if (not self.__work_queue.empty()) or repeat:
                try:
                    if self.__current_work == "":
                        self.__current_work = self.__work_queue.get()

                    self.__data_fetcher.project_name = self.__current_work
                    repeat = self.__data_fetcher.update_project()
                    if repeat:
                        continue
                except FileNotFoundError:
                    # self.error_queue.put(FileNotFoundError("could not find the compile-commands.json file"))
                    print(Fore.RED + "[HierarchyThread]   could not find the compile-commands.json file for project: " +
                          Fore.BLUE + self.__current_work + Fore.RESET)
                    repeat = False

                print("[HierarchyThread]    work deleted: " + self.__current_work)
                self.__current_work = ""
                repeat = False

    def start(self):
        print("[HierarchyThread]    started")
        self.__thread = Thread(target=self.__run)
        self.__thread.start()

    def stop(self):
        self.thread.join()
        print("[HierarchyThread]  stopped")
