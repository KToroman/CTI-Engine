import os
import time
from os.path import join
from threading import Event, Lock, Thread
from typing import List

from PyQt5.QtWidgets import QApplication
from colorama import Fore

from src.app.App import AppMeta
from src.app.Threads.FileSaverThread import FileSaverThread
from src.app.Threads.HierarchyThread import HierarchyThread
from src.app.Threads.PassiveDataThread import PassiveDataThread
from src.fetcher.hierarchy_fetcher.HierarchyFetcher import HierarchyFetcher
from src.fetcher.process_fetcher.PassiveDataFetcher import PassiveDataFetcher
from src.model.Model import Model
from src.model.core.StatusSettings import StatusSettings
from src.saving.SaveInterface import SaveInterface
from src.saving.SaveToJSON import SaveToJSON
from src.view.AppRequestsInterface import AppRequestsInterface
from src.view.UIInterface import UIInterface


class SecondApp(QApplication, AppRequestsInterface, metaclass=AppMeta):

    def __init__(self, argv: List[str], ui: UIInterface, start_with_gui: bool, active_mode_event, passive_mode_event,
                 load_event, load_path_queue, active_mode_queue, visualize_event: Event, error_queue):
        super().__init__(argv)
        self.__model_lock: Lock = Lock()

        self.active_mode_event = active_mode_event
        self.passive_mode_event = passive_mode_event
        self.passive_mode_event.set()

        self.load_event = load_event
        self.load_path_queue = load_path_queue
        self.active_mode_queue = active_mode_queue
        self.error_queue = error_queue
        self.visualize_event = visualize_event

        self.__cti_dir_path = self.__get_cti_folder_path()

        self.__ui = ui

        self.fetching_passive_data = Event()

        self.hast_gui = start_with_gui

        self.__model = Model()

        self.__passive_data_fetcher: PassiveDataFetcher = PassiveDataFetcher(self.__model, self.__model_lock)
        self.hierarchy_fetcher = HierarchyFetcher(self.__model, self.__model_lock)
        self.saver: SaveInterface = SaveToJSON(self.__cti_dir_path)

        self.passive_thread: PassiveDataThread = PassiveDataThread(self.__passive_data_fetcher,
                                                                   self.passive_mode_event, self.fetching_passive_data)

        self.hierarchy_thread: HierarchyThread = HierarchyThread(self.hierarchy_fetcher, self.error_queue)

        self.file_saver_thread: FileSaverThread = FileSaverThread(self.__model, self.saver, self.__model_lock)

        self.app_thread = Thread(target=self.run)
        self.is_running = True
        self.curr_working_dir: str = ""

    def start(self):
        print("[app]    started")
        self.passive_thread.start()
        self.file_saver_thread.start()
        self.hierarchy_thread.start()
        self.app_thread.start()

    def stop(self):
        print("[app]    stop signal sent")
        self.hierarchy_thread.stop()
        self.passive_thread.stop()
        self.file_saver_thread.stop()

        self.is_running = False
        self.app_thread.join()
        print("[app]    stopped")

    def run(self):
        waiting_for_hierarchy = False
        waiting_for_hierarchy_project = ""
        while self.is_running:
            if self.fetching_passive_data.is_set():
                if self.curr_working_dir != self.__get_current_project_dir():
                    if self.curr_working_dir != "":
                        if self.hierarchy_thread.is_done_bool():
                            if waiting_for_hierarchy_project == "":
                                waiting_for_hierarchy_project = self.curr_working_dir
                            self.file_saver_thread.delete_work(waiting_for_hierarchy_project)
                            self.visualize_event.is_set()
                            print(Fore.LIGHTGREEN_EX + "[App]    project finished" + Fore.RESET)
                            waiting_for_hierarchy = False
                            waiting_for_hierarchy_project = ""
                        else:
                            waiting_for_hierarchy = True
                            waiting_for_hierarchy_project = self.curr_working_dir
                    if self.curr_working_dir != self.__get_current_project_dir():
                        self.curr_working_dir = self.__get_current_project_dir()
                        self.file_saver_thread.add_work(self.curr_working_dir)
                        self.hierarchy_thread.add_work(self.curr_working_dir)
            else:
                if self.hierarchy_thread.is_done_bool():
                    if waiting_for_hierarchy_project == "":
                        waiting_for_hierarchy_project = self.curr_working_dir
                    self.file_saver_thread.delete_work(waiting_for_hierarchy_project)
                    self.visualize_event.is_set()
                    print(Fore.LIGHTGREEN_EX + "[App]    project finished" + Fore.RESET)
                    waiting_for_hierarchy = False
                    waiting_for_hierarchy_project = ""
            if waiting_for_hierarchy:
                print("[App]    waiting for hierarchy")
                if self.hierarchy_thread.is_done_bool():
                    if waiting_for_hierarchy_project == "":
                        waiting_for_hierarchy_project = self.curr_working_dir
                    self.file_saver_thread.delete_work(waiting_for_hierarchy_project)
                    self.visualize_event.is_set()
                    print(Fore.LIGHTGREEN_EX + "[App]    project finished" + Fore.RESET)
                    waiting_for_hierarchy = False
                    waiting_for_hierarchy_project = ""

            if self.hast_gui:
                self.__update_status()

    def __get_current_project_dir(self) -> str:
        with self.__model_lock:
            return self.__model.get_current_working_directory()

    def __update_status(self) -> None:
        if self.active_mode_event.is_set():
            self.__ui.status_queue.put(StatusSettings.MEASURING)
            return
        if self.load_event.is_set():
            self.__ui.status_queue.put(StatusSettings.LOADING)
            return
        if self.passive_mode_event.is_set():
            if not self.hierarchy_thread.is_done_bool():
                self.__ui.status_queue.put(StatusSettings.MEASURING)
                return
            if self.fetching_passive_data:
                self.__ui.status_queue.put(StatusSettings.MEASURING)
            else:
                self.__ui.status_queue.put(StatusSettings.SEARCHING)
            return
        self.__ui.status_queue.put(StatusSettings.WAITING)

    def __get_cti_folder_path(self) -> str:
        path: str = ""
        path += join(os.getcwd().split("cti-engine-prototype")[0])
        return path
