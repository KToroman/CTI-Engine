import os.path
import threading
import time
from multiprocessing import Queue
from os.path import join
from threading import Lock, Thread, Event
from typing import List

import psutil


from src.fetcher.process_fetcher.DataFetcher import DataFetcher
from src.fetcher.process_fetcher.Threads.FetcherThread import FetcherThread
from src.fetcher.process_fetcher.Threads.ProcessCollectorThread import ProcessCollectorThread
from src.fetcher.process_fetcher.Threads.ProcessFindingThread import ProcessFindingThread

from src.fetcher.process_fetcher.process_observer.metrics_observer.DataObserver import DataObserver
from src.model.Model import Model


class PassiveDataFetcher(DataFetcher):

    def __init__(self, model: Model, model_lock: Lock, saver_queue: Queue, hierarchy_queue: Queue,
                 shutdown: Event, save_path: str, process_finder_count=1, process_collector_count=1, fetcher_count=1,
                 fetcher_process_count=15):

        self.__model = model
        self.__model_lock = model_lock
        self.__shutdown = shutdown

        self.__save_path = save_path
        self.__time_to_wait: float = 15
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

    def update_project(self) -> bool:
        for finder in self.__process_finder:
            finder.set_work()
        return self.__time_keeper()

    def __time_keeper(self) -> bool:
        if max(p.time_till_false for p in self.__process_collector_list) <= time.time():
            return False
        return True

    def start(self):
        print("[PassiveDataFetcher]    sending start signal")
        process_list: List[psutil.Process] = list()
        process_list_lock: threading.Lock = threading.Lock()
        # self.__data_fetching_thread.start()
        for i in range(self.__fetcher_count):
            fetcher = FetcherThread(process_list, process_list_lock, self.__model, self.__model_lock,
                                    DataObserver(), self.__fetcher_process_count, self.__shutdown)
            self.__fetcher.append(fetcher)
            fetcher.start()
        for i in range(self.__process_collector_count):
            process_collector_thread = ProcessCollectorThread(process_list, process_list_lock, self.__model, self.__model_lock,
                                       True, self.__fetcher, self.__saver_queue, self.__hierarchy_queue,
                                       self.__save_path, self.__shutdown, self.__found_project_event)
            self.__process_collector_list.append(p)
            process_collector_thread.start()
        for i in range(self.__process_finder_count):
            finder = ProcessFindingThread(self.__process_collector_list, self.__shutdown)
            self.__process_finder.append(finder)
            finder.start()
            time.sleep(0.5)

    def stop(self):
        print("[PassiveDataFetcher]  stop signal sent...")
        for finder in self.__process_finder:
            finder.stop()
        for collector in self.__process_collector_list:
            collector.stop()
        for f in self.__fetcher:
            f.stop()
        print("[PassiveDataFetcher]  stopped all threads")
