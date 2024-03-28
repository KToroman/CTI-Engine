from typing import Protocol

import psutil

from src.fetcher.FetcherInterface import FetcherInterface
from src.model.core.DataEntry import DataEntry
from src.model.core.ProcessPoint import ProcessPoint


class DataFetcher(FetcherInterface, Protocol):
    def add_data_entry(self, data_entry: DataEntry) -> None:
        raise NotImplemented

    def fetch_metrics(self, process: psutil.Process) -> ProcessPoint:
        raise NotImplemented

    def update_project(self) -> bool:
        raise NotImplemented
