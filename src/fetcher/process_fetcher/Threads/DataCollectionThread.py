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


class DataCollectionThread:
    def __init__(self, process_list: List[psutil.Process], process_list_lock: SyncLock, model: Model, model_lock: SyncLock,
                 data_observer: DataObserver, process_count, shutdown: SyncEvent, active_event: SyncEvent):
        self._thread: Thread
        self._shutdown = shutdown
        self._process_list = process_list
        self._process_list_lock = process_list_lock
        self._model = model
        self._model_lock = model_lock
        self._is_full: bool = False
        self._current_processes: List[psutil.Process] = list()
        self._data_observer = data_observer
        self._process_count = process_count
        self._active_event = active_event

        self.time_till_false: float = 0

    def _run(self):
        while not self._shutdown.is_set():
            for process in self._current_processes:

                if not self._active_event.is_set():
                    self._current_processes.clear()
                    with self._process_list_lock:
                        self._process_list.clear()
                    continue

                try:
                    if process.is_running():
                        self._make_entry(self._data_observer.observe(process))
                        time.sleep(0.001)
                    else:
                        with self._process_list_lock:
                            self._process_list.remove(process)
                        self._current_processes.remove(process)
                        self._is_full = False
                except NoSuchProcess:
                    with self._process_list_lock:
                        self._process_list.remove(process)
                    self._current_processes.remove(process)
                    self._is_full = False
                    continue

    def add_work(self, process: psutil.Process):
        if len(self._current_processes) < self._process_count:
            self._current_processes.append(process)
            if len(self._current_processes) >= self._process_count:
                self._is_full = True
            else:
                self._is_full = False

    def start(self):
        print("[FetcherThread]    started")
        self._thread = Thread(target=self._run)
        self._thread.start()

    def stop(self):
        self._thread.join()
        print("[FetcherThread]  stopped")

    def has_work(self) -> bool:
        return self._is_full

    def _add_data_entry(self, data_entry: DataEntry):
        with self._model_lock:
            self._model.insert_datapoint(data_entry)
        self.time_till_false = time.time() + 20

    def _make_entry(self, process_point: ProcessPoint) -> None:
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
            self._add_data_entry(entry)
        except NoSuchProcess:
            return
        except FileNotFoundError:
            return
        except PermissionError:
            return
