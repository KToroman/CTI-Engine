from multiprocessing import Process
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
        self.__hierarchy_fetcher: HierarchyFetcher = HierarchyFetcher(self.__model)
        self.__fetcher: FetcherInterface
        self.__passive_fetching: bool = True
        self.__is_running: bool = True
        self.__curr_project_name: str
        self.__visualize = False
        self.__last_change: int = 0
        self.__curr_status: StatusSettings = StatusSettings.WAITING
        self.__load_project: bool = False
        self.__path_to_load: str = ""
        self.__active_fetching_bool: bool = False
        self.__curr_source_file_name: str = ""
        self.__continue_fetching: bool = False
        if start_with_gui:
            self.__UI: UIInterface = prepare_gui(self)
        super(App, self).__init__([])

        self.__passive_fetching_on = False
        self.error_list: List[Exception] = list()
        self.__curr_project_name: str = ""

    def __get_cti_folder_path(self) -> str:
        path: str = ""
        path += join(os.getcwd().split("cti-engine-prototype")[0])
        return path

    def run(self) -> None:
        self.__curr_project_name = self.__model.get_current_working_directory()
        while self.__is_running:
            if self.__has_gui:
                self.__gui_handling()
            if self.__passive_fetching:
                self.__passive_measuring()
            if self.__load_project:
                Thread(target=self.__load).start()
            if self.__active_fetching_bool:
                Thread(target=self.__active_fetching).start()
        print("done running")

        if self.__has_gui:
            print("ok... not running i guess?")
            self.__curr_status = StatusSettings.FINISHED
            self.__last_change = time.time() + 10
            self.__UI.visualize(self.__model)

    def __gui_handling(self):
        self.__UI.execute()
        self.__UI.update_statusbar(self.__curr_status)
        if self.__visualize:
            self.__curr_status = StatusSettings.FINISHED
            self.__last_change = time.time() + 10
            self.__UI.visualize(self.__model)
            self.__visualize = False
        if self.__last_change <= time.time():
            self.__curr_status = StatusSettings.WAITING
            self.__last_change = time.time() + 10
        for error in self.error_list:
            self.__UI.deploy_error(error)
            self.error_list.remove(error)

    def __passive_measuring(self):
        if not self.__passive_fetching_on:
            Thread(target=self.__passive_fetch).start()
        if self.__curr_project_name != self.__model.get_current_working_directory():
            hierarchy_fetcher = HierarchyFetcher(self.__model)
            self.__curr_project_name = self.__model.get_current_working_directory()
            Thread(target=self.__hierarchy_fetch, args=[hierarchy_fetcher]).start()
            Thread(target=self.__save_project, args=[hierarchy_fetcher]).start()
            self.__curr_status = StatusSettings.MEASURING
            self.__last_change = time.time() + 10

    def __hierarchy_fetch(self, hierarchy_fetcher: HierarchyFetcher) -> None:
        __hierarchy_needed: bool = True
        while __hierarchy_needed:
            try:
                __hierarchy_needed = hierarchy_fetcher.update_project()
            except FileNotFoundError:
                self.__error_handling()
                self.error_list.append(FileNotFoundError("could not find the compile-commands.json file"))
                self.__hierarchy_needed = False
                self.__hierarchy_fetcher.is_done = True
                return

    def __fetch(self) -> None:
        self.__curr_status = StatusSettings.MEASURING
        self.__last_change = time.time() + 10
        while self.__continue_fetching:
            try:
                self.__continue_fetching = self.__fetcher.update_project()
                self.__curr_status = StatusSettings.MEASURING
                self.__last_change = time.time() + 10
            except FileNotFoundError as e:
                self.__error_handling()
                self.error_list.append(e)
                self.__curr_project_name = self.__model.get_current_working_directory()
                return
        self.__curr_project_name = self.__model.get_current_working_directory()
        self.__visualize = True
        self.__curr_status = StatusSettings.FINISHED
        self.__last_change = time.time() + 10

    def __error_handling(self):
        self.__curr_status = StatusSettings.FAILED
        self.__last_change = time.time() + 20

    def __passive_fetch(self) -> None:
        # hierarchy fetcher will need to be run when project is found
        self.__passive_fetching_on = True
        while self.__passive_fetching:
            self.__found_project = self.__passive_data_fetcher.update_project()
        self.__passive_fetching_on = False

    def __save_project(self, hierarchy_fetcher: HierarchyFetcher) -> None:
        name: str = self.__model.get_current_working_directory()
        saver: SaveInterface = SaveToJSON(self.__cti_dir_path)
        while (self.__found_project and (
                name == self.__model.get_current_working_directory())) or not hierarchy_fetcher.is_done:
            # if the current project is still being watched or the hierarchy is not yet completed
            self.__curr_status = StatusSettings.MEASURING
            self.__last_change = time.time() + 10
            project: Project = self.__get_project(name)
            saver.save_project(project)
            time.sleep(3)
        saver.save_project(self.__model.get_project_by_name(name))
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
        self.__active_fetching_bool = True
        self.__curr_source_file_name = source_file_name

    def __active_fetching(self):
        self.__active_fetching_bool = False
        self.__passive_fetching = False
        self.__continue_fetching = True
        self.__fetcher = ActiveDataFetcher(self.__curr_source_file_name, self.__model,
                                           f"{self.__cti_dir_path}/{self.__model.get_project_name}/build")
        self.__fetch()

    def load_from_directory(self, path: str) -> None:
        self.__path_to_load = path
        self.__load_project = True

    def __load(self):
        self.__load_project = False
        self.__passive_fetching = False
        self.__continue_fetching = True
        self.__fetcher = FileLoader(self.__path_to_load, self.__model)
        self.__fetch()


    def quit_application(self) -> bool:
        self.__is_running = False
        self.__passive_fetching = False
        self.__continue_fetching = False
        return not self.__is_running

    def restart_measurement(self):
        self.__passive_fetching = True

    def quit_measurement(self):
        self.__passive_fetching = False
        self.__continue_fetching = False
