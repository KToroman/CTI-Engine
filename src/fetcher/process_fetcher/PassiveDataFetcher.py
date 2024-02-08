
import time
from os.path import join
from threading import Thread
from typing import List
import psutil
from src.fetcher.hierarchy_fetcher.HierarchyFetcher import HierarchyFetcher

from src.fetcher.process_fetcher.DataFetcher import DataFetcher
from src.fetcher.process_fetcher.process_observer.ProcessCollector import ProcessCollector
from src.fetcher.process_fetcher.process_observer.metrics_observer.DataObserver import DataObserver
from src.model.Model import Model
from src.model.core.DataEntry import DataEntry
from src.model.core.ProcessPoint import ProcessPoint


class PassiveDataFetcher(DataFetcher):

    def __init__(self, model: Model):
        self.__model = model
        self.__process_collector: ProcessCollector = ProcessCollector(model)
        self.__data_observer: DataObserver = DataObserver()
        self.__time_to_wait: float = 15
        self.__time_till_false: float = 0

    def update_project(self) -> bool:
        Thread(target=self.__fetch_process, daemon=True).start()
        return self.__time_keeper()

    def add_data_entry(self, data_entry: DataEntry):
        self.__model.insert_datapoint(data_entry)
        self.__time_till_false = time.time() + self.__time_to_wait

    def fetch_metrics(self, process: psutil.Process) -> ProcessPoint:
        return self.__data_observer.observe(process)

    def __time_keeper(self) -> bool:
        if self.__time_till_false <= time.time():
            return False
        return True

    def __fetch_process(self):
        processes = self.__process_collector.catch_process()
        if processes is None:
            return
        for line in processes:
            Thread(target=self.__create_process, args=[line]).start()

    def __create_process(self, line: str):
        Thread(target=self.__get_data, args=[self.__process_collector.make_process(line)]).start()

    def __get_data(self, process: psutil.Process):
        try:
            if process is None:
                return
            while process.is_running():
                Thread(target=self.__make_entry, args=[self.fetch_metrics(process)]).start()
            self.__process_collector.process_list.remove(process)
        except:
            self.__process_collector.process_list.remove(process)

    def __make_entry(self, process_point: ProcessPoint):
        try:
            cmdline: List[str] = process_point.process.cmdline()
            path: str = process_point.process.cwd()
            for line in cmdline:
                if line.endswith(".o"):
                    path = join(path.split("build/")[0], "build",path.split("build/")[1], "build", line)
                    break
            if path == "":
                return
            entry: DataEntry = DataEntry(path, process_point.timestamp, process_point.metrics)
            self.add_data_entry(entry)
        except:
            return
