import os
from threading import Lock
from multiprocessing.synchronize import Event as SyncEvent

import psutil
from psutil import NoSuchProcess

from src.fetcher.process_fetcher.Threads.DataCollectionThread import DataCollectionThread
from src.fetcher.process_fetcher.process_observer.metrics_observer.DataObserver import DataObserver
from src.model.Model import Model
from src.model.core.DataEntry import DataEntry
from src.model.core.ProcessPoint import ProcessPoint
from src.model.core.SourceFile import SourceFile


class ActiveDataCollectionThread(DataCollectionThread):

    def __init__(self, process_list: list[psutil.Process], process_list_lock: Lock, model: Model, model_lock: Lock,
                 data_observer: DataObserver, process_count, shutdown: SyncEvent, source_file: SourceFile, active_event: SyncEvent):
        self.__source_file = source_file
        super().__init__(process_list, process_list_lock, model, model_lock, data_observer, process_count, shutdown, active_event)

    def _add_data_entry(self, data_entry: DataEntry):
        with self._model_lock:
            self._model.insert_datapoint_header(data_entry, self.__source_file)
            print("check2")

    def _make_entry(self, process_point: ProcessPoint) -> None:
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

                    print((source_file_path, path))

                    break
            if not has_o:
                return
            entry: DataEntry = DataEntry(path, process_point.timestamp, process_point.metrics)
            self._add_data_entry(entry)
        except NoSuchProcess:
            return
        except FileNotFoundError:
            return
        except PermissionError:
            return
