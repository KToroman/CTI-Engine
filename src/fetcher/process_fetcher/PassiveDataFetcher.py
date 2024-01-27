import os.path
from typing import List

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
        self.model = model
        self.process_collector: ProcessCollector = ProcessCollector(-1)
        self.data_observer: DataObserver = DataObserver()
        self.path_to_save = path_to_save

    def __check_for_project(self, process: psutil.Process) -> bool:
        return self.process_collector.check(process)

    def add_data_entry(self, process_point: ProcessPoint):
        entry_list: List[DataEntry] = list()
        path: str = self.model.current_project.working_dir
        cmdline: List[str] = process_point.process.cmdline()
        for entry in cmdline:
            if entry.endswith(".o"):
                name: List[str] = entry.split(".dir/")[-1].split(".")
                path += name[0]  # name of cfile
                path += "."
                path += name[1]  # file ending (cpp/cc/...)
        entry = DataEntry(path, process_point.timestamp, process_point.metrics)
        entry_list.append(entry)

    def fetch_metrics(self, process: psutil.Process) -> ProcessPoint:
        return self.data_observer.observe(process)

    def update_project(self) -> bool:
        processes = self.process_collector.catch_processes()
        if not processes:
            for proc in processes:
                if not self.__check_for_project(proc):
                    ppid: int = proc.ppid()
                    parent_ppid: int = psutil.Process(ppid).ppid()
                    working_dir: str = psutil.Process(parent_ppid).cwd()
                    self.model.add_project(Project(working_dir, parent_ppid, self.path_to_save))

                self.add_data_entry(self.fetch_metrics(proc))

            return True

        return False
