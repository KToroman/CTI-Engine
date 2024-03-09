import os.path
import threading
import time
from multiprocessing import Queue
from os.path import join
from threading import Thread
from typing import List

import psutil
from psutil import NoSuchProcess

from src.fetcher.hierarchy_fetcher.HierarchyFetcher import HierarchyFetcher

from src.fetcher.process_fetcher.DataFetcher import DataFetcher
from src.fetcher.process_fetcher.Threads.FetcherThread import FetcherThread
from src.fetcher.process_fetcher.Threads.ProcessCollectorThread import ProcessCollectorThread
from src.fetcher.process_fetcher.Threads.ProcessFindingThread import ProcessFindingThread
from src.fetcher.process_fetcher.process_observer.ProcessCollector import ProcessCollector
from src.fetcher.process_fetcher.process_observer.metrics_observer.DataObserver import DataObserver
from src.model.Model import Model
from src.model.core.DataEntry import DataEntry
from src.model.core.ProcessPoint import ProcessPoint


class PassiveDataFetcher(DataFetcher):

    def __init__(self, model: Model, model_lock: threading.Lock, saver_queue: Queue, hierarchy_queue: Queue):
        self.__model = model
        self.__model_lock = model_lock

        self.__time_to_wait: float = 15
        self.__time_till_false_lock = threading.Lock()

        self.__saver_queue = saver_queue
        self.__hierarchy_queue = hierarchy_queue

        self.__process_finder: List[ProcessFindingThread] = list()
        self.__process_finder_count = 1

        self.__process_collector_list: List[ProcessCollectorThread] = list()
        self.__process_collector_count = 1

        self.__fetcher_count: int = 1
        self.__process_count = 15
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
                                    DataObserver(), self.__process_count)
            self.__fetcher.append(fetcher)
            fetcher.start()
        for i in range(self.__process_collector_count):
            p = ProcessCollectorThread(process_list, process_list_lock, self.__model, self.__model_lock,
                                       True, self.__fetcher, self.__saver_queue, self.__hierarchy_queue)
            self.__process_collector_list.append(p)
            p.start()
        for i in range(self.__process_finder_count):
            finder = ProcessFindingThread(self.__process_collector_list)
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
