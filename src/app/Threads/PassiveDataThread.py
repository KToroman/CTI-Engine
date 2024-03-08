from threading import Event, Thread

from src.fetcher.process_fetcher.PassiveDataFetcher import PassiveDataFetcher


class PassiveDataThread:
    def __init__(self,shutdown_event: Event, data_fetcher: PassiveDataFetcher, collect_data_passive: Event, found_project: Event):
        self.thread: Thread
        self.collect_data_passive = collect_data_passive
        self.found_project = found_project
        self.shutdown = shutdown_event
        self.data_fetcher = data_fetcher

    def collect_data(self):
        while not self.shutdown.is_set():
            if self.collect_data_passive.is_set():
                if self.data_fetcher.update_project():
                    self.found_project.set()
                else:
                    self.found_project.clear()

    def start(self):
        print("[PassiveDataThread]    started")
        self.thread = Thread(target=self.collect_data)
        self.data_fetcher.start()
        self.thread.start()

    def join(self):
        print("[PassiveDataThread]  stop signal sent")
        if self.thread.is_alive(): #TODO why would this ever be needed?
            self.thread.join()
        print("[PassiveDataThread]  stopped")
