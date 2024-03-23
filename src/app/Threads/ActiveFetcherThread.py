import queue
from multiprocessing import Queue
from threading import Thread
from multiprocessing.synchronize import Event as SyncEvent
from multiprocessing.synchronize import Lock as SyncLock

from PyQt5.QtCore import pyqtSignal

from src.fetcher.process_fetcher.ActiveDataFetcher import ActiveDataFetcher
from src.model.DataBaseEntry import DataBaseEntry
from src.model.Model import Model


class ActiveFetcherThread:
    def __init__(
        self,
        shutdown_event: SyncEvent,
        saver_queue: "Queue[str]",
        save_path: str,
        model: Model,
        model_lock: SyncLock,
        source_file_name_queue: "Queue[str]",
        error_queue: "Queue[BaseException]",
        build_dir_path: str,
        active_measurement_active: SyncEvent,
        visualise_event: pyqtSignal,
        visualise_project_queue: "Queue[str]",
    ) -> None:
        self.__thread: Thread
        self.__model: Model = model
        self.__model_lock: SyncLock = model_lock
        self.__shutdown_event: SyncEvent = shutdown_event
        self.__source_file_name_queue = source_file_name_queue
        self.__error_queue = error_queue
        self.__build_dir_path: str = build_dir_path
        self.__active_measurement_active: SyncEvent = active_measurement_active
        self.__saver_queue = saver_queue
        self.__save_path: str = save_path
        self.__visualise_signal: pyqtSignal = visualise_event  # type: ignore[call-overload]
        self.__visualise_project_queue = visualise_project_queue

    def start(self) -> None:
        self.__thread = Thread(target=self.__run)
        self.__thread.start()

    def __run(self) -> None:
        while not self.__shutdown_event.is_set():
            if not self.__source_file_name_queue.empty():
                self.__active_measurement_active.set()
                self.__start_new_measurement()
            self.__active_measurement_active.clear()

    def __start_new_measurement(self) -> None:
        source_file_name: str = self.__source_file_name_queue.get(True, 10)
        if not source_file_name.endswith(".o"):
            self.__error_queue.put(Exception("You can not build a single header!"))
            self.__active_measurement_active.clear()
            return
        if source_file_name == None:
            timeout_error: TimeoutError = TimeoutError(
                "[ActiveFetcherThread] Active Fetcher Thread could not access its source-file-queue."
            )
            self.__error_queue.put(timeout_error, True, 1)
            self.__active_measurement_active.clear()
            return
        with self.__model_lock:
            compile_command = self.__model.current_project.get_sourcefile(source_file_name).compile_command
        if compile_command == "":
            self.__error_queue.put(Exception("This SourceFile has not compile_command!"))
            self.__active_measurement_active.clear()
            return

        self.__model.current_project.current_sourcefile = source_file_name
        active_data_fetcher: ActiveDataFetcher
        with ActiveDataFetcher(
                source_file_name=source_file_name,
                model=self.__model,
                saver_queue=self.__saver_queue,
                save_path=self.__save_path,
                build_dir_path=self.__build_dir_path,
                model_lock=self.__model_lock,
                hierarchy_queue=Queue(),
        ) as active_data_fetcher:
            self.measure_source_file(active_data_fetcher)

        with self.__model_lock:
            curr_proj = self.__model.current_project
            if curr_proj is None:
                return
            try:
                self.__saver_queue.put(curr_proj.name, block=False)
            except queue.Full:
                pass
        self.__visualise_project_queue.put(curr_proj.get_project_name())
        self.__active_measurement_active.clear()
        self.__visualise_signal.emit()  # type: ignore[attr-defined]

    def measure_source_file(self, active_data_fetcher: ActiveDataFetcher) -> None:
        actively_fetching: bool = True
        while (self.__active_measurement_active.is_set() and actively_fetching and (not self.__shutdown_event.is_set())):
            actively_fetching = active_data_fetcher.update_project()

    def stop(self) -> None:
        if self.__thread.is_alive():
            self.__thread.join()
