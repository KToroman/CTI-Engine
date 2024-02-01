from fetcher.FetcherInterface import FetcherInterface
from fetcher.process_fetcher.PassiveDataFetcher import PassiveDataFetcher
from src.view.AppRequestsInterface import AppRequestsInterface


class App(AppRequestsInterface):
    def __init__(self, active_mode: bool) -> None:
        self.__active_mode = active_mode

    def run(self):
        if self.__active_mode:
            self.run_active_mode()
        else:
            self.run_passive_mode()

    def run_passive_mode(self):
        self.__passive_fetcher: FetcherInterface = PassiveDataFetcher()
        continue_measuring: bool = True
        while (continue_measuring):
            continue_measuring = PassiveDataFetcher.update_project()
            # TODO fetch click-commands
        self.finish_off_passive_measurement()
