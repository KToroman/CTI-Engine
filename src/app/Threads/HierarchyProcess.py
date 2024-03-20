import time
from multiprocessing import Queue, Process
from threading import Thread
from multiprocessing.synchronize import Event as SyncEvent


from src.fetcher.hierarchy_fetcher.HierarchyFetcher import HierarchyFetcher
from src.model.Model import Model
from src.model.core.Project import Project
from src.model.core.SourceFile import SourceFile
from multiprocessing.synchronize import Lock as SyncLock


class HierarchyProcess:
    def __init__(self, shutdown_event: SyncEvent, data_fetcher: HierarchyFetcher, error_queue: Queue,
                 work_queue: Queue, hierarchy_fetching_event: SyncEvent):
        self.__process: Process = Process(target=self.__run_process)
        self.__shutdown = shutdown_event
        self.__data_fetcher = data_fetcher
        self.__work_queue = work_queue
        self.__error_queue = error_queue
        self.__current_work: str = ""
        self.project: Project
        self.__hierarchy_fetching_event = hierarchy_fetching_event

    def __run_process(self):
        try:
            repeat: bool = False
            while not self.__shutdown.is_set():
                if (not self.__work_queue.empty()) or repeat:
                    try:
                        if self.__current_work == "":
                            self.project = self.__work_queue.get()
                            self.__current_work = self.project.name

                        if not self.__hierarchy_fetching_event.is_set():
                            if self.__current_work != "":
                                self.__data_fetcher.source_file_queue.put(SourceFile(self.__current_work))
                                self.__data_fetcher.source_file_queue.put(SourceFile("fin"))
                            self.__current_work = ""
                            repeat = False
                            continue
                        self.__data_fetcher.project = self.project
                        repeat = self.__data_fetcher.update_project()
                        if repeat:
                              continue
                    except FileNotFoundError as e:
                        self.__error_queue.put(FileNotFoundError("could not find the compile-commands.json file"))
                        print("[HierarchyProcess]   could not find the compile-commands.json file for project: " +
                              self.__current_work)
                        repeat = False
                        self.__data_fetcher.source_file_queue.put(SourceFile("fin"))
                    self.__current_work = ""
                    repeat = False
        except KeyboardInterrupt:
            pass
        self.__data_fetcher.__del__()

    def start(self):
        print("[HierarchyProcess]    started")
        self.__process = Process(target=self.__run_process)
        self.__process.start()

    def stop(self):
        self.__data_fetcher.__del__()
        if self.__process.is_alive():
            self.__process.join()
        print("[HierarchyProcess]  stopped")

    def is_alive(self) -> bool:
        return self.__process.is_alive()
