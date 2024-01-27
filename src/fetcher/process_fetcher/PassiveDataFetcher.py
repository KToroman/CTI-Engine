import psutil

from src.fetcher.process_fetcher.DataFetcher import DataFetcher
from src.fetcher.process_fetcher.process_observer.ProcessCollector import ProcessCollector
from src.fetcher.process_fetcher.process_observer.metrics_observer.DataObserver import DataObserver
from src.model.Model import Model
from src.model.core.DataEntry import DataEntry
from src.model.core.ProcessPoint import ProcessPoint


class PassiveDataFetcher(DataFetcher):

    def __init__(self, model: Model):
        self.model = model
        self.process_collector: ProcessCollector = ProcessCollector()
        self.data_observer: DataObserver = DataObserver()


    def __check_for_project(self, process: psutil.Process):

    def add_data_entry(self, process_point: ProcessPoint):
        entry = DataEntry()


        self.model.insert_datapoints(entry)

    def fetch_metrics(self, process: psutil.Process) -> ProcessPoint:
        raise NotImplemented

    def update_project(self) -> bool:
        raise NotImplemented

