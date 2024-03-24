import threading
import multiprocessing
import time
from multiprocessing import Queue
from typing import List, Any

import typing_extensions
from typing_extensions import Self

from multiprocessing.synchronize import Event as SyncEvent
from multiprocessing.synchronize import Lock as SyncLock

import psutil

from src.app.Threads.BuilderThread import BuilderThread
from src.builder.BuilderInterface import BuilderInterface
from src.builder.header_builder.CompilingTool import CompilingTool
from src.exceptions.ProjectNotFoundException import ProjectNotFoundException
from src.fetcher.FetcherInterface import FetcherInterface
from src.fetcher.process_fetcher.Threads.ActiveDataCollectionThread import (
    ActiveDataCollectionThread,
)
from src.fetcher.process_fetcher.process_observer.metrics_observer.DataObserver import (
    DataObserver,
)
from src.model.DataBaseEntry import DataBaseEntry
from src.model.Model import Model
from src.model.core.CFile import CFile
from src.model.core.CFileReadViewInterface import CFileReadViewInterface
from src.model.core.Project import Project
from src.model.core.SourceFile import SourceFile
from src.fetcher.process_fetcher.Threads.ProcessFindingThread import (
    ProcessFindingThread,
)
from src.fetcher.process_fetcher.Threads.ProcessCollectorThread import (
    ProcessCollectorThread,
)
from src.fetcher.process_fetcher.Threads.PassiveDataCollectionThread import (
    PassiveDataCollectionThread,
)


class ActiveDataFetcher(FetcherInterface):
    __seconds__to_move_on = 3

    def __init__(
        self,
        source_file_name: str,
        model: Model,
        build_dir_path: str,
        saver_queue: "multiprocessing.Queue[str]",
        save_path: str,
        hierarchy_queue: "multiprocessing.Queue[Any]",
        model_lock: SyncLock,
        fetcher_count: int = 5,
        fetcher_process_count: int = 10,
        process_collector_count: int = 20,
        process_finder_count: int = 15,
    ) -> None:
        self.__model = model
        self.__model_lock = model_lock
        self.__model.wait_for_project()
        self.__header_error_queue: "Queue[str]" = Queue()
        with self.__model_lock:
            self.__source_file: SourceFile = model.get_sourcefile_by_name(
                source_file_name
            )
        if model.current_project is None:
            raise ProjectNotFoundException

        self.__compiling_tool: BuilderInterface = CompilingTool(
            curr_project_dir=model.current_project.working_dir,
            source_file=self.__source_file,
            path=build_dir_path,
            header_error_queue=self.__header_error_queue
        )

        self.__save_path = save_path

        self.__builder_Thread: BuilderThread
        self.__building_event: SyncEvent = multiprocessing.Event()
        self.__building_event.clear()
        self.__finished_event: SyncEvent = multiprocessing.Event()
        self.__finished_event.clear()

        self.__active_event: SyncEvent = multiprocessing.Event()
        self.__active_event.set()

        self.__process_finder_list: List[ProcessFindingThread] = list()
        self.__process_collector_list: List[ProcessCollectorThread] = list()
        self.__data_collector_list: List[PassiveDataCollectionThread] = list()
        self.__data_collector_count: int = fetcher_count
        self.__process_collector_count = process_collector_count

        self.__saver_queue = saver_queue
        self.__hierarchy_queue = hierarchy_queue

        self.__fetcher_process_count = fetcher_process_count
        self.__process_finder_count = process_finder_count
        self.__shutdown_event: SyncEvent = multiprocessing.Event()

    def update_project(self) -> bool:
        """Main method of the active data fetcher. Returns True if this method should be called again."""
        #if not self.__header_error_queue.empty():
        self.__building_event.set()
        while self.__building_event.is_set() or not self.__header_error_queue.empty():
            if not self.__header_error_queue.empty():
                header = self.__header_error_queue.get()
                if header == "fin":
                    time.sleep(0.01)
                    header = self.__header_error_queue.get()
                    with self.__model_lock:
                        model_header = self.__model.current_project.get_header(header,
                                                                           self.__model.current_project.get_sourcefile(
                                                                                self.__model.current_project.current_sourcefile))
                        model_header.has_been_build = True
                    continue
                if header == "ERROR":
                    self.__finished_event.set()
                    self.__building_event.clear()
                    break
                with self.__model_lock:
                    model_header = self.__model.current_project.get_header(header, self.__model.current_project.get_sourcefile(self.__model.current_project.current_sourcefile))
                if model_header is not None:
                    model_header.error = True
                    model_header.has_been_build = True
            for finder in self.__process_finder_list:
                if self.__shutdown_event.is_set():
                    break
                finder.set_work(None)

        if self.__finished_event.is_set():
            return False
        else:
            return True

    # enter and exit define a context manager (with).
    # each instance of ActiveDataFetcher should only exist in one with-Context

    def __enter__(self) -> Self:
        # required threads should be started here
        # queue to be used by builder thread and process finding thread
        self.__grep_command_queue: "multiprocessing.Queue[str]" = multiprocessing.Queue()
        process_list: List[psutil.Process] = list()
        process_list_lock: SyncLock = multiprocessing.Lock()

        for i in range(self.__data_collector_count):
            fetcher = ActiveDataCollectionThread(
                process_list=process_list,
                process_list_lock=process_list_lock,
                model=self.__model,
                model_lock=self.__model_lock,
                data_observer=DataObserver(),
                process_count=self.__fetcher_process_count,
                shutdown=self.__shutdown_event,
                source_file=self.__source_file,
                active_event=self.__active_event,
                saving_queue=self.__saver_queue,
            )
            self.__data_collector_list.append(fetcher)
            fetcher.start()

        for i in range(self.__process_collector_count):
            process_collector_thread = ProcessCollectorThread(
                process_list,
                process_list_lock,
                self.__model,
                self.__model_lock,
                False,
                self.__data_collector_list,
                self.__saver_queue,
                self.__hierarchy_queue,
                self.__save_path,
                self.__shutdown_event,
                None,
                None,
                None,
                self.__active_event,
            )
            self.__process_collector_list.append(process_collector_thread)
            process_collector_thread.start()

        for i in range(self.__process_finder_count):
            finder = ProcessFindingThread(
                self.__shutdown_event,
                self.__process_collector_list,
                self.__active_event,
                active_fetching=True,
            )
            self.__process_finder_list.append(finder)
            finder.start()

        self.__building_thread = BuilderThread(
            self.__building_event,
            self.__compiling_tool,
            self.__grep_command_queue,
            self.__finished_event,
            self.__shutdown_event,
        )
        self.__building_thread.start()
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, traceback: Any) -> typing_extensions.Literal[False]:
        # required threads should be stopped here
        self.__shutdown_event.set()
        self.__active_event.clear()
        for thread in self.__process_finder_list:
            thread.stop()
        for thread1 in self.__process_collector_list:
            thread1.stop()
        for thread2 in self.__data_collector_list:
            thread2.stop()
        self.__building_thread.stop()
        self.__compiling_tool.clear_directory()
        return False
