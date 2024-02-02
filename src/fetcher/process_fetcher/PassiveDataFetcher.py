import os.path
import time
from threading import Thread
from typing import List

import jsonpickle
import psutil

from src.fetcher.process_fetcher.DataFetcher import DataFetcher
from src.fetcher.process_fetcher.process_observer.ProcessCollector import ProcessCollector
from src.fetcher.process_fetcher.process_observer.metrics_observer.DataObserver import DataObserver
from src.model.Model import Model
from src.model.core.DataEntry import DataEntry
from src.model.core.ProcessPoint import ProcessPoint
from src.model.core.Project import Project


class PassiveDataFetcher(DataFetcher):

    def __init__(self, model: Model, path_to_save: str):
        self.__model = model
        self.__process_collector: ProcessCollector = ProcessCollector(-1)
        self.__data_observer: DataObserver = DataObserver()
        self.path_to_save = path_to_save
        self.__seconds_to_wait: int = 5
        self.__time_till_false: float = 0
        self.run_catcher: bool = False
        self.process_queue: List[psutil.Process] = list()
        self.catcher_thread = Thread(target=self.catch_process, daemon=True)
        self.collector_thread = Thread(target=self.collector, daemon=True)
        self.got_started = False
        self.current_origin_pid: int = -1
        self.pid_list: List[int] = list()

    def __check_for_project(self, process: psutil.Process) -> bool:
        return self.__process_collector.check(process)

    def add_data_entry(self, process_point: ProcessPoint):
        pid = psutil.Process(psutil.Process(process_point.process.ppid()).ppid()).ppid()
        entry_list: List[DataEntry] = list()
        path: str = self.__model.current_project.working_dir
        cmdline: List[str] = process_point.process.cmdline()
        for line in cmdline:
            if line.endswith(".o"):
                name: List[str] = line.split(".dir/")[-1].split(".")
                path += name[0]  # name of cfile
                path += "."
                path += name[1]  # file ending (cpp/cc/...)
        entry: DataEntry = DataEntry(path, process_point.timestamp, process_point.metrics)
        entry_list.append(entry)
        self.__model.insert_datapoints(entry_list, pid)

    def catch_process(self):
        while self.run_catcher:
            for process in psutil.process_iter(['pid', 'name', 'username']):
                proc = self.__process_collector.catch_processes(process)
                if proc is not None and self.not_in_queue(proc):
                    self.__time_till_false = time.time() + self.__seconds_to_wait
                    print("got process")
                    self.process_queue.append(proc)

    def not_in_queue(self, process: psutil.Process):
        for p in self.process_queue:
            if p.ppid() == process.ppid():
                return False
        return True

    def fetch_metrics(self, process: psutil.Process) -> ProcessPoint:
        return self.__data_observer.observe(process)

    def __time_counter(self) -> bool:
        if time.time() >= self.__time_till_false:
            return True
        return False

    def get_data(self, proc: psutil.Process):
        print("data thread")

        pid: int = psutil.Process(psutil.Process(proc.ppid()).ppid()).ppid()
        if pid not in self.pid_list:
            self.pid_list.append(pid)
            print(psutil.Process(pid))
            working_dir: str = psutil.Process().cwd()
            self.__model.add_project(Project(working_dir, pid, self.path_to_save))
        while proc.is_running():
            self.add_data_entry(self.fetch_metrics(proc))
            time.sleep(0.01)

    def collector(self):
        while True:
            if self.process_queue.__len__() != 0:
                Thread(target=self.get_data, args=[self.process_queue.pop()], daemon=True).start()
                time.sleep(0.1)

    def update_project(self) -> bool:
        if not self.got_started:
            self.got_started = True
            self.run_catcher = True
            self.collector_thread.start()
            self.catcher_thread.start()

        if self.__time_counter():
            return False
        return True
