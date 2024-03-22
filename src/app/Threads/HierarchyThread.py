import time
import typing
from multiprocessing import Queue, Process
from threading import Thread
from multiprocessing.synchronize import Event as SyncEvent

from src.app.Threads.HierarchyProcess import HierarchyProcess
from src.fetcher.hierarchy_fetcher.HierarchyFetcher import HierarchyFetcher
from src.model.Model import Model
from src.model.core.CFile import CFile
from src.model.core.Header import Header
from src.model.core.Project import Project
from src.model.core.SourceFile import SourceFile
from multiprocessing.synchronize import Lock as SyncLock


class HierarchyThread:
    def __init__(self, shutdown_event: SyncEvent, fetching_hierarchy: SyncEvent, source_file_queue: "Queue[SourceFile]",
                 model: Model, model_lock: SyncLock, hierarchy_process: HierarchyProcess,
                 hierarchy_work_queue: "Queue[Project]",
                 process_shutdown: SyncEvent):

        self.__thread: Thread
        self.__shutdown = shutdown_event
        self.__current_work: str = ""
        self.__fetching_hierarchy = fetching_hierarchy
        self.source_file_queue = source_file_queue
        self.__model = model
        self.__model_lock = model_lock
        self.__process = hierarchy_process
        self.__hierarchy_work_queue = hierarchy_work_queue
        self.__process_shutdown = process_shutdown

        self.header = 0

    def __run_thread(self) -> None:
        current_project: str = ""
        while not self.__shutdown.is_set():
            if not self.__hierarchy_work_queue.empty():
                if not self.__process.is_alive():
                    self.__process_shutdown.clear()
                    self.__process.start()
            if not self.source_file_queue.empty():
                data: SourceFile = self.source_file_queue.get()
                if self.__current_work == "":
                    self.__current_work = data.path
                    self.__fetching_hierarchy.set()
                    continue
                if data.path == "cancel":
                    self.__model.get_semaphore_by_name(self.__current_work).hierarchy_fetcher_set()
                    time.sleep(0.5)
                    while not self.source_file_queue.empty():
                        data = self.source_file_queue.get()
                        if data.path != "cancel":
                            self.__model.get_project_by_name(data.path).set_failed()
                            self.__model.get_semaphore_by_name(data.path).hierarchy_fetcher_set()
                    self.__current_work = ""
                    self.__fetching_hierarchy.clear()
                    self.__process_shutdown.set()
                    self.__process.stop()
                    continue
                if data.path == "fin":
                    self.__model.get_semaphore_by_name(self.__current_work).hierarchy_fetcher_set()
                    self.__current_work = ""
                    self.__fetching_hierarchy.clear()
                    self.__process_shutdown.set()
                    self.__process.stop()
                    continue
                if data.path == "ERROR":
                    self.__process_shutdown.set()
                    with self.__model_lock:
                        self.__model.get_project_by_name(self.__current_work).set_failed()
                    self.__model.get_semaphore_by_name(self.__current_work).hierarchy_fetcher_set()
                    self.__current_work = ""
                    self.__fetching_hierarchy.clear()
                    self.__process.stop()
                    time.sleep(1)
                    continue
                time.sleep(0.01)
                with self.__model_lock:
                    proj: Project = self.__model.get_project_by_name(self.__current_work)
                    source_file: SourceFile = proj.update_source_file(data.path, data.compile_command)
                    source_file.error = data.error
                    self.__update_headers(proj, source_file, data.headers)

    def __update_headers(self, project: Project, parent: CFile, headers: typing.List[Header]) -> None:
        for header in headers:
            project.update_headers(header, parent, 1)


    def start(self) -> None:
        self.__thread = Thread(target=self.__run_thread)
        self.__thread.start()

    def stop(self) -> None:
        self.__process_shutdown.set()
        if self.__process.is_alive():
            self.__process.stop()
        if self.__thread.is_alive():
            self.__thread.join()
