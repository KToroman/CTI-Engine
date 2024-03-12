import os.path
import threading
import time
from multiprocessing import Queue
from os.path import join
from threading import Lock, Thread, Event
from typing import List
from multiprocessing.synchronize import Event as SyncEvent

import psutil
from PyQt5.QtCore import pyqtSignal

from src.fetcher.process_fetcher.DataFetcher import DataFetcher
from src.fetcher.process_fetcher.Threads.FetcherThread import FetcherThread
from src.fetcher.process_fetcher.Threads.ProcessCollectorThread import ProcessCollectorThread
from src.fetcher.process_fetcher.Threads.ProcessFindingThread import ProcessFindingThread

from src.fetcher.process_fetcher.process_observer.metrics_observer.DataObserver import DataObserver
from src.model.Model import Model


class PassiveDataFetcher(DataFetcher):

    def __init__(self, model: Model, model_lock: Lock, saver_queue: Queue, hierarchy_queue: Queue,
                 shutdown: Event, save_path: str, project_queue: Queue, finished_event: pyqtSignal,
                 project_finished_event: SyncEvent, passive_mode_event: SyncEvent, process_finder_count=2,
                 process_collector_count=2, fetcher_count=2, fetcher_process_count=15):

        self.__model = model
        self.__model_lock = model_lock
        self.__shutdown = shutdown

        self.__passive_mode_event = passive_mode_event
        self.__project_queue = project_queue
        self.__finished_event = finished_event
        self.__project_finished_event = project_finished_event

        self.__save_path = save_path

        self.__time_till_false_lock: Lock = Lock()

        self.__saver_queue = saver_queue
        self.__hierarchy_queue = hierarchy_queue

        self.__process_finder: List[ProcessFindingThread] = list()
        self.__process_finder_count = process_finder_count

        self.__process_collector_list: List[ProcessCollectorThread] = list()
        self.__process_collector_count = process_collector_count

        self.__fetcher_count: int = fetcher_count
        self.__fetcher_process_count = fetcher_process_count
        self.__fetcher: List[FetcherThread] = list()
        self.__done_fetching: bool = True
        self.max_time = 0

    def update_project(self) -> bool:
        for finder in self.__process_finder:
            finder.set_work()
        time_keeper_bool: bool = self.__time_keeper()
        if time_keeper_bool:
            self.__done_fetching = False
        else:
            if not self.__done_fetching:
                self.finish_fetching()
        return time_keeper_bool

    def finish_fetching(self):
        if not self.__done_fetching:
            self.__done_fetching = True
            self.__semaphore()

    def __semaphore(self):
        with self.__model_lock:
            if self.__model.current_project is not None:
                with self.__model.get_semaphore_by_name(self.__model.get_current_working_directory()).set_lock:
                    self.__model.get_semaphore_by_name(self.__model.get_current_working_directory()).stop_fetcher_set()

    def __time_keeper(self) -> bool:
        if self.__get_time_till_false() < time.time():
            return False
        return True

    def __get_time_till_false(self) -> float:
        max_time: float = 0
        process_time: float = 0
        fetcher_time: float = 0
        for p in self.__process_collector_list:
            if max_time < p.time_till_false:
                process_time = p.time_till_false
        for f in self.__fetcher:
            if max_time < f.time_till_false:
                fetcher_time = f.time_till_false
        max_time = max(process_time, fetcher_time)
        return max_time

    def start(self):
        print("[PassiveDataFetcher]    sending start signal")
        process_list: List[psutil.Process] = list()
        process_list_lock: threading.Lock = threading.Lock()
        # self.__data_fetching_thread.start()
        for i in range(self.__fetcher_count):
            fetcher = FetcherThread(process_list, process_list_lock, self.__model, self.__model_lock,
                                    DataObserver(), self.__fetcher_process_count, self.__shutdown,
                                    self.__passive_mode_event)
            self.__fetcher.append(fetcher)
            fetcher.start()
        for i in range(self.__process_collector_count):
            process_collector_thread = ProcessCollectorThread(process_list, process_list_lock, self.__model,
                                                              self.__model_lock,
                                                              True, self.__fetcher, self.__saver_queue,
                                                              self.__hierarchy_queue,
                                                              self.__save_path, self.__shutdown, self.__project_queue,
                                                              self.__finished_event, self.__project_finished_event,
                                                              self.__passive_mode_event)
            self.__process_collector_list.append(process_collector_thread)
            process_collector_thread.start()
        for i in range(self.__process_finder_count):
            finder = ProcessFindingThread(self.__process_collector_list, self.__shutdown, self.__passive_mode_event)
            self.__process_finder.append(finder)
            finder.start()

    def stop(self):
        print("[PassiveDataFetcher]  stop signal sent...")
        for finder in self.__process_finder:
            finder.stop()
        for collector in self.__process_collector_list:
            collector.stop()
        for f in self.__fetcher:
            f.stop()
        print("[PassiveDataFetcher]  stopped all threads")
