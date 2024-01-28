import os
from typing import List
import psutil
from builder.BuilderInterface import BuilderInterface
from builder.header_builder.CompilingTool import CompilingTool
from fetcher.FetcherInterface import FetcherInterface
from fetcher.process_fetcher.process_observer.ProcessCollector import ProcessCollector
from fetcher.process_fetcher.process_observer.metrics_observer.DataObserver import (
    DataObserver,
)
from model.Model import Model
from model.core.DataEntry import DataEntry
from model.core.ProcessPoint import ProcessPoint
from model.core.SourceFile import SourceFile


class ActiveDataFetcher(FetcherInterface):
    def update_project() -> bool:
        pass

    def __init__(self, source_file_name: str, model: Model, build_dir_path: str) -> None:
        self.model = model
        self.source_file: SourceFile = model.get_sourcefile_by_name(source_file_name)
        self.data_observer = DataObserver()
        self.process_collector = ProcessCollector(-1)
        self.compiling_tool: BuilderInterface = CompilingTool(self.source_file, build_dir_path)  # TODO

    def fetch_metrics(self, process: psutil.Process) -> ProcessPoint:
        return self.data_observer.observe(process)

    def add_data_entry(self, process_point: ProcessPoint):
        path: str = self.model.current_project.working_dir
        cmdline: List[str] = process_point.process.cmdline()
        for entry in cmdline:
            if entry.endswith(".o"):
                name: List[str] = entry.split(".dir/")[-1].split(".")
                path += name[0]  # name of cfile
                path += "."
                path += name[1]  # file ending (cpp/cc/...) # TODO get header file ending from source file or builder
        self.model.insert_datapoints(
            [DataEntry(path, process_point.metrics, process_point.timestamp)]
        )
