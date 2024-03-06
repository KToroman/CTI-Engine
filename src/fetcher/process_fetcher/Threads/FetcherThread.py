import os
import time
from multiprocessing import Queue
from os.path import join
from threading import Event, Thread, Lock
from typing import List

import psutil
from psutil import NoSuchProcess

from src.fetcher.hierarchy_fetcher.HierarchyFetcher import HierarchyFetcher
from src.fetcher.process_fetcher.process_observer.metrics_observer.DataObserver import DataObserver
from src.model.Model import Model
from src.model.core.DataEntry import DataEntry
from src.model.core.ProcessPoint import ProcessPoint


class FetcherThread:
    def __init__(self, process_list: List[psutil.Process], process_list_lock: Lock, model: Model, model_lock: Lock,
                 data_observer: DataObserver, process_count):
        self.thread: Thread = None
        self.shutdown: Event = Event()
        self.shutdown.clear()
        self.__process_list = process_list
        self.__process_list_lock = process_list_lock
        self.__model = model
        self.__model_lock = model_lock
        self.__is_full: bool = False
        self.__current_processes: List[psutil.Process] = list()
        self.__data_observer = data_observer
        self.process_count = process_count

    def collect_data(self):
        while not self.shutdown.is_set():
            for process in self.__current_processes:
                try:
                    if process.is_running():
                        self.__make_entry(self.fetch_metrics(process))
                        time.sleep(0.001)
                    else:
                        with self.__process_list_lock:
                            self.__process_list.remove(process)
                        self.__current_processes.remove(process)
                        self.__is_full = False
                except NoSuchProcess:
                    with self.__process_list_lock:
                        self.__process_list.remove(process)
                    self.__current_processes.remove(process)
                    self.__is_full = False
                    continue

    def add_work(self, process: psutil.Process):
        if len(self.__current_processes) < self.process_count:
            self.__current_processes.append(process)
            if len(self.__current_processes) >= self.process_count:
                self.__is_full = True
            else:
                self.__is_full = False

    def start(self):
        print("[FetcherThread]    started")
        self.thread = Thread(target=self.collect_data)
        self.thread.start()

    def stop(self):
        self.shutdown.set()
        self.thread.join()
        print("[FetcherThread]  stopped")

    def has_work(self) -> bool:
        return self.__is_full

    def add_data_entry(self, data_entry: DataEntry):
        with self.__model_lock:
            self.__model.insert_datapoint(data_entry)

    def __make_entry(self, process_point: ProcessPoint) -> None:
        try:
            cmdline: List[str] = process_point.process.cmdline()
            path: str = process_point.process.cwd()
            if os.getcwd().split("/")[-1] in path:
                return
            has_o: bool = False
            for line in cmdline:
                if line.endswith(".o"):
                    path = join(path, "CMakeFiles", line.split("CMakeFiles/")[-1])
                    has_o = True
                    break
            if not has_o:
                return
            entry: DataEntry = DataEntry(path, process_point.timestamp, process_point.metrics)
            self.add_data_entry(entry)
        except NoSuchProcess:
            return
        except FileNotFoundError:
            return
        except PermissionError:
            return

    def fetch_metrics(self, process: psutil.Process) -> ProcessPoint:
        return self.__data_observer.observe(process)
