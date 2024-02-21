
import os.path
import threading
from threading import Thread
from time import time
from typing import List
from os.path import join
import psutil
from src.builder.BuilderInterface import BuilderInterface
from src.builder.header_builder.CompilingTool import CompilingTool
from src.fetcher.FetcherInterface import FetcherInterface
from src.fetcher.process_fetcher.process_observer.ProcessCollector import ProcessCollector
from src.fetcher.process_fetcher.process_observer.metrics_observer.DataObserver import (
    DataObserver,
)
from src.model.Model import Model
from src.model.core.DataEntry import DataEntry
from src.model.core.Header import Header
from src.model.core.ProcessPoint import ProcessPoint
from src.model.core.SourceFile import SourceFile


class ActiveDataFetcher(FetcherInterface):
    __seconds__to_move_on = 3

    def __init__(
            self, source_file_name: str, model: Model, build_dir_path: str, model_lock: threading.Lock
    ) -> None:
        self.__model = model
        self.__model_lock = model_lock
        self.__source_file: SourceFile = model.get_sourcefile_by_name(
            source_file_name)
        self.__data_observer = DataObserver()
        self.__process_collector = ProcessCollector(model, False, model_lock)
        self.__compiling_tool: BuilderInterface = CompilingTool(curr_project_dir=model.current_project.working_dir,
                                                                source_file=self.__source_file, path=build_dir_path
                                                                )
        self.__time_header_last_found: float = 0
        self.__done_building = False

    def update_project(self) -> bool:
        self.__move_on_to_next_header()
        Thread(target=self.__fetch_process, daemon=True).start()
        return not self.__done_building

    # TODO wiederholen bis header weg

    def __fetch_process(self):
        while self.__time_header_last_found + self.__seconds__to_move_on < time():
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
            if not self.filter_for_str(process, self.__header.build_file_name):
                return
            while process.is_running():
                Thread(target=self.__make_entry, args=[self.fetch_metrics(process)]).start()
                self.__time_header_last_found = time()
            self.__process_collector.remove_process_from_list(process)
        except:
            self.__process_collector.remove_process_from_list(process)

    def fetch_metrics(self, process: psutil.Process) -> ProcessPoint:
        return self.__data_observer.observe(process)

    def __make_entry(self, process_point: ProcessPoint):
        try:
            cmdline: List[str] = process_point.process.cmdline()
            path: str = ""
            for line in cmdline:
                if line.endswith(".o"):
                    path = os.path.split(line)[-1].replace("#", "/")
                    path = path.removesuffix(".cpp.o")
                    break
            if path == "":
                return
            entry: DataEntry = DataEntry(path, process_point.timestamp, process_point.metrics)
            self.__time_header_last_found = time()
            self.add_data_entry(entry)
        except psutil.NoSuchProcess:
            return

    def add_data_entry(self, data_entry: DataEntry):
        self.__model_lock.acquire()
        self.__model.insert_datapoint_header(data_entry, self.__source_file)
        self.__model_lock.release()

    def __move_on_to_next_header(self) -> None:
        if not self.__done_building:
            self.__header: Header = self.__compiling_tool.get_next_header()
            self.__done_building: bool = not self.__compiling_tool.build()

    def filter_for_str(self, process: psutil.Process, string: str) -> bool:
        cmdline: List[str] = process.cmdline()
        for entry in cmdline:
            if string in entry and entry.endswith(".o"):
                return True
        return False
