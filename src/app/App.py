from src.fetcher.process_fetcher.ActiveDataFetcher import ActiveDataFetcher
from src.model.Model import Model
from src.fetcher.FetcherInterface import FetcherInterface
from src.fetcher.process_fetcher.PassiveDataFetcher import PassiveDataFetcher
from src.view.AppRequestsInterface import AppRequestsInterface
from src.view.GUI.MainWindow import MainWindow
from src.view.UIInterface import UIInterface


class App(AppRequestsInterface):
    CTI_DIR_PATH: str = "usr/cti-engine"  # TODO change

    def __init__(self, active_mode: bool, start_with_gui: bool, cti_dir_path: str = CTI_DIR_PATH) -> None:
        self.__active_mode = active_mode
        if start_with_gui:
            self.__UI: UIInterface = MainWindow()
        self.__model = Model()
        self.__cti_dir_path = cti_dir_path

    def run(self):
        if self.__active_mode:
            self.run_active_measurement()
        else:
            self.run_passive_mode()

    def run_passive_mode(self) -> None:
        self.__passive_fetcher: FetcherInterface = PassiveDataFetcher(
            self.__model, self.__cti_dir_path)
        continue_measuring: bool = True
        while (continue_measuring):
            self.__UI.update_statusbar("measuring")
            continue_measuring = self.__passive_fetcher.update_project()
            # TODO fetch click-commands
        self.__UI.update_statusbar("preparing data")
        self.finish_off_passive_measurement()
        self.__UI.visualize(self.__model)

    def finish_off_passive_measurement(self) -> None:
        pass

    def run_active_measurement(self, source_file_name: str):
        self.__active_fetcher: FetcherInterface = ActiveDataFetcher(
            source_file_name, self.__model, self.__cti_dir_path)
