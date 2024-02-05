from time import time
from typing import List
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
    __seconds__to_move_on = 1

    def update_project(self) -> bool:
        found_header: bool = True
        self.__header_proc: psutil.Process = None
        self.__move_on_to_next_header()
        found_header = self.search_for_header()
        while found_header:
            found_header = self.search_for_header()
            if found_header:
                process_point: ProcessPoint = self.__fetch_metrics(
                    self.__header_proc)
                self.__add_data_entry(process_point)
                self.__time_header_last_found = time()
            elif self.__time_header_last_found + ActiveDataFetcher.__seconds__to_move_on < time():
                self.__move_on_to_next_header()
                found_header = True
        return self.__done_building

    def __move_on_to_next_header(self) -> None:
        if self.__done_building:
            self.__header: Header = self.__compiling_tool.get_next_header()
            self.__done_building: bool = self.__compiling_tool.build()

    def search_for_header(self) -> bool:
        processes: List[psutil.Process] = self.__process_collector.catch_processes(
        )
        for process in processes:
            if ActiveDataFetcher.filter_for_str(
                    process, self.__header.path):
                self.__header_proc = process
                return True
        return False

    def filter_for_str(process: psutil.Process, string: str):
        cmdline: List[str] = process.cmdline()
        for entry in cmdline:
            if string in entry and entry.endswith(".o"):
                return True
        return False

    def __init__(
        self, source_file_name: str, model: Model, build_dir_path: str
    ) -> None:
        self.__model = model
        self.__source_file: SourceFile = model.get_sourcefile_by_name(
            source_file_name)
        self.__data_observer = DataObserver()
        self.__process_collector = ProcessCollector(-1)
        self.__compiling_tool: BuilderInterface = CompilingTool(
            self.__source_file, build_dir_path
        )  # TODO
        self.__time_header_last_found: float = 0

    def __fetch_metrics(self, process: psutil.Process) -> ProcessPoint:
        return self.__data_observer.observe(process)

    def __add_data_entry(self, process_point: ProcessPoint):
        data_entry: DataEntry = DataEntry(self.__header.path, process_point.metrics, process_point.timestamp)
        self.__model.insert_datapoints_header(
            [data_entry], self.__header
        )
