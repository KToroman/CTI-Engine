import threading
from multiprocessing import Process
import os
import time
from threading import Thread
from os.path import join
from typing import List
from multiprocessing import Process

from src.exceptions.ProjectNotFoundException import ProjectNotFoundException

from src.fetcher.file_fetcher.FileLoader import FileLoader
from src.fetcher.hierarchy_fetcher.HierarchyFetcher import HierarchyFetcher
from src.fetcher.process_fetcher.ActiveDataFetcher import ActiveDataFetcher
from src.model.Model import Model
from src.fetcher.process_fetcher.PassiveDataFetcher import PassiveDataFetcher
from src.model.core.Project import Project
from src.saving.SaveInterface import SaveInterface
from src.saving.SaveToJSON import SaveToJSON
from src.view.AppRequestsInterface import AppRequestsInterface
from src.view.GUI.prepare_gui import prepare_gui
from src.view.UIInterface import UIInterface
from PyQt5.QtWidgets import QApplication

from src.model.core.StatusSettings import StatusSettings


class AppMeta(type(QApplication), type(AppRequestsInterface)):
    pass


class App(QApplication, AppRequestsInterface, metaclass=AppMeta):
    __DEFAULT_GUI: bool = True

    def __init__(self, shutdown_event, active_mode_event, passive_mode_event, load_event, load_path_queue,
                 active_mode_queue, model_queue, error_queue, visualize_event, status_queue,
                 start_with_gui: bool = __DEFAULT_GUI) -> None:
        self.shutdown_event = shutdown_event
        self.active_mode_event = active_mode_event
        self.passive_mode_event = passive_mode_event
        self.load_event = load_event
        self.load_path_queue = load_path_queue
        self.active_mode_queue = active_mode_queue

        self.__has_gui: bool = start_with_gui
        self.__model_lock: threading.Lock = threading.Lock()
        self.__model = Model()
        self.__cti_dir_path = self.__get_cti_folder_path()
        self.__passive_data_fetcher: PassiveDataFetcher = PassiveDataFetcher(self.__model, self.__model_lock)
        self.__curr_project_name: str = ""
        self.__last_found_processes: float = time.time()
        self.__hierarchy_fetcher_bool: bool = True
        self.__visualize: bool = True

        self.__watching_processes: bool = False
        self.__found_processes: bool = False

        # set up GUI
        if start_with_gui:
            pass

        super(App, self).__init__([])

    def set_ui(self, ui: UIInterface):
        self.__UI = ui

    def start(self):
        pass

    def stop(self):
        pass
    def run(self) -> None:
        self.__curr_project_name = self.__model.get_current_working_directory()
        while not self.shutdown_event.is_set():
            if self.__has_gui:
                self.__update_status()
                self.__update_GUI()
            if self.passive_mode_event.is_set():
                self.__fetch_passive()
            if self.load_event.is_set():
                self.__fetch_load()
            if self.active_mode_event.is_set():
                self.__fetch_active()

    def __update_GUI(self) -> None:
        if self.__visualize:
            self.__UI.model_queue.put(self.__model)
            self.__UI.visualize_event.set()
            self.__visualize = False

    def __update_status(self) -> None:
        if self.active_mode_event.is_set():
            self.__UI.status_queue.put(StatusSettings.MEASURING)
            return
        if self.load_event.is_set():
            self.__UI.status_queue.put(StatusSettings.LOADING)
            return
        if self.passive_mode_event.is_set():
            if not self.__hierarchy_fetcher_bool:
                self.__UI.status_queue.put(StatusSettings.MEASURING)
                return
            if time.time() > self.__last_found_processes + 10:
                self.__UI.status_queue.put(StatusSettings.MEASURING)
            else:
                self.__UI.status_queue.put(StatusSettings.SEARCHING)
            return
        self.__UI.status_queue.put(StatusSettings.WAITING)


    def __fetch_passive(self):
        if not self.__watching_processes:
            Thread(target=self.__watch_processes).start()
        if self.__curr_project_name != self.__get_current_project_dir():
            # set up hierarchy fetching
            with self.__model_lock:
                hierarchy_fetcher = HierarchyFetcher(self.__model.current_project, self.__model_lock)
                self.__curr_project_name = self.__model.get_current_working_directory()
            # start hierarchy fetching and saving threads
            Thread(target=self.__hierarchy_fetch, args=[hierarchy_fetcher]).start()
            Thread(target=self.__save_project, args=[hierarchy_fetcher]).start()
            # TODO Thread als member
            self.__last_found_processes = time.time()

    def __get_current_project_dir(self) -> str:
        with self.__model_lock:
            return self.__model.get_current_working_directory()

    def __watch_processes(self):
        self.__watching_processes = True
        while self.passive_mode_event.is_set():
            self.__found_processes = self.__passive_data_fetcher.update_project()
            if self.__found_processes:
                self.__last_found_processes = time.time()
        self.__watching_processes = False

    def __hierarchy_fetch(self, hierarchy_fetcher: HierarchyFetcher) -> None:
        self.__hierarchy_fetcher_bool = False
        __hierarchy_needed: bool = True
        while __hierarchy_needed:
            try:
                __hierarchy_needed = hierarchy_fetcher.update_project()
            except FileNotFoundError:
                self.__UI.error_queue.put(FileNotFoundError("could not find the compile-commands.json file"))
                self.__hierarchy_fetcher_bool = True
                return
        waiting_for_passive: bool = True
        while waiting_for_passive:
            waiting_for_passive = (self.__last_found_processes + 15 < time.time() and
                                   self.__curr_project_name == hierarchy_fetcher.project.working_dir)
            if not waiting_for_passive:
                self.__visualize = True

    def __fetch_load(self) -> None:
        if not self.load_path_queue.empty():
            path: str = self.load_path_queue.get(block=True, timeout=0.05)
            self.__file_loader = FileLoader(path, self.__model, self.__model_lock)
            Thread(target=self.__load_project_from_file).start()

    def __load_project_from_file(self):
        try:
            self.__file_loader.update_project()

        except FileNotFoundError:
            self.__UI.error_queue.put(FileNotFoundError("could not find the project file"))
            return
        self.load_event.clear()
        self.__visualize = True

    def __fetch_active(self):
        if not self.active_mode_queue.empty():
            source_file_name: str = self.active_mode_queue.get(block=True, timeout=0.05)
            self.__active_fetcher = ActiveDataFetcher(source_file_name, self.__model, self.__cti_dir_path,
                                                      self.__model_lock)
            Thread(target=self.__start_active_mode).start()
            self.active_mode_event.clear()

    def __start_active_mode(self):
        continue_active_mode: bool = True
        while continue_active_mode:
            continue_active_mode = self.__active_fetcher.update_project()
        self.__visualize = True

    def __get_cti_folder_path(self) -> str:
        path: str = ""
        path += join(os.getcwd().split("cti-engine-prototype")[0])
        return path

    def __save_project(self, hierarchy_fetcher: HierarchyFetcher) -> None:
        with self.__model_lock:
            name: str = self.__model.get_current_working_directory()
        saver: SaveInterface = SaveToJSON(self.__cti_dir_path)
        while (self.__found_processes and self.__current_project_name_check(name)) or not hierarchy_fetcher.is_done:
            # if the current project is still being watched or the hierarchy is not yet completed
            project: Project = self.__get_project(name)
            saver.save_project(project)
            time.sleep(3)

        saver.save_project(self.__get_project(name))
        if self.__has_gui:
            self.__visualize = True
        print("saver exit")

    def __current_project_name_check(self, name: str) -> bool:
        with self.__model_lock:
            if name == self.__model.get_current_working_directory():
                return True
            return False

    def __get_project(self, name: str) -> Project:
        project: Project = Project("", "")
        try:
            with self.__model_lock:
                project = self.__model.get_project_by_name(name)
        except ProjectNotFoundException:
            self.__get_project(name)
        return project
