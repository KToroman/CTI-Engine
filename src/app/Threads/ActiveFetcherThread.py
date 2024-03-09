from multiprocessing import Queue
from threading import Event, Lock, Thread

from src.fetcher.process_fetcher.ActiveDataFetcher import ActiveDataFetcher
from src.model.Model import Model


class ActiveFetcherThread:
    def __init__(self, shutdown_event: Event, model: Model, model_lock: Lock, source_file_name_queue: Queue, error_queue: Queue, build_dir_path: str) -> None:
        self.__thread: Thread
        self.__model: Model = model
        self.__model_lock: Lock = model_lock
        self.__shutdown_event: Event = shutdown_event
        self.__source_file_name_queue: Queue = source_file_name_queue
        self.__error_queue: Queue = error_queue
        self.__build_dir_path: str = build_dir_path

    def start(self):
        print("[ActiveFetcherThread]    started")
        self.__thread = Thread(target=self.__run)
        self.__thread.start()

    def __run(self):
        while not self.__shutdown_event.is_set():
            if not self.__source_file_name_queue.empty():
                self.__start_new_measurement()

    def __start_new_measurement(self):
        source_file_name: str = self.__source_file_name_queue.get(True, 10)
        if (source_file_name == None):
            timeout_error: TimeoutError = TimeoutError("[ActiveFetcherThread] Active Fetcher Thread could not access its source-file-queue.")
            self.__error_queue.put(timeout_error, True, 15)
            return
        active_data_fetcher: ActiveDataFetcher = ActiveDataFetcher(source_file_name=source_file_name, model=self.__model, build_dir_path=self.__build_dir_path, model_lock=self.__model_lock)
        self.measure_source_file(active_data_fetcher)
        
    def measure_source_file(self, active_data_fetcher: ActiveDataFetcher):
        actively_fetching: bool = False
        while (not self.__shutdown_event.is_set) and (actively_fetching):
            actively_fetching = active_data_fetcher.update_project()

    def stop(self):
        print("[ActiveFetcherThread]    stop signal sent.")
        if self.__thread.is_alive():
            self.__thread.join()
        print("[ActiveFetcherThread]    stopped.")