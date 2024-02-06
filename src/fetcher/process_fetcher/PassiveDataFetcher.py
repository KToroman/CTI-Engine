import os.path
import time
from typing import List

import jsonpickle
import psutil
from src.fetcher import hierarchy_fetcher
from src.fetcher.hierarchy_fetcher.HierarchyFetcher import HierarchyFetcher

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

    def __check_for_project(self, process: psutil.Process) -> bool:
        return self.__process_collector.check(process)

    def add_data_entry(self, process_point: ProcessPoint):
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
        self.__model.insert_datapoints(entry_list)

    def fetch_metrics(self, process: psutil.Process) -> ProcessPoint:
        return self.__data_observer.observe(process)

    def __time_counter(self) -> bool:
        if 0 <= self.__time_till_false >= time.time():
            self.__time_till_false = time.time() + self.__seconds_to_wait
            return False
        elif self.__time_till_false <= time.time():
            self.__time_till_false = 0
            return True
        return False

    def update_project(self) -> bool:
        processes: List[psutil.Process] = self.__process_collector.catch_processes()
        if not processes:
            if self.__time_counter():
                return self.finish_measurment()
            return True

        for proc in processes:
            if not self.__check_for_project(proc):
                ppid: int = proc.ppid()
                parent_ppid: int = psutil.Process(ppid).ppid()
                working_dir: str = psutil.Process(ppid).cwd()
                self.__model.add_project(Project(working_dir, parent_ppid, self.path_to_save))

            self.add_data_entry(self.fetch_metrics(proc))

        self.__time_till_false = 0
        return True

    def finish_measurment(self):
        if self.__model.projects:
            hierarchy_fetcher = HierarchyFetcher(self.__model)
            return hierarchy_fetcher.update_project()
        return True