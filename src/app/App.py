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



class AppMeta(type(QApplication), type(AppRequestsInterface)):
    pass

class App(QApplication, AppRequestsInterface, metaclass=AppMeta):
    CTI_DIR_PATH: str = "/common/homes/students/upufw_toroman/cti-engine"  # TODO change
    __DEFAULT_GUI: bool = True

    def __init__(self, start_with_gui: bool = __DEFAULT_GUI, cti_dir_path: str = CTI_DIR_PATH) -> None:
        self.__has_gui: bool = start_with_gui
        self.__model = Model()
        self.__cti_dir_path = cti_dir_path
        self.__passive_data_fetcher: PassiveDataFetcher = PassiveDataFetcher(self.__model)
        self.__hierarchy_fetcher: HierarchyFetcher = HierarchyFetcher(self.__model)
        self.__fetcher: FetcherInterface
        self.__continue_measuring: bool = True
        self.__is_running: bool = True
        if start_with_gui:
            self.__UI: UIInterface = prepare_gui(self)
            self.__UI.execute()
            #Thread(target=self.gui_loop).start()

    """
    def gui_loop(self):
        while True:
            self.__UI.execute()
            time.sleep(0.1)
            """

    def run(self):
        while self.__is_running:
            if self.__continue_measuring:
                Thread(target=self.__passive_fetch).start()
            if self.__model.get_current_working_directory() != "" and not self.__hierarchy_fetcher.is_done: # if there is a new project
                Thread(target=self.__hierarchy_fetcher.update_project).start()
                Thread(target=self.__save_project(self.__model.get_current_working_directory()))

        if self.__has_gui:
            self.__UI.visualize(self.__model)

    def __fetch(self):
        while (self.__continue_measuring):
            self.__continue_measuring = self.__fetcher.update_project()

    def __passive_fetch(self):
        self.__hierarchy_fetcher.is_done = False # hierarchy fetcher will need to be run when project is found
        while self.__continue_measuring:
            self.__continue_measuring = self.__passive_data_fetcher.update_project()

    def __save_project(self, name: str):
        saver: SaveInterface = SaveToJSON()
        stop_time: float = time.time() + 10
        while stop_time > time.time() and self.__continue_measuring:
            project: Project = self.__get_project(name)
            saver.save_project(project)
            time.sleep(3)
            if project.working_dir == self.__model.get_current_working_directory():
                stop_time = time.time() + 10
        saver.save_project(self.__model.get_project_by_name(name))

    def __get_project(self, name: str):
        project: Project = Project("", "")
        try: 
            project = self.__model.get_project_by_name(name)
        except ProjectNotFoundException:
            self.__get_project
        return project
    
    def start_active_measurement(self, source_file_name: str):
        self.__fetcher = ActiveDataFetcher(source_file_name, self.__model, f"{self.CTI_DIR_PATH}/{self.__model.get_project_name}/build")
        self.__fetch()
        if self.__has_gui:
            self.__UI.visualize(self.__model)

    def load_from_directory(self, path: str):
        print(self.__model.current_project.path_to_save)
        self.__fetcher = FileLoader(path, self.__model)
        self.__fetch()
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
