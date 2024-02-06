import click

from src.fetcher.file_fetcher.FileLoader import FileLoader
from src.fetcher.hierarchy_fetcher.HierarchyFetcher import HierarchyFetcher
from src.fetcher.process_fetcher.ActiveDataFetcher import ActiveDataFetcher
from src.model.Model import Model
from src.fetcher.FetcherInterface import FetcherInterface
from src.fetcher.process_fetcher.PassiveDataFetcher import PassiveDataFetcher
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
        self.__fetcher: FetcherInterface = PassiveDataFetcher(self.__model, self.__cti_dir_path)
        self.__cancel_measurement: bool = False


    def run(self):
        self.__continue_measuring: bool = True
        while self.__continue_measuring and not self.__cancel_measurement:
            self.__continue_measuring = self.__fetcher.update_project()
            if not self.__model.projects:
                self.__fetcher = PassiveDataFetcher(self.__model, self.__cti_dir_path)
                self.__continue_measuring = True
        if self.__has_gui:
            self.__UI.visualize(self.__model)


    
    @click.command()
    @click.option('--source_file_name', prompt='Enter a filepath', help = 'filepath for active measurement')
    @click.argument('source_file_name')
    @click.argument('path')
    def start_active_measurement_command(self, source_file_name: str, path: str):
        app = App(False)
        app.load_from_directory(path)
        app.start_active_measurement()
    
    def start_active_measurement(self, source_file_name: str):
        self.__fetcher: FetcherInterface = ActiveDataFetcher(
            source_file_name, self.__model, self.__cti_dir_path)
        self.run()
        if self.__has_gui:
            self.__UI.visualize(self.__model)

    @click.command()
    @click.argument('path')
    def load_from_directory_command(self, path: str):
        app = App(False)
        app.load_from_directory()
    
    def load_from_directory(self, path: str):
        self.__fetcher = FileLoader(path, self.__model)
        self.run()


    @click.command("quit")
    def quit_application_command(self) -> bool:
        pass
    
    def quit_application(self) -> bool:
        pass

    @click.command("quit_measurement")
    def quit_measurement_command(self) -> bool:
        pass
    
    @click.command("quit_measurement")
    def quit_measurement(self) -> bool:
        self.__cancel_measurement = True
        return True
    
    @click.command("restart_measurement")
    def restart_measurement_command(self) -> bool:
        pass

    def restart_measurement(self) -> bool:
        self.__cancel_measurement = False

    @click.group()
    def group():
        pass

    group.add_command(restart_measurement_command)
    group.add_command(quit_measurement_command)
    group.add_command(quit_application_command, "quit")
    group.add_command(load_from_directory_command)
    group.add_command(start_active_measurement_command)


if __name__ == "__main__":
    app = App(False)
    app.load_from_directory("projects/CTI_ENGINE_SAVE 69 1706886699")