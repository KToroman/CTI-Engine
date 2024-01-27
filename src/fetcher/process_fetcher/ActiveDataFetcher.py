import psutil
from fetcher.FetcherInterface import FetcherInterface
from fetcher.process_fetcher.process_observer.metrics_observer.DataObserver import DataObserver
from model.Model import Model
from model.core.ProcessPoint import ProcessPoint

class ActiveDataFetcher(FetcherInterface):
    def update_project() -> bool:
        pass

    def __init__(self, model: Model) -> None:
        self.model = model
        self.data_observer = DataObserver()

    def fetch_metrics(self, process: psutil.Process) -> ProcessPoint:
        return self.data_observer.observe(process)
    
    def add_data_entry(process_point: ProcessPoint):
        name: str = process_point.process.name()
        
