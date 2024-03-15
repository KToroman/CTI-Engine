import threading
import multiprocessing
import time
from typing import List
from typing_extensions import Self

from multiprocessing.synchronize import Event as SyncEvent
from multiprocessing.synchronize import Lock as SyncLock

import psutil

from src.app.Threads.BuilderThread import BuilderThread
from src.builder.BuilderInterface import BuilderInterface
from src.builder.header_builder.CompilingTool import CompilingTool
from src.fetcher.FetcherInterface import FetcherInterface
from src.fetcher.process_fetcher.Threads.ActiveDataCollectionThread import ActiveDataCollectionThread
from src.fetcher.process_fetcher.process_observer.metrics_observer.DataObserver import DataObserver
from src.model.Model import Model
from src.model.core.SourceFile import SourceFile
from src.fetcher.process_fetcher.Threads.ProcessFindingThread import ProcessFindingThread
from src.fetcher.process_fetcher.Threads.ProcessCollectorThread import ProcessCollectorThread
from src.fetcher.process_fetcher.Threads.PassiveDataCollectionThread import PassiveDataCollectionThread


class ActiveDataFetcher(FetcherInterface):
    __seconds__to_move_on = 3

    def __init__(self,
                 source_file_name: str,
                 model: Model, build_dir_path: str,
                 saver_queue: multiprocessing.Queue,
                 save_path: str,
                 hierarchy_queue: multiprocessing.Queue,
                 model_lock: SyncLock,
                 fetcher_count: int = 5,
                 fetcher_process_count: int = 10,
                 process_collector_count: int = 20,
                 process_finder_count: int = 15,
                 ) -> None:
        self.__model = model
        self.__model_lock = model_lock
        self.__model.wait_for_project()
        with self.__model_lock:
            self.__source_file: SourceFile = model.get_sourcefile_by_name(source_file_name)

        self.__compiling_tool: BuilderInterface = CompilingTool(curr_project_dir=model.current_project.working_dir,
                                                                source_file=self.__source_file, path=build_dir_path)

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
        self.__building_event.set()
        while self.__building_event.is_set():
            for finder in self.__process_finder_list:
                finder.set_work(None)

        if self.__finished_event.is_set():
            return False
        else:
            return True

    # enter and exit define a context manager (with). each instance of ActiveDataFetcher should only exist in one with-Context

    def __enter__(self) -> Self:
        # required threads should be started here
        # queue to be used by builder thread and process finding thread
        self.__grep_command_queue = multiprocessing.Queue()
        process_list: List[psutil.Process] = list()
        process_list_lock: SyncLock = multiprocessing.Lock()

        for i in range(self.__data_collector_count):
            fetcher = ActiveDataCollectionThread(process_list, process_list_lock, self.__model, self.__model_lock,
                                                 DataObserver(), self.__fetcher_process_count, self.__shutdown_event,
                                                 self.__source_file, self.__active_event, self.__saver_queue)
            self.__data_collector_list.append(fetcher)
            fetcher.start()

        for i in range(self.__process_collector_count):
            process_collector_thread = ProcessCollectorThread(process_list, process_list_lock, self.__model,
                                                              self.__model_lock,
                                                              False, self.__data_collector_list, self.__saver_queue,
                                                              self.__hierarchy_queue,
                                                              self.__save_path, self.__shutdown_event,
                                                              None, None, None, self.__active_event)
            self.__process_collector_list.append(process_collector_thread)
            process_collector_thread.start()

        for i in range(self.__process_finder_count):
            finder = ProcessFindingThread(
                self.__shutdown_event, self.__process_collector_list, self.__active_event, active_fetching=True)
            self.__process_finder_list.append(finder)
            finder.start()

        self.__building_thread = BuilderThread(
            self.__building_event, self.__compiling_tool, self.__grep_command_queue, self.__finished_event,
            self.__shutdown_event)
        self.__building_thread.start()
        return self

    def __exit__(self, exc_type, exc_val, traceback) -> bool:
        # required threads should be stopped here
        self.__shutdown_event.set()
        for thread in self.__process_finder_list:
            thread.stop()
        for thread in self.__process_collector_list:
            thread.stop()
        for thread in self.__data_collector_list:
            thread.stop()
        self.__building_thread.stop()
        return False
