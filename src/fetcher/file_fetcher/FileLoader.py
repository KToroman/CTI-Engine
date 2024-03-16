import os
from multiprocessing import Manager, Queue
from multiprocessing.synchronize import Lock as SyncLock
from typing import Dict, List, Optional, Tuple


from rocksdict import Rdict

from src.exceptions.CFileNotFoundError import CFileNotFoundError
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
        project_queue: Queue,
    ):
        self.__model_lock = model_lock
        self.__path = directory_path
        self.__model = model
        self.__visualize_signal = visualize_signal
        self.__project_queue = project_queue
        self.__all_cfiles: Dict[str, CFile] = dict()

    def update_project(self) -> bool:
        if self.__is_valid_path():
            project: Project = self.__create_project()
            self.__insert_values(project)
            with self.__model_lock:
                self.__model.add_project(project, None)
                self.__model.current_project = project
            self.__project_queue.put(project.name)
            self.__visualize_signal.emit()
            return False
        raise FileNotFoundError("Couldn't find any saved projects on the given path")

    def __insert_values(self, project: Project):
        db: Rdict = Rdict(self.__path)
        for key, value in db.items():
            self.__add_to_project(key, value, project)
        db.close()

    def __add_to_project(self, key: str, value: Tuple, project: Project):
        paths: List[str] = key.split("\n")
        path = paths[0]
        parent_path = paths[1]
        hierarchy: int = int(paths[2])
        found_cfile = self.__all_cfiles.get(path, None)
        if found_cfile is None:
            found_cfile = self.__add_cfile_to_project(
                path=path,
                parent_path=parent_path,
                hierarchy=hierarchy,
                value=value,
                project=project,
            )
        self.__add_data_entry(found_cfile, value)
        if hierarchy > 0 and found_cfile.parent is None:
            parent = self.__all_cfiles.get(parent_path, None)
            if parent is None:
                parent = self.__add_parent(parent_path, hierarchy, project)
            found_cfile.parent = parent

    def __add_data_entry(self, cfile: CFile, value: Tuple):
        data_entry = self.__extract_dataentry(value=value, cfile_path=cfile.path)
        if data_entry is None:
            return
        cfile.data_entries.append(data_entry)

    def __add_cfile_to_project(
        self,
        path: str,
        parent_path: str,
        hierarchy: int,
        value: Tuple,
        project: Project,
    ) -> CFile:
        if hierarchy > 0:
            parent = self.__all_cfiles.get(parent_path, None)
            if parent is None:
                parent = self.__add_parent(parent_path, hierarchy, project)
            new_header = Header(path=path, parent=parent, hierarchy_level=hierarchy)
            parent.headers.append(new_header)
            self.__all_cfiles.update({path: new_header})
            return new_header
        else:
            new_sourcefile: SourceFile = SourceFile(path)
            project.source_files.append(new_sourcefile)
            self.__all_cfiles.update({path: new_sourcefile})
            return new_sourcefile

    def __add_parent(self, parent_path: str, hierarchy: int, project: Project) -> CFile:
        parent: CFile
        if hierarchy == 1:
            parent = SourceFile(parent_path)
            project.source_files.append(parent)
        if hierarchy == 2:
            parent = Header(path=parent_path, parent=None, hierarchy_level=1)
        self.__all_cfiles.update({parent_path: parent})
        return parent

    def __extract_dataentry(self, value: Tuple, cfile_path: str) -> Optional[DataEntry]:
        timestamp: float = value[0]
        metrics: List[Metric] = value[1]
        if timestamp is None or metrics is None:
            return None
        else:
            data_entry: DataEntry = DataEntry(
                path=cfile_path, timestamp=timestamp, metrics=metrics
            )
            return data_entry

    def __create_project(self) -> Project:
        project_name = self.__path.removesuffix("_DataBase")
        project = Project("", project_name, self.__path)
        return project

    def __is_valid_path(self) -> bool:
        return os.path.isdir(self.__path)
