from multiprocessing import Queue
import os
from multiprocessing.synchronize import Event as SyncEvent
from multiprocessing.synchronize import Lock as SyncLock


import psutil
from psutil import NoSuchProcess

from src.fetcher.process_fetcher.Threads.PassiveDataCollectionThread import (
    PassiveDataCollectionThread,
)
from src.fetcher.process_fetcher.process_observer.metrics_observer.DataObserver import (
    DataObserver,
)
from src.model.Model import Model
from src.model.core.DataEntry import DataEntry
from src.model.core.ProcessPoint import ProcessPoint
from src.model.core.SourceFile import SourceFile


class ActiveDataCollectionThread(PassiveDataCollectionThread):

    def __init__(
        self,
        process_list: list[psutil.Process],
        process_list_lock: SyncLock,
        model: Model,
        model_lock: SyncLock,
        data_observer: DataObserver,
        process_count,
        shutdown: SyncEvent,
        source_file: SourceFile,
        active_event: SyncEvent,
        saving_queue: Queue
    ):
        self.__source_file = source_file
        self.__saving_queue: Queue = saving_queue
        super().__init__(
            process_list,
            process_list_lock,
            model,
            model_lock,
            data_observer,
            process_count,
            shutdown,
            active_event,
        )

    def __add_data_entry(self, data_entry: DataEntry):
        with self.__model_lock:
            self.__model.insert_datapoint_header(
                data_entry=data_entry, source_file_path=self.__source_file.path
            )

    def __make_entry(self, process_point: ProcessPoint) -> None:
        try:
            cmdline: list[str] = process_point.process.cmdline()
            path: str = process_point.process.cwd()

            if "cc1plus" not in cmdline[0]:
                return

            has_o: bool = False
            for line in cmdline:
                if line.endswith(".o"):

                    source_file_path = line.split("/")[-2].replace("#", "/")
                    if source_file_path != self.__source_file.path:
                        return

                    path = line.split("/")[-1].replace("#", "/")
                    path = path.removesuffix(".cpp.o")
                    has_o = True

                    break
            if not has_o:
                return
            entry: DataEntry = DataEntry(
                path, process_point.timestamp, process_point.metrics
            )
            self.__add_data_entry(entry)
        except NoSuchProcess:
            return
        except FileNotFoundError:
            return
        except PermissionError:
            return
