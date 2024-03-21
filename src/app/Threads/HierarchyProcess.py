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
    def __init__(self, shutdown_event: SyncEvent, error_queue: "Queue[BaseException]",
                 work_queue: "Queue[Project]", hierarchy_fetching_event: SyncEvent,
                 source_file_queue: "Queue[SourceFile]", pid_queue: "Queue[str]", max_workers: int):
        self.__process: Process = Process(target=self.__run_process)
        self.__shutdown = shutdown_event
        self.__data_fetcher = HierarchyFetcher
        self.__work_queue = work_queue
        self.__error_queue = error_queue
        self.__current_work: str = ""
        self.project: Project
        self.__hierarchy_fetching_event = hierarchy_fetching_event
        self.max_workers = max_workers
        self.__pid_queue = pid_queue
        self.source_file_queue = source_file_queue

    def __run_process(self) -> None:
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
                                self.__data_fetcher.source_file_queue.put(SourceFile("ERROR"))
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


    def start(self) -> None:
        self.__data_fetcher = HierarchyFetcher(
            self.__hierarchy_fetching_event,
            self.__shutdown,
            self.source_file_queue,
            self.__pid_queue,
            max_workers=self.max_workers,
        )
        self.__process = Process(target=self.__run_process)
        self.__process.start()

    def stop(self) -> None:
        if self.__process.is_alive():
            self.__data_fetcher.__del__()

            self.__process.join()

    def is_alive(self) -> bool:
        return self.__process.is_alive()
