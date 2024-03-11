from multiprocessing import Queue
from threading import Event, Thread, Lock
from multiprocessing.synchronize import Event as SyncEvent

from colorama import Fore

from src.fetcher.hierarchy_fetcher.HierarchyFetcher import HierarchyFetcher


class HierarchyThread:
    def __init__(self, shutdown_event: Event, data_fetcher: HierarchyFetcher, error_queue: Queue, work_queue: Queue,
                 hierarchy_fetching_event: SyncEvent):

        self.__thread: Thread
        self.__shutdown = shutdown_event
        self.__data_fetcher = data_fetcher
        self.__work_queue = work_queue
        self.__error_queue = error_queue
        self.__current_work: str = ""
        self.__hierarchy_fetching_event = hierarchy_fetching_event

    def __run(self):
        repeat: bool = False
        while not self.__shutdown.is_set():
            if (not self.__work_queue.empty()) or repeat:
                try:
                    if self.__current_work == "":
                        self.__current_work = self.__work_queue.get()

                    if not self.__hierarchy_fetching_event.is_set():
                        self.__data_fetcher.set_semaphore(self.__current_work)
                        print("[HierarchyThread]    work deleted: " + self.__current_work)
                        self.__current_work = ""
                        repeat = False
                        continue
                    print(self.__current_work)
                    self.__data_fetcher.project_name = self.__current_work
                    repeat = self.__data_fetcher.update_project()
                    if repeat:
                        continue
                except FileNotFoundError as e:
                    self.__error_queue.put(FileNotFoundError("could not find the compile-commands.json file"))
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
        self.__data_fetcher.__del__()
        self.__thread.join()
        print("[HierarchyThread]  stopped")
