from multiprocessing import Queue
from threading import Event, Thread
from typing import List, Optional

from colorama import Fore

from src.fetcher.hierarchy_fetcher.HierarchyFetcher import HierarchyFetcher


class HierarchyThread:
    def __init__(self, shutdown_event: Event, data_fetcher: HierarchyFetcher, error_queue: Queue):
        self.thread: Thread
        self.shutdown = shutdown_event
        self.data_fetcher = data_fetcher
        self.work_queue: List[str] = list()
        self.error_queue = error_queue
        self.is_done = False

    def collect_data(self):
        repeat: bool = False
        while not self.shutdown.is_set():
            if self.work_queue or repeat:
                try:
                    self.data_fetcher.project_name = self.work_queue[0]
                    repeat = self.data_fetcher.update_project()
                except FileNotFoundError:
                    #self.error_queue.put(FileNotFoundError("could not find the compile-commands.json file"))
                    print(Fore.RED + "[HierarchyThread]   could not find the compile-commands.json file for project" +
                          self.work_queue[0] + Fore.RESET)
                    repeat = False
                    self.is_done = True

                if self.data_fetcher.is_done:
                    self.work_queue.pop(0)
                    if not self.work_queue:
                        self.is_done = True
                        repeat = False

    def is_done_bool(self) -> bool:
        if self.is_done:
            self.is_done = False
            return True
        return False

    def add_work(self, project_name: str):
        print("[HierarchyThread]   work added")
        self.work_queue.append(project_name)

    def start(self):
        print("[HierarchyThread]    started")
        self.thread = Thread(target=self.collect_data)
        self.thread.start()

    def join(self):
        self.thread.join()
        print("[HierarchyThread]  stopped")
