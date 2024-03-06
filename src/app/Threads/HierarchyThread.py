from multiprocessing import Queue
from threading import Event, Thread
from typing import List, Optional

from colorama import Fore

from src.fetcher.hierarchy_fetcher.HierarchyFetcher import HierarchyFetcher


class HierarchyThread:
    def __init__(self, data_fetcher: HierarchyFetcher, error_queue: Queue):
        self.thread: Thread = None
        self.shutdown: Event = Event()
        self.shutdown.clear()
        self.data_fetcher = data_fetcher
        self.work_queue: List[str] = list()
        self.error_queue = error_queue
        self.is_done: str = ""

    def collect_data(self):
        repeat: bool = False
        while not self.shutdown.is_set():
            if self.work_queue or repeat:
                try:
                    self.data_fetcher.project_name = self.work_queue[0]
                    repeat = self.data_fetcher.update_project()
                except FileNotFoundError:
                    # self.error_queue.put(FileNotFoundError("could not find the compile-commands.json file"))
                    print(Fore.RED + "[HierarchyThread]   could not find the compile-commands.json file for project: " +
                          Fore.BLUE + self.work_queue[0] + Fore.RESET)
                    repeat = False
                if self.data_fetcher.is_done:
                    self.is_done = self.work_queue.pop(0)
                    print("[HierarchyThread]    work deleted: " + self.is_done)
                    repeat = False

    def is_done_str(self) -> str:
        if self.is_done != "":
            temp_name = self.is_done
            self.is_done = ""
            return temp_name
        return "none"

    def add_work(self, project_name: str):
        print("[HierarchyThread]   work added")
        self.work_queue.append(project_name)

    def start(self):
        print("[HierarchyThread]    started")
        self.thread = Thread(target=self.collect_data)
        self.thread.start()

    def stop(self):
        self.shutdown.set()
        self.thread.join()
        print("[HierarchyThread]  stopped")
