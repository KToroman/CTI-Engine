from multiprocessing import Queue, Lock
from threading import Thread
from multiprocessing.synchronize import Event as SyncEvent
from multiprocessing.synchronize import Lock as SyncLock

from PyQt5.QtCore import pyqtSignal

from src.fetcher.process_fetcher.ActiveDataFetcher import ActiveDataFetcher
from src.model.Model import Model


class ActiveFetcherThread:
    def __init__(self,
                 shutdown_event: SyncEvent,
                 saver_queue: Queue,
                 save_path: str,
                 model: Model,
                 model_lock: Lock,
                 source_file_name_queue: Queue,
                 error_queue: Queue,
                 build_dir_path: str,
                 active_measurement_active: SyncEvent,
                 visualise_event: pyqtSignal,
                 visualise_project_queue: Queue) -> None:
        self.__thread: Thread
        self.__model: Model = model
        self.__model_lock: SyncLock = model_lock
        self.__shutdown_event: SyncEvent = shutdown_event
        self.__source_file_name_queue: Queue = source_file_name_queue
        self.__error_queue: Queue = error_queue
        self.__build_dir_path: str = build_dir_path
        self.__active_measurement_active: SyncEvent = active_measurement_active
        self.__saver_queue: Queue = saver_queue
        self.__save_path: str = save_path
        self.__visualise_signal: pyqtSignal = visualise_event
        self.__visualise_project_queue: Queue = visualise_project_queue

    def start(self):
        print("[ActiveFetcherThread]    started")
        self.__thread = Thread(target=self.__run)
        self.__thread.start()

    def __run(self):
        while not self.__shutdown_event.is_set():
            if not self.__source_file_name_queue.empty():
                self.__active_measurement_active.set()
                self.__start_new_measurement()

    def __start_new_measurement(self):
        source_file_name: str = self.__source_file_name_queue.get(True, 10)
        if (source_file_name == None):
            timeout_error: TimeoutError = TimeoutError(
                "[ActiveFetcherThread] Active Fetcher Thread could not access its source-file-queue.")
            self.__error_queue.put(timeout_error, True, 15)
            return
        active_data_fetcher: ActiveDataFetcher
        with ActiveDataFetcher(source_file_name=source_file_name, model=self.__model, saver_queue=self.__saver_queue, save_path=self.__save_path,
                               build_dir_path=self.__build_dir_path, model_lock=self.__model_lock, hierarchy_queue=Queue()) as active_data_fetcher:
            self.measure_source_file(active_data_fetcher)

        with self.__model_lock:
            project: str = self.__model.current_project.name

        self.__saver_queue.put(project)
        self.__visualise_project_queue.put(project)
        self.__visualise_signal.emit()
        
    def measure_source_file(self, active_data_fetcher: ActiveDataFetcher):
        actively_fetching: bool = True
        while (not self.__shutdown_event.is_set()) and actively_fetching:
            actively_fetching = active_data_fetcher.update_project()

    def stop(self):
        print("[ActiveFetcherThread]    stop signal sent.")
        if self.__thread.is_alive():
            self.__thread.join()
        print("[ActiveFetcherThread]    stopped.")
