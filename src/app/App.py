import sys
import time
from threading import Thread

import click
from exceptions.ProjectNotFoundException import ProjectNotFoundException

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


class App(AppRequestsInterface):
    CTI_DIR_PATH: str = "usr/cti-engine"  # TODO change
    DEFAULT_GUI: bool = True

    def __init__(self, start_with_gui: bool = DEFAULT_GUI, cti_dir_path: str = CTI_DIR_PATH) -> None:
        if start_with_gui:
            self.__UI: UIInterface = prepare_gui()
        self.__has_gui: bool = start_with_gui
        self.__model = Model()
        self.__cti_dir_path = cti_dir_path
        self.__passive_data_fetcher: FetcherInterface = PassiveDataFetcher(self.__model)
        self.__hierarchy: FetcherInterface = HierarchyFetcher(self.__model)
        self.__save: SaveInterface = SaveToJSON()

        self.__cancel_measurement: bool = False
        self.__is_measuring: bool = False
        self.__continue_measuring: bool = True
        self.__running_passive_fetcher: bool = False

        self.is_running: bool = True

    def run(self):
        while self.is_running:
            if self.__continue_measuring and not self.__running_passive_fetcher:
                self.__run_passive_measurement()
        if self.__has_gui:
            self.__UI.visualize(self.__model)

    def __run_passive_measurement(self):
        Thread(target=self.__passive_measurement()).start()
        self.__running_passive_fetcher = True

    def __passive_measurement(self):
        curr_project_name: str = ""
        if self.__model.get_current_project() is not None:
            curr_project_name = self.__model.get_current_working_directory()
        while not self.__cancel_measurement:
            self.__is_measuring = self.__passive_data_fetcher.update_project()
            if self.__model.current_project is None:
                time.sleep(0.0001)
                continue
            if curr_project_name != self.__model.get_current_working_directory():
                Thread(target=self.__make_hierarchy).start()
                curr_project_name = self.__model.get_current_working_directory()
                Thread(target=self.__save_project, args=[curr_project_name]).start()
            time.sleep(0.01)
        self.__running_passive_fetcher = False

    def __make_hierarchy(self):
        self.__hierarchy.update_project()

    def __save_project(self, name: str):
        saver: SaveInterface = SaveToJSON()
        stop_time: float = time.time() + 10
        print("saver opend")
        while stop_time > time.time() and not self.__cancel_measurement:
            project: Project = self.__get_project(name)
            saver.save_project(project)
            time.sleep(3)
            if project.working_dir == self.__model.get_current_working_directory():
                stop_time = time.time() + 10
        saver.save_project(self.__model.get_project_by_name(name))
        print("saver colsed")

    def __get_project(self, name: str):
        project: Project = Project("", "")
        try: 
            project = self.__model.get_project_by_name(name)
        except ProjectNotFoundException:
            self.__get_project
        return project
        

    @click.command()
    @click.option('--source_file_name', prompt='Enter a filepath', help='filepath for active measurement')
    @click.argument('source_file_name')
    @click.argument('path')
    def start_active_measurement_command(self, source_file_name: str, path: str):
        app = App(False)
        app.load_from_directory(path)
        app.start_active_measurement(source_file_name)

    def start_active_measurement(self, source_file_name: str):
        self.__fetcher: FetcherInterface = ActiveDataFetcher(
            source_file_name=source_file_name, model=self.__model, build_dir_path = self.CTI_DIR_PATH)
        self.run()
        if self.__has_gui:
            self.__UI.visualize(self.__model)

    @click.command()
    @click.argument('path')
    def load_from_directory_command(self, path: str):
        app = App(False)
        app.load_from_directory(path)

    def load_from_directory(self, path: str):
        self.__fetcher = FileLoader(path, self.__model)
        self.run()

    def quit_application(self) -> bool:
        self.is_running = False
        return self.is_running

    @click.command("quit_measurement")
    def quit_measurement(self) -> bool:
        self.__cancel_measurement = True
        return True

    def restart_measurement(self):
        self.__cancel_measurement = False
        self.run()

    @click.group()
    def group():
        pass

    group.add_command(load_from_directory_command)
    group.add_command(start_active_measurement_command)


if __name__ == "__main__":
    app = App(False)
    app.load_from_directory("projects/CTI_ENGINE_SAVE 69 1706886699")
