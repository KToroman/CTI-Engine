import os
from multiprocessing import Queue
from multiprocessing.synchronize import Lock as SyncLock
from typing import Dict, List, Optional, Any

from rocksdict import Rdict, RdictIter
from src.fetcher.FetcherInterface import FetcherInterface
from src.model.Model import Model
from src.model.core.CFile import CFile
from src.model.core.DataEntry import DataEntry
from src.model.core.Header import Header
from src.model.core.Metric import Metric
from src.model.core.Project import Project
from PyQt5.QtCore import pyqtSignal

from src.model.core.SourceFile import SourceFile


class FileLoader(FetcherInterface):

    def __init__(
        self,
        directory_path: str,
        model: Model,
        model_lock: SyncLock,
        visualize_signal: pyqtSignal,
        project_queue: "Queue[str]",
    ):
        self.__model_lock = model_lock
        self.__dir_path = directory_path
        self.__model = model
        self.__visualize_signal = visualize_signal
        self.__project_queue = project_queue
        self.__all_cfiles: Dict[str, CFile] = dict()
        
        self.__path: str = ""
        self.__hierarchy = 0
        self.__found_cfile = None
        self.__timestamp = 0
        self.__parent: str = ""
        self.__compile_command: str = ""
        self.__project: Project
        

    def update_project(self) -> bool:
        if self.__is_valid_path():
            self.__db = Rdict(self.__dir_path)
            self.__iter: RdictIter = self.__db.iter()
            self.__project = self.__create_project()
            self.__add_files()
            self.__insert_values()

            with self.__model_lock:
                self.__model.add_project(self.__project, None)
            self.__project_queue.put(self.__project.name)
            self.__visualize_signal.emit()  # type: ignore[attr-defined]
            self.__db.close()
            return False
        raise FileNotFoundError(
            "Couldn't find any saved projects on the given path")
    
    def __insert_values(self) -> None:
        self.__iter.seek_to_first()
        while self.__iter.valid():
            key = self.__iter.key()
            value = self.__iter.value()
            self.__decode_key(key)
            if value is not None:
                self.__add_to_project(value)
            self.__iter.next()

    def __add_files(self):
        for i in range(0,3):
            self.__iter.seek_to_first()
            while self.__iter.valid():
                key = self.__iter.key()
                value = self.__iter.value()
                self.__decode_key(key)
                if value is None:
                    self.__divide_files(i)
                self.__iter.next()
                
    def __divide_files(self, hierarchy_level: int):
        if hierarchy_level == 0:
            if self.__hierarchy == hierarchy_level:
                file = SourceFile(self.__path)
                self.__project.source_files.append(file)
                if self.__compile_command != "":
                    file.compile_command = self.__compile_command
                self.__all_cfiles[self.__file_identifier] = file

        elif self.__hierarchy == hierarchy_level:
            parent_key = f"{self.__parent}\n{self.__grand_parent}\n"
            parent = self.__all_cfiles.get(parent_key, None)
            file = Header(self.__path, None, self.__hierarchy)
            file.parent = parent
            parent.headers.append(file)
            self.__all_cfiles[self.__file_identifier] = file

    def __decode_key(self, key: str):
        keys: List[str] = key.split("\n")
        self.__path = keys[0]
        self.__compile_command = keys[1]
        self.__parent = keys[2]
        self.__grand_parent = keys[3]
        self.__hierarchy: int = int(keys[4])
        self.__timestamp: float = float(keys[5])
        self.__found_cfile = self.__all_cfiles.get(self.__path, None)
        self.__file_identifier = f"{self.__path}\n{self.__parent}\n{self.__grand_parent}"

    def __add_to_project(self, value: List[Any]):
        self.__found_cfile = self.__all_cfiles.get(self.__file_identifier)
        if self.__found_cfile is None:
            self.__found_cfile = self.__add_cfile_to_project()
        if self.__hierarchy > 0:
            #self.__check_parent()
            pass
        self.__add_data_entry(value)


    def __check_parent(self):
        parent = self.__all_cfiles.get(f"{self.__parent}\n{self.__grand_parent}\n", None)
        if parent is None:
            header_path = self.__path
            self.__path = self.__parent
            parent = self.__add_cfile_to_project()
            self.__path = header_path
        for header in parent.headers:
            if header.path == self.__path:
                return
        parent.headers.append(self.__found_cfile)
    

    def __add_data_entry(self, value: List[Any]):
        if self.__found_cfile is None:
            return
        data_entry = self.__extract_dataentry(
            value=value, cfile_path=self.__found_cfile.path, timestamp=self.__timestamp)
        if data_entry is None:
            return
        else:
            self.__found_cfile.data_entries.append(data_entry)

    def __add_cfile_to_project(
        self,
    ) -> CFile:
        '''to be called if no cfile with path==path was found yet. '''
        self.counter += 1
        new_sourcefile: SourceFile = SourceFile(self.__path)
        if not self.__compile_command == "":
            new_sourcefile.compile_command = self.__compile_command
        self.__project.source_files.append(new_sourcefile)
        self.__project.file_dict.add_file(new_sourcefile)
        self.__all_cfiles[self.__path] = new_sourcefile
        return new_sourcefile


    def __extract_dataentry(self, value: List[Any] | None, cfile_path: str, timestamp: float) -> Optional[DataEntry]:
        if value is None:
            return None
        metrics: List[Metric] = value
        # TODO if compile command add to sourcefile
        data_entry: DataEntry = DataEntry(
            path=cfile_path, timestamp=timestamp, metrics=metrics
        )
        return data_entry

    def __create_project(self) -> Project:
        project_name = self.__dir_path.removesuffix("_DataBase")
        project = Project("", project_name, self.__dir_path)
        return project

    def __is_valid_path(self) -> bool:
        return os.path.isdir(self.__dir_path)
