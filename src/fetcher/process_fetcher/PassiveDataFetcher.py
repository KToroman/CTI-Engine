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

        self.__seconds_to_wait: int = 5
        self.__time_till_false: float = 0

        self.process_list: List[CProcess] = list()

        self.current_origin_pid: int = -1
        self.pid_list: List[int] = list()
        self.time_till_quit = time.time()

        self.is_running = True
        self.got_started = False

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

    def process_catcher(self, processes):
        proc: List[CProcess] = self.__process_collector.catch_processes(processes)
        for process in proc:
            if process not in self.process_list:
                self.__time_till_false = time.time() + self.__seconds_to_wait
                print("got process")
                self.process_list.append(process)

    def catch_process(self):

        while self.is_running:
            ps = subprocess.Popen(['ps', '-ef'], stdout=subprocess.PIPE)
            grep = subprocess.Popen(['grep', 'CMakeFiles'], stdin=ps.stdout, stdout=subprocess.PIPE)
            ps.stdout.close()
            grep.stdout.readline()
            Thread(target=self.process_catcher, args=[grep.stdout])

    def fetch_metrics(self, process: psutil.Process) -> ProcessPoint:
        return self.__data_observer.observe(process)

    def __time_counter(self) -> bool:
        if time.time() >= self.__time_till_false:
            return True
        return False

    def get_data(self, proc: CProcess):
        print("data thread")

        try:
            pid: int = psutil.Process(psutil.Process(proc.ppid()).ppid()).ppid()
            if pid not in self.pid_list:
                self.pid_list.append(pid)
                print(psutil.Process(pid))
                working_dir: str = psutil.Process().cwd()
                self.__model.add_project(Project(working_dir, pid, self.path_to_save))
            while proc.is_running():
                self.add_data_entry(self.fetch_metrics(proc))
                time.sleep(0.01)
            self.process_list.remove(proc)
        except:
            self.process_list.remove(proc)

    def collector(self):

        while self.is_running:
            for proc in self.process_list:
                if proc.gets_observed is False:
                    proc.gets_observed = True
                    Thread(target=self.get_data, args=[proc], daemon=True).start()
                time.sleep(0.1)

    def update_project(self) -> bool:
        if not self.got_started:
            self.got_started = True
            Thread(target=self.catch_process, daemon=True).start()
            Thread(target=self.collector, daemon=True).start()

        self.time_till_quit = time.time() + 3
        self.time_keeper()
        if self.__time_counter():
            return False
        return True

    def time_keeper(self):
        if self.time_till_quit <= time.time():
            self.is_running = False
            self.got_started = False
