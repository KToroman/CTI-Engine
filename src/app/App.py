from multiprocessing import Queue, Event, Lock
from multiprocessing.synchronize import Event as SyncEvent
import os
from os.path import join

from PyQt5.QtCore import pyqtSignal
from src.app.Threads.ActiveFetcherThread import ActiveFetcherThread

from src.app.Threads.FileFetcherThread import FileFetcherThread
from src.app.Threads.FileSaverThread import FileSaverThread
from src.app.Threads.HierarchyThread import HierarchyThread
from src.app.Threads.PassiveDataThread import PassiveDataThread
from src.fetcher.file_fetcher.FileLoader import FileLoader
from src.fetcher.hierarchy_fetcher.HierarchyFetcher import HierarchyFetcher
from src.fetcher.process_fetcher.PassiveDataFetcher import PassiveDataFetcher
from src.app.Threads.GUICommunicationManager import GUICommunicationManager
from src.model.Model import Model
from src.saving.SaveInterface import SaveInterface
from src.saving.SaveToJSON import SaveToJSON

from src.view.AppRequestsInterface import AppRequestsInterface


class App(AppRequestsInterface):
    def __init__(self, shutdown_event: Event, passive_mode_event: Event, load_event: Event,
                 load_path_queue: Queue, source_file_name_queue: Queue, visualize_signal: pyqtSignal,
                 error_queue: Queue, error_signal: pyqtSignal, status_signal: pyqtSignal,
                 status_queue: Queue, project_queue: Queue, cancel_event: Event, restart_event: Event, model: Model):
        self.__model_lock: Lock = Lock()

        self.passive_mode_event = passive_mode_event
        self.shutdown_event = shutdown_event
        self.load_event = load_event

        self.load_path_queue = load_path_queue

        self.__source_file_name_queue = source_file_name_queue
        self.__error_queue = error_queue
        self.__error_signal = error_signal
        self.__status_signal = status_signal
        self.visualize_signal = visualize_signal
        self.status_queue = status_queue
        self.__project_queue = project_queue
        self.__restart_event = restart_event
        self.__finished_project_event: Event = Event()

        self.__cancel_event = cancel_event

        self.__cti_dir_path = self.__get_cti_folder_path()

        self.fetching_passive_data: Event = Event()
        self.__active_measurement_active: Event = Event()

        self.__fetching_hierarchy: SyncEvent = Event()

        self.__model = model
        self.__hierarchy_fetcher_work_queue: Queue = Queue()
        self.__file_saver_work_queue: Queue = Queue()
        self.__pid_queue: Queue = Queue()

        self.__passive_data_fetcher: PassiveDataFetcher = PassiveDataFetcher(self.__model, self.__model_lock,
                                                                             self.__file_saver_work_queue,
                                                                             self.__hierarchy_fetcher_work_queue,
                                                                             self.shutdown_event, self.__cti_dir_path,
                                                                             self.__project_queue,
                                                                             self.visualize_signal,
                                                                             self.__finished_project_event,
                                                                             self.passive_mode_event,
                                                                             process_finder_count=5,
                                                                             process_collector_count=3,
                                                                             fetcher_count=3,
                                                                             fetcher_process_count=20)
        self.__hierarchy_fetching_event: SyncEvent = Event()
        self.__hierarchy_fetching_event.set()

        self.hierarchy_fetcher = HierarchyFetcher(self.__model, self.__model_lock, self.__hierarchy_fetching_event,
                                                  self.shutdown_event, self.__pid_queue)
        self.saver: SaveInterface = SaveToJSON(self.__cti_dir_path)

        self.passive_thread: PassiveDataThread = PassiveDataThread(shutdown_event, self.__passive_data_fetcher,
                                                                   self.passive_mode_event, self.fetching_passive_data)

        self.hierarchy_thread: HierarchyThread = HierarchyThread(shutdown_event, self.hierarchy_fetcher,
                                                                 self.__error_queue, self.__hierarchy_fetcher_work_queue,
                                                                 self.__hierarchy_fetching_event,
                                                                 self.__fetching_hierarchy)

        self.file_saver_thread: FileSaverThread = FileSaverThread(self.shutdown_event, self.__model, self.saver,
                                                                  self.__model_lock, self.__finished_project_event,
                                                                  self.__file_saver_work_queue)
        self.file_fetch_thread: FileFetcherThread = FileFetcherThread(self.__error_queue, self.__model,
                                                                      self.__model_lock, self.shutdown_event,
                                                                      self.load_path_queue, self.load_event,
                                                                      self.__project_queue, self.visualize_signal)
        self.__status_and_error_thread: GUICommunicationManager = (
            GUICommunicationManager(shutdown_event=self.shutdown_event, error_queue=self.__error_queue,
                                    error_signal=self.__error_signal, passive_mode_event=self.passive_mode_event,
                                    status_queue=self.status_queue, status_signal=self.__status_signal,
                                    fetching_passive_data=self.fetching_passive_data,
                                    active_measurement_active=self.__active_measurement_active,
                                    finished_project_event=self.__finished_project_event, load_event=self.load_event,
                                    cancel_event=self.__cancel_event, restart_event=self.__restart_event,
                                    hierarchy_fetching_event=self.__hierarchy_fetching_event,
                                    fetching_hierarchy=self.__fetching_hierarchy))

    def prepare_threads(self):
        self.__active_mode_fetcher_thread: ActiveFetcherThread = ActiveFetcherThread(self.shutdown_event,
                                                                                     self.__file_saver_work_queue,
                                                                                     self.__cti_dir_path,
                                                                                     self.__model,
                                                                                     self.__model_lock,
                                                                                     self.__source_file_name_queue,
                                                                                     self.__error_queue,
                                                                                     self.__cti_dir_path,
                                                                                     self.__active_measurement_active)

    def start(self):
        print("[app]    started")
        self.prepare_threads()

        self.__status_and_error_thread.start()
        self.passive_thread.start()
        self.file_saver_thread.start()
        self.hierarchy_thread.start()
        self.file_fetch_thread.start()

        self.__active_mode_fetcher_thread.start()


    def stop(self):
        self.shutdown_event.set()
        self.passive_thread.stop()
        self.hierarchy_thread.stop()
        self.file_saver_thread.stop()
        self.__status_and_error_thread.stop()
        self.__active_mode_fetcher_thread.stop()
        self.file_fetch_thread.stop()
        print("[App]    stopped")

    def __get_cti_folder_path(self) -> str:
        path: str = ""
        path += join(os.getcwd().split("cti-engine-prototype")[0])
        return path
