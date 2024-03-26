import time
from multiprocessing import Queue, Lock
from multiprocessing.synchronize import Lock as SyncLock
from typing import List
from multiprocessing.synchronize import Event as SyncEvent

import psutil
from PyQt5.QtCore import pyqtSignal

from src.fetcher.process_fetcher.DataFetcher import DataFetcher
from src.fetcher.process_fetcher.Threads.PassiveDataCollectionThread import PassiveDataCollectionThread
from src.fetcher.process_fetcher.Threads.ProcessCollectorThread import ProcessCollectorThread
from src.fetcher.process_fetcher.Threads.ProcessFindingThread import ProcessFindingThread

from src.fetcher.process_fetcher.process_observer.metrics_observer.DataObserver import DataObserver
from src.model.Model import Model
from src.model.core.Project import Project


class PassiveDataFetcher(DataFetcher):

    def __init__(self, model: Model, model_lock: SyncLock, saver_queue: "Queue[str]", hierarchy_queue: "Queue[Project]",
                 shutdown: SyncEvent, save_path: str, project_queue: "Queue[str]", finished_event: pyqtSignal,
                 project_finished_event: SyncEvent, passive_mode_event: SyncEvent, pid_queue: "Queue[str]",
                 process_finder_count: int = 2, process_collector_count: int = 2, fetcher_count: int = 2,
                 fetcher_process_count: int = 15) -> None:

        self.__model = model
        self.__model_lock = model_lock
        self.__shutdown = shutdown

        self.__passive_event = passive_mode_event
        self.__project_queue = project_queue
        self.__finished_event = finished_event
        self.__project_finished_event = project_finished_event

        self.__save_path = save_path

        self.__time_till_false_lock: SyncLock = Lock()

        self.__saver_queue = saver_queue
        self.__hierarchy_queue = hierarchy_queue

        self.__process_finder: List[ProcessFindingThread] = list()
        self.__process_finder_count = process_finder_count

        self.__process_collector_list: List[ProcessCollectorThread] = list()
        self.__process_collector_count = process_collector_count

        self.__fetcher_count: int = fetcher_count
        self.__fetcher_process_count = fetcher_process_count
        self.__fetcher: List[PassiveDataCollectionThread] = list()
        self.__done_fetching: bool = True
        self.max_time = 0
        self.__pid_queue = pid_queue

        self.__pid_list: List[str] = list()

        self.__save_time: float = 0

        self.workers_on: bool = False

    def update_project(self) -> bool:
        current_project = ""
        with self.__model_lock:
            if self.__model.current_project is not None and self.__model.project_in_semaphore_list(self.__model.current_project.working_dir):
                current_project = self.__model.current_project.working_dir
        while not self.__pid_queue.empty():
            item = self.__pid_queue.get()
            self.__pid_list.append(item)
        for finder in self.__process_finder:
            finder.set_work(self.__pid_list)
        for p in self.__process_collector_list:
            p.current_project = current_project
        time_keeper_bool: bool = self.__time_keeper()
        if time_keeper_bool:
            self.__done_fetching = False
        else:
            if not self.__done_fetching:
                self.finish_fetching()
        self.__pid_list.clear()
        return time_keeper_bool

    def finish_fetching(self) -> None:
        if not self.__done_fetching:
            self.__done_fetching = True
            self.__semaphore()

    def __semaphore(self) -> None:
        with self.__model_lock:
            if self.__model.current_project is not None and self.__model.project_in_semaphore_list(self.__model.get_current_working_directory()):
                with self.__model.get_semaphore_by_name(self.__model.current_project.name).set_lock:
                    self.__model.get_semaphore_by_name(self.__model.current_project.name).stop_fetcher_set()

    def cancel(self):
        if not self.__done_fetching:
            self.__done_fetching = True
        for sem in self.__model.semaphore_list:
            sem.stop_fetcher_set()

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

    def start(self) -> None:
        process_list: List[psutil.Process] = list()
        process_list_lock: SyncLock = Lock()
        # self.__data_fetching_thread.start()
        for i in range(self.__fetcher_count):
            fetcher = PassiveDataCollectionThread(process_list, process_list_lock, self.__model, self.__model_lock,
                                           DataObserver(), self.__fetcher_process_count, self.__shutdown,
                                           self.__passive_event)
            self.__fetcher.append(fetcher)
            fetcher.start()
        for i in range(self.__process_collector_count):
            process_collector_thread = ProcessCollectorThread(process_list, process_list_lock, self.__model,
                                                              self.__model_lock,
                                                              True, self.__fetcher, self.__saver_queue,
                                                              self.__hierarchy_queue,
                                                              self.__save_path, self.__shutdown, self.__project_queue,
                                                              self.__finished_event, self.__project_finished_event,
                                                              self.__passive_event)
            self.__process_collector_list.append(process_collector_thread)
            process_collector_thread.start()
        for i in range(self.__process_finder_count):
            finder = ProcessFindingThread(self.__shutdown, self.__process_collector_list, self.__passive_event,
                                          active_fetching=False)
            self.__process_finder.append(finder)
            finder.start()
        self.workers_on = True

    def stop(self) -> None:
        for finder in self.__process_finder:
            finder.stop()
        for collector in self.__process_collector_list:
            collector.stop()
        for f in self.__fetcher:
            f.stop()
        self.workers_on = False

    def restart_workers(self) -> None:
        for finder in self.__process_finder:
            finder.start()
        for collector in self.__process_collector_list:
            collector.start()
        for f in self.__fetcher:
            f.start()
        self.workers_on = True
