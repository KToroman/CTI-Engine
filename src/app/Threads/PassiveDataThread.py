from threading import Event, Thread

from src.fetcher.process_fetcher.PassiveDataFetcher import PassiveDataFetcher


class PassiveDataThread:
    def __init__(self, data_fetcher: PassiveDataFetcher, collect_data_passive: Event, found_project: Event):
        self.__thread: Thread = None
        self.__shutdown: Event = Event()
        self.__shutdown.clear()
        self.__collect_data_passive = collect_data_passive
        self.__found_project = found_project
        self.__data_fetcher = data_fetcher

    def __run(self):
        while not self.__shutdown.is_set():
            if self.__collect_data_passive.is_set():
                if self.__data_fetcher.update_project():
                    self.__found_project.set()
                else:
                    self.__found_project.clear()

    def start(self):
        print("[PassiveDataThread]    started")
        self.__thread = Thread(target=self.__run)
        self.__data_fetcher.start()
        self.__thread.start()

    def stop(self):
        print("[PassiveDataThread]  stop signal sent")
        self.__shutdown.set()
        self.__data_fetcher.stop()
        if self.__thread.is_alive():
            self.__thread.join()
        print("[PassiveDataThread]  stopped")
