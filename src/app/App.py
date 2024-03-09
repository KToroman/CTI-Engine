import multiprocessing
from multiprocessing import Queue
import os
from os.path import join
from threading import Event, Lock

from PyQt5.QtCore import pyqtSignal
from src.app.Threads.ActiveFetcherThread import ActiveFetcherThread

from src.app.Threads.FileFetcherThread import FileFetcherThread
from src.app.Threads.FileSaverThread import FileSaverThread
from src.app.Threads.HierarchyThread import HierarchyThread
from src.app.Threads.PassiveDataThread import PassiveDataThread
from src.fetcher.hierarchy_fetcher.HierarchyFetcher import HierarchyFetcher
from src.fetcher.process_fetcher.ActiveDataFetcher import ActiveDataFetcher
from src.fetcher.process_fetcher.PassiveDataFetcher import PassiveDataFetcher
from src.model.Model import Model
from src.saving.SaveInterface import SaveInterface
from src.saving.SaveToJSON import SaveToJSON

from src.view.AppRequestsInterface import AppRequestsInterface


class App(AppRequestsInterface):
    def __init__(self, shutdown_event: Event, passive_mode_event: Event, load_event: Event,
                 load_path_queue: Queue, source_file_name_queue: Queue, visualize_signal: pyqtSignal, error_queue: Queue, error_signal: pyqtSignal,
                 status_queue: Queue, model_queue: Queue, cancel_event: Event, restart_event: Event):
        self.__model_lock: Lock = Lock()

        self.passive_mode_event = passive_mode_event

        self.load_event = load_event
        self.load_path_queue = load_path_queue
        self.__source_file_name_queue = source_file_name_queue
        self.__error_queue = error_queue
        self.__error_signal = error_signal
        self.visualize_signal = visualize_signal
        self.status_queue = status_queue
        self.model_queue = model_queue
        self.cancel_event = cancel_event
        self.restart_event = restart_event

        self.__cti_dir_path = self.__get_cti_folder_path()

        self.fetching_passive_data = Event()

        self.__model = Model()
        self.__hierarchy_fetcher_work_queue: multiprocessing.Queue = multiprocessing.Queue()
        self.__file_saver_work_queue: multiprocessing.Queue = multiprocessing.Queue()

        self.__passive_data_fetcher: PassiveDataFetcher = PassiveDataFetcher(self.__model, self.__model_lock,
                                                                             self.__file_saver_work_queue,
                                                                             self.__hierarchy_fetcher_work_queue,
                                                                             self.shutdown_event, self.__cti_dir_path)
        self.hierarchy_fetcher = HierarchyFetcher(self.__model, self.__model_lock)
        self.saver: SaveInterface = SaveToJSON(self.__cti_dir_path)

        self.passive_thread: PassiveDataThread = PassiveDataThread(shutdown_event, self.__passive_data_fetcher,
                                                                   self.passive_mode_event, self.fetching_passive_data)

        self.hierarchy_thread: HierarchyThread = HierarchyThread(shutdown_event, self.hierarchy_fetcher,
                                                                 self.error_queue, self.__hierarchy_fetcher_work_queue)

        self.__finished_project_event: Event = Event()

        self.file_saver_thread: FileSaverThread = FileSaverThread(shutdown_event, self.__model, self.saver,
                                                                  self.__model_lock, self.__finished_project_event,
                                                                  self.__file_saver_work_queue)
        self.file_fetch_thread: FileFetcherThread = FileFetcherThread(self.error_queue, self.__model, self.__model_lock,
                                                                      self.shutdown_event, self.load_path_queue)

    def prepare_threads(self):
        self.__active_mode_fetcher_thread: ActiveFetcherThread = ActiveFetcherThread(self.shutdown_event, self.__model, self.__model_lock, self.__source_file_name_queue, self.__error_queue, self.__cti_dir_path)

    def start(self):
        print("[app]    started")
        self.passive_thread.start()
        self.file_saver_thread.start()
        self.hierarchy_thread.start()

    def stop(self):
        self.shutdown_event.set()
        self.passive_thread.stop()
        self.hierarchy_thread.stop()
        self.file_saver_thread.stop()

    def __get_cti_folder_path(self) -> str:
        path: str = ""
        path += join(os.getcwd().split("cti-engine-prototype")[0])
        return path
