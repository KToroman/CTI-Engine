import os.path
import subprocess
import time
from threading import Thread
from typing import List, Tuple

import jsonpickle
import psutil

from src.fetcher.process_fetcher.CProcess import CProcess
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

        self.__seconds_to_wait: int = 15
        self.__time_till_false: float = 0

        self.process_list: List[CProcess] = list()

        self.current_origin_pid: int = -1
        self.project_list: List[str] = list()
        self.time_till_quit = time.time()

        self.entry_queue: List[DataEntry] = list()

        self.is_running = True
        self.got_started = False
        self.processes_found = 0

    def make_entry(self, process_point: ProcessPoint):
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
            self.entry_queue.append(entry)
        except:
            return

    def add_data_entry(self, process_point: ProcessPoint):
        while self.is_running:
            if self.entry_queue and self.__model.current_project is not None:
                self.__time_till_false = time.time() + self.__seconds_to_wait
                self.__model.insert_datapoints([self.entry_queue.pop()])

    def proc_in_proc_list(self, proc: CProcess):
        for process in self.process_list:
            try:
                if proc.pid == process.pid:
                    return True
            except:
                continue
        return False

    def make_process(self, line: str):
        process = self.__process_collector.catch_processes(line)
        if not self.proc_in_proc_list(process) and process is not None:
            self.process_list.append(process)
            print("new Process")
            Thread(target=self.get_data, args=[process]).start()

    def process_catcher(self, processes):
        for line in processes:
            Thread(target=self.make_process, args=[line]).start()

    def get_project_name(self, proc: CProcess) -> str:
        if proc.working_dir.split("build").__len__() > 2:
            return os.path.abspath(proc.working_dir.split("build")[1])
        return proc.working_dir.split("build")[0]


        return proc.cwd()

    def catch_process(self):
            ps = subprocess.Popen(['ps', '-e'], stdout=subprocess.PIPE)
            grep = subprocess.Popen(['grep', 'cc1plus'], stdin=ps.stdout, stdout=subprocess.PIPE, encoding='utf-8')
            grep.stdout.readline()
            Thread(target=self.process_catcher, args=[grep.stdout]).start()


    def fetch_metrics(self, process: CProcess) -> ProcessPoint:
        return self.__data_observer.observe(process)

    def __time_counter(self) -> bool:
        if time.time() >= self.__time_till_false:
            return True
        return False

    def get_data(self, proc: CProcess):
        try:
            while proc.is_running():
                Thread(target=self.make_entry, args=[self.fetch_metrics(proc)], daemon=True).start()
            self.process_list.remove(proc)
        except:
            self.process_list.remove(proc)

    def project_checker(self):
        while self.is_running:
            try:
                proc = self.process_list[-1]
                project_name: str = self.get_project_name(proc)
                if self.__model.current_project is None or project_name != self.__model.current_project.working_dir:
                    self.project_list.append(project_name)
                    self.__model.add_project(Project(project_name, proc.ppid(), self.path_to_save))
            except:
                continue

    def update_project(self) -> bool:
        if not self.got_started:
            self.got_started = True
            Thread(target=self.add_data_entry, args=[None], daemon=True).start()
            Thread(target=self.project_checker, daemon=True).start()
        Thread(target=self.catch_process, daemon=True).start()

        self.time_till_quit = time.time() + 1
        self.time_keeper()
        if self.__time_counter():
            return False
        return True

    def time_keeper(self):
        if self.time_till_quit <= time.time():
            self.is_running = False
            self.got_started = False
