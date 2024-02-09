from multiprocessing import Process
import os
import sys
import time
from threading import Thread
from os.path import join


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

from src.view.GUI.Visuals.StatusSettings import StatusSettings



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
        self.__continue_measuring: bool = True
        self.__is_running: bool = True
        if start_with_gui:
            self.__UI: UIInterface = prepare_gui(self)

    def __get_cti_folder_path(self) -> str:
        path: str = ""
        path += join(os.getcwd().split("cti-engine-prototype")[0])
        return path

    def run(self) -> None:
        while self.__is_running:
            self.__UI.execute()
            if self.__continue_measuring:
                if self.__has_gui:
                    self.__UI.update_statusbar(StatusSettings.MEASURING)
                Thread(target=self.__passive_fetch).start()
            if self.__model.get_current_working_directory() != "" and not self.__hierarchy_fetcher.is_done: # if there is a new project
                self.__hierarchy_needed = True
                Thread(target=self.__hierarchy_fetch).start()
                Thread(target=self.__save_project).start()
        print("done running")
        if self.__has_gui:
            self.__UI.update_statusbar(StatusSettings.FINISHED)
            self.__UI.visualize(self.__model)

    def __hierarchy_fetch(self) -> None:
        while self.__hierarchy_needed:
            try:
                self.__hierarchy_needed = self.__hierarchy_fetcher.update_project()
            except FileNotFoundError:
                self.__UI.deploy_error(FileNotFoundError("could not find the compile-commands.json file"))
                self.__hierarchy_needed = False

    def __fetch(self) -> None:
        if self.__has_gui:
            self.__UI.update_statusbar(StatusSettings.MEASURING)
        while (self.__continue_measuring):
            self.__continue_measuring = self.__fetcher.update_project()
        if self.__has_gui:
            self.__UI.update_statusbar(StatusSettings.FINISHED)

    def __passive_fetch(self) -> None:
        self.__hierarchy_fetcher.is_done = False 
        # hierarchy fetcher will need to be run when project is found
        found_project: bool = False 
        while self.__continue_measuring:
            found_project = self.__passive_data_fetcher.update_project()
        if found_project:
            print("done with project")
            self.__UI.visualize(self.__model)

    def __save_project(self) -> None:
        name: str = self.__model.get_current_working_directory()
        saver: SaveInterface = SaveToJSON(self.__cti_dir_path)
        stop_time: float = time.time() + 10
        while stop_time > time.time() and self.__continue_measuring:
            project: Project = self.__get_project(name)
            saver.save_project(project)
            time.sleep(3)
            if project.working_dir == self.__model.get_current_working_directory():
                stop_time = time.time() + 10
        saver.save_project(self.__model.get_project_by_name(name))
        print("saver exit")

    def __get_project(self, name: str) -> Project:
        project: Project = Project("", "")
        try: 
            project = self.__model.get_project_by_name(name)
        except ProjectNotFoundException:
            self.__get_project
        return project
    
    def start_active_measurement(self, source_file_name: str) -> None:
        self.__fetcher = ActiveDataFetcher(source_file_name, self.__model, f"{self.__cti_dir_path}/{self.__model.get_project_name}/build")
        self.__fetch()
        if self.__has_gui:
            self.__UI.visualize(self.__model)

    def load_from_directory(self, path: str) -> None:
        print(self.__model.current_project.path_to_save)
        self.__fetcher = FileLoader(path, self.__model)
        self.__fetch()
        self.__hierarchy_fetcher.is_done = True
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
