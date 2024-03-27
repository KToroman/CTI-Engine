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
        self.__parent_or_compile_command: str = ""
        self.__project: Project
        

    def update_project(self) -> bool:
        if self.__is_valid_path():
            self.__db = Rdict(self.__dir_path)
            self.__iter: RdictIter = self.__db.iter()
            self.__project = self.__create_project()
            self.__insert_values()
            self.__add_files()
            with self.__model_lock:
                self.__model.add_project(self.__project, None)
                self.__model.current_project = self.__project
            self.__project_queue.put(self.__project.name)
            self.__visualize_signal.emit()  # type: ignore[attr-defined]
            self.__db.close()
            num_files = len(self.__all_cfiles)
            print(f"there are now {num_files} files")
            return False
        raise FileNotFoundError(
            "Couldn't find any saved projects on the given path")
    
    def __insert_values(self) -> None:
        self.__iter.seek_to_first()
        while self.__iter.valid():
            key = self.__iter.key()
            value = self.__iter.value()
            self.__decode_key(key)
            self.__add_to_project(value)
            self.__iter.next()

    def __add_files(self):
        self.__iter.seek_to_first()
        counter = 0
        while self.__iter.valid():
            key = self.__iter.key()
            value = self.__iter.value()
            self.__decode_key(key)
            if value is None:
                counter += 1
                self.__divide_files()
            self.__iter.next()
        print(f"added {counter}-files")

    def __divide_files(self):
        if self.__hierarchy == 0:
            file = SourceFile(self.__path)
        if self.__hierarchy == 1:
            file = Header(self.__path, None, 1)
        if self.__hierarchy == 2:
            file = Header(self.__path, None, 2)
        self.__all_cfiles[self.__file_identifier] = file

    def __decode_key(self, key: str):
        keys: List[str] = key.split("\n")
        self.__path = keys[0]
        self.__parent_or_compile_command = keys[1]
        self.__grand_parent = keys[2]
        self.__hierarchy: int = int(keys[3])
        self.__timestamp: float = float(keys[4])
        self.__found_cfile = self.__all_cfiles.get(self.__path, None)
        self.__file_identifier = f"{self.__path}\n{self.__parent_or_compile_command}\n{self.__grand_parent}"

    def __add_to_project(self, value: List[Any]):
        self.__found_cfile = self.__all_cfiles.get(self.__file_identifier)
        if self.__found_cfile is None:
            self.__found_cfile = self.__add_cfile_to_project(
            )
        if self.__hierarchy > 0:
            self.__check_parent()
        self.__add_data_entry(value)


    def __check_parent(self):
        parent = self.__all_cfiles.get(f"{self.__parent_or_compile_command}\n{self.__grand_parent}", None)
        if parent is None:
            header_path = self.__path
            self.__path = self.__parent_or_compile_command
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
        new_sourcefile: SourceFile = SourceFile(self.__path)
        if not self.__parent_or_compile_command == "":
            new_sourcefile.compile_command = self.__parent_or_compile_command
        self.__project.source_files.append(new_sourcefile)
        self.__project.file_dict.add_file(new_sourcefile)
        self.__all_cfiles[self.__path] = new_sourcefile
        return new_sourcefile

    def __add_parent(self) -> CFile:
        if self.__hierarchy == 1:
            parent = SourceFile(self.__parent_or_compile_command)
            self.__project.source_files.append(parent)
            self.__project.file_dict.add_file(parent)
        if self.__hierarchy == 2:
            parent = Header(path=self.__path, parent=None, hierarchy_level=1)
        self.__all_cfiles[self.__parent_or_compile_command] = parent
        return parent

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
