import os.path
import subprocess
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
        self.__path_to_save = path_to_save
        self.__process_collector: ProcessCollector = ProcessCollector()
        self.__data_observer: DataObserver = DataObserver()

        self.__entry_list: List[DataEntry] = list()
        self.__process_list: List[psutil.Process] = list()

        self.__time_to_wait: int = 15
        self.__time_till_false: int = 0

    def update_project(self) -> bool:
        Thread(target=self.__catch_process).start()
        self.__project_checker()
        self.add_data_entry(None)
        return self.__time_keeper()

    def add_data_entry(self, process_point: ProcessPoint):
        if self.__entry_list:
            self.__model.insert_datapoints(self.__entry_list)
            self.__time_till_false = time.time() + self.__time_to_wait

    def fetch_metrics(self, process: psutil.Process) -> ProcessPoint:
        return self.__data_observer.observe(process)

    def __time_keeper(self) -> bool:
        if self.__time_till_false <= time.time():
            return False
        return True

    def __catch_process(self):
        ps = subprocess.Popen(['ps', '-e'], stdout=subprocess.PIPE)
        grep = subprocess.Popen(['grep', 'cc1plus'], stdin=ps.stdout, stdout=subprocess.PIPE, encoding='utf-8')
        grep.stdout.readline()
        for line in grep.stdout:
            Thread(target=self.__make_process, args=[line]).start()

    def __make_process(self, line: str):
        process = self.__process_collector.catch_processes(line)
        if not self.__process_in_list(process) and process is not None:
            self.__process_list.append(process)
            print("new Process")
            Thread(target=self.__get_data, args=[process]).start()

    def __get_data(self, process: psutil.Process):
        try:
            while process.is_running():
                Thread(target=self.__make_entry, args=[self.fetch_metrics(process)], daemon=True).start()
            self.__process_list.remove(process)
        except:
            self.__process_list.remove(process)

    def __make_entry(self, process_point: ProcessPoint):
        try:
            cmdline: List[str] = process_point.process.cmdline()
            path: str = ""
            for line in cmdline:
                if line.endswith(".o"):
                    path = os.path.abspath(line)
                    break
            if path == "":
                return
            entry: DataEntry = DataEntry(path, process_point.timestamp, process_point.metrics)
            self.__entry_list.append(entry)
        except:
            return

    def __process_in_list(self, process: psutil.Process):
        for proc in self.__process_list:
            try:
                if proc.pid == process.pid:
                    return True
            except:
                continue
        return False

    def __project_checker(self):
        try:
            proc = self.__process_list[-1]
            project_name: str = self.__get_project_name(proc)
            if self.__model.current_project is None or project_name != self.__model.current_project.working_dir:
                self.__model.add_project(Project(project_name, proc.ppid(), self.__path_to_save))
        except:
            return

    def __get_project_name(self, process: psutil.Process) -> str:
        working_dir: str = process.cwd()
        if working_dir.split("build").__len__() > 2:
            return os.path.abspath(working_dir.split("build")[1])
        return working_dir.split("build")[0]
