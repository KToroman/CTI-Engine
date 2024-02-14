from multiprocessing import Process, Queue, Event
import os
import sys
import time
from threading import Thread
from os.path import join
from typing import List

import click
from src.exceptions.ProjectNotFoundException import ProjectNotFoundException

from src.fetcher.file_fetcher.FileLoader import FileLoader
from src.fetcher.hierarchy_fetcher.HierarchyFetcher import HierarchyFetcher
from src.fetcher.process_fetcher.ActiveDataFetcher import ActiveDataFetcher
from src.model.Model import Model
from src.fetcher.FetcherInterface import FetcherInterface
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

    def __init__(self, start_with_gui: bool = __DEFAULT_GUI) -> None:
        self.__has_gui: bool = start_with_gui

        self.__model = Model()
        self.__cti_dir_path = self.__get_cti_folder_path()
        self.__passive_data_fetcher: PassiveDataFetcher = PassiveDataFetcher(self.__model)
        self.__hierarchy_fetcher: HierarchyFetcher
        self.__fetcher: FetcherInterface
        self.__curr_project_name: str = ""

        # Events for GUI
        self.shutdown_event = Event()
        self.active_mode_event = Event()
        self.passive_mode_event = Event()
        self.passive_mode_event.set()
        self.load_event = Event()

        # Queues for GUI messages
        self.load_path_queue: Queue = Queue(1)
        self.active_mode_queue: Queue = Queue(1)
        self.error_queue: Queue = Queue(5)

        # set up GUI
        if start_with_gui:
            self.__UI: UIInterface = prepare_gui(self, self.load_path_queue, self.active_mode_queue, self.error_queue)
        super(App, self).__init__([])



    def run(self) -> None:
        self.__curr_project_name = self.__model.get_current_working_directory()
        while not self.shutdown_event.is_set():
            if self.__has_gui:
                self.__update_GUI()
            if self.passive_mode_event.is_set():
                self.__fetch_passive()
            if self.load_event.is_set():
                self.__fetch_load()
            if self.active_mode_event.is_set():
                self.__fetch_active()

    def __update_GUI(self) -> None:
        if self.__visualize:
            self.__UI.visualize.set()
            self.__UI.model_queue.put(self.__model)
            self.__UI.status_queue.put(StatusSettings.FINISHED)
            self.__visualize = False

    def __get_cti_folder_path(self) -> str:
        path: str = ""
        path += join(os.getcwd().split("cti-engine-prototype")[0])
        return path
  
    def __hierarchy_fetch(self, hierarchy_fetcher: HierarchyFetcher) -> None:
        __hierarchy_needed: bool = True
        while __hierarchy_needed:
            try:
                __hierarchy_needed = hierarchy_fetcher.update_project()
            except FileNotFoundError:
                self.error_list.append(FileNotFoundError("could not find the compile-commands.json file"))
                self.__hierarchy_needed = False
                self.__hierarchy_fetcher.is_done = True
                return

    def __fetch(self) -> None:
        if self.__has_gui:
            self.__UI.update_statusbar(StatusSettings.MEASURING)
        while self.__continue_fetching:
            self.__UI.execute()
            self.__continue_fetching = self.__fetcher.update_project()
        if self.__has_gui:
            self.__UI.update_statusbar(StatusSettings.FINISHED)

    def __passive_fetch(self) -> None:
        # hierarchy fetcher will need to be run when project is found
        self.__passive_fetching_on = True
        while self.__continue_measuring:
            self.__found_project = self.__passive_data_fetcher.update_project()
        self.__passive_fetching_on = False

    def __save_project(self, hierarchy_fetcher: HierarchyFetcher) -> None:
        name: str = self.__model.get_current_working_directory()
        saver: SaveInterface = SaveToJSON(self.__cti_dir_path)
        while (self.__found_project and (
                name == self.__model.get_current_working_directory())) or not hierarchy_fetcher.is_done:
            # if the current project is still being watched or the hierarchy is not yet completed
            project: Project = self.__get_project(name)
            saver.save_project(project)
            time.sleep(3)
        saver.save_project(self.__model.get_project_by_name(name))
        if self.__has_gui:
            self.__visualize = True
        print("saver exit")

    def __get_project(self, name: str) -> Project:
        project: Project = Project("", "")
        try:
            project = self.__model.get_project_by_name(name)
        except ProjectNotFoundException:
            self.__get_project(name)
        return project

    def start_active_measurement(self, source_file_name: str) -> None:   
        self.__continue_measuring = False
        self.__continue_fetching = True
        self.__fetcher = ActiveDataFetcher(source_file_name, self.__model,
                                           f"{self.__cti_dir_path}/{self.__model.get_project_name}/build")
        self.__fetch()
        if self.__has_gui:
            self.__UI.visualize(self.__model)

    def load_from_directory(self, path: str) -> None:
        self.__continue_measuring = False
        self.__continue_fetching = True
        self.__fetcher = FileLoader(path, self.__model)
        self.__fetch()
        self.__curr_project_name = self.__model.get_project_name()
        if self.__has_gui:
            self.__UI.visualize(self.__model)

    def quit_application(self) -> bool:
        self.__is_running = False
        return not self.__is_running

    def restart_measurement(self):
        self.__continue_measuring = True
        self.run()

    def quit_measurement(self):
        self.__continue_measuring = False
