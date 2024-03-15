import os
import time
from os.path import join
from threading import Thread
from typing import List, Optional
from multiprocessing.synchronize import Event as SyncEvent
from multiprocessing.synchronize import Lock as SyncLock

import psutil
from psutil import NoSuchProcess

from src.fetcher.process_fetcher.process_observer.metrics_observer.DataObserver import DataObserver
from src.model.Model import Model
from src.model.core.DataEntry import DataEntry
from src.model.core.ProcessPoint import ProcessPoint


class PassiveDataCollectionThread:
    def __init__(self, process_list: List[psutil.Process], process_list_lock: SyncLock, model: Model, model_lock: SyncLock,
                 data_observer: DataObserver, process_count, shutdown: SyncEvent, active_event: SyncEvent):
        self.__thread: Thread
        self._shutdown = shutdown
        self.__process_list = process_list
        self.__process_list_lock = process_list_lock
        self.__model = model
        self.__model_lock = model_lock
        self.__is_full: bool = False
        self.__current_processes: List[psutil.Process] = list()
        self.__data_observer = data_observer
        self.__process_count = process_count
        self.__active_event = active_event

        self.time_till_false: float = 0

    def _run(self):
        while self.__active_event.is_set() and (not self._shutdown.is_set()):
            for process in self.__current_processes:
                try:
                    if process.is_running():
                        self.__make_entry(self.__data_observer.observe(process))
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

        self.__current_processes.clear()
        with self.__process_list_lock:
            self.__process_list.clear()

    def add_work(self, process: psutil.Process):
        if len(self.__current_processes) < self.__process_count:
            self.__current_processes.append(process)
            if len(self.__current_processes) >= self.__process_count:
                self.__is_full = True
            else:
                self.__is_full = False

    def start(self):
        print("[FetcherThread]    started")
        self.__thread = Thread(target=self._run)
        self.__thread.start()

    def stop(self):
        self.__thread.join()
        print("[FetcherThread]  stopped")

    def has_work(self) -> bool:
        return self.__is_full

    def __add_data_entry(self, data_entry: DataEntry):
        time.sleep(0.01)
        with self.__model_lock:
            self.__model.insert_datapoint(data_entry)
            self.time_till_false = time.time() + 35

    def __make_entry(self, process_point: ProcessPoint) -> None:
        try:
            cmdline: List[str] = process_point.process.cmdline()
            path: str = process_point.process.cwd()
            if os.getcwd().split("/")[-1] in path:
                return
            has_o: bool = False
            for line in cmdline:
                if line.endswith(".o"):
                    path = join(path, "CMakeFiles",
                                line.split("CMakeFiles/")[-1])
                    has_o = True
                    break
            if not has_o:
                return
            entry: DataEntry = DataEntry(
                path, process_point.timestamp, process_point.metrics)
            self.__add_data_entry(entry)
        except NoSuchProcess:
            return
        except FileNotFoundError:
            return
        except PermissionError:
            return
