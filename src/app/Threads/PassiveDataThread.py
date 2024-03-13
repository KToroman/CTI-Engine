from multiprocessing.synchronize import Event as SyncEvent

from threading import Thread

from src.fetcher.process_fetcher.PassiveDataFetcher import PassiveDataFetcher


class PassiveDataThread:
    def __init__(self, shutdown_event: SyncEvent, data_fetcher: PassiveDataFetcher, collect_data_passive: SyncEvent,
                 found_project: SyncEvent):
        self.__thread: Thread
        self.__shutdown: SyncEvent = shutdown_event
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
            else:
                self.__data_fetcher.finish_fetching()
                self.__found_project.clear()

    def start(self):
        print("[PassiveDataThread]    started")
        self.__thread = Thread(target=self.__run)
        self.__data_fetcher.start()
        self.__thread.start()

    def stop(self):
        print("[PassiveDataThread]  stop signal sent")
        self.__data_fetcher.stop()
        self.__thread.join()
        print("[PassiveDataThread]  stopped")
