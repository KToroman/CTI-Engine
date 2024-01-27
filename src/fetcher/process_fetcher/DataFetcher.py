from typing import Protocol

import psutil

from src.fetcher.FetcherInterface import FetcherInterface
from src.fetcher.process_fetcher.process_observer.ProcessCollector import ProcessCollector
from src.fetcher.process_fetcher.process_observer.metrics_observer.DataObserver import DataObserver
from src.model.Model import Model
from src.model.core.DataEntry import DataEntry
from src.model.core.ProcessPoint import ProcessPoint


class DataFetcher(FetcherInterface, Protocol):

    process_collector: ProcessCollector = None
    data_observer: DataObserver = None

    def add_data_entry(self, process_point: ProcessPoint):
        raise NotImplemented

    def fetch_metrics(self, process: psutil.Process) -> ProcessPoint:
        raise NotImplemented

    def update_project(self) -> bool:
        raise NotImplemented
