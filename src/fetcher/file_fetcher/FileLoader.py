import os
from multiprocessing import Manager, Queue
from multiprocessing.synchronize import Lock as SyncLock
from posixpath import join
from typing import Dict, List, Optional, Tuple


from rocksdict import Rdict, RdictIter

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
            self.__db = Rdict(self.__path)
            project: Project = self.__create_project()
            print("[FileLoader]     created new project")
            self.__insert_values(project)
            with self.__model_lock:
                self.__model.add_project(project, None)
                self.__model.current_project = project
            self.__project_queue.put(project.name)
            self.__visualize_signal.emit()
            print("[FileLoader]     visualize signal emitted")
            self.__db.close()
            return False
        raise FileNotFoundError(
            "Couldn't find any saved projects on the given path")

    def __insert_values(self, project: Project):
        iter: RdictIter = self.__db.iter()
        iter.seek_to_first()
        while iter.valid():
            key = iter.key()
            value = iter.value()
            self.__add_to_project(key, value, project)
            iter.next()
        print("[FileLoader]     added all entries to model.")

    def __add_to_project(self, key: str, value: List, project: Project):
        keys: List[str] = key.split("\n")
        path = keys[0]
        parent_or_compile_command = keys[1]
        hierarchy: int = int(keys[2])
        timestamp: float = float(keys[3])
        found_cfile = self.__all_cfiles.get(path, None)
        if found_cfile is None:
            found_cfile = self.__add_cfile_to_project(
                path=path,
                parent_or_compile_command=parent_or_compile_command,
                hierarchy=hierarchy,
                value=value,
                project=project,
            )
        if found_cfile.hierarchy_level > 0 and found_cfile.parent.path != parent_or_compile_command:
            found_cfile = self.__add_cfile_to_project(
                path=path,
                parent_or_compile_command=parent_or_compile_command,
                hierarchy=hierarchy,
                value=value,
                project=project,
            )
        if found_cfile.hierarchy_level > 0 and found_cfile.parent.path != parent_or_compile_command:
            found_cfile = self.__add_cfile_to_project(
                path=path,
                parent_or_compile_command=parent_or_compile_command,
                hierarchy=hierarchy,
                value=value,
                project=project,
            )
            
        self.__add_data_entry(
            found_cfile, value, timestamp)
        if hierarchy > 0 and found_cfile.parent is None:
            parent = self.__all_cfiles.get(parent_or_compile_command, None)
            if parent is None:
                parent = self.__add_parent(
                    parent_or_compile_command, hierarchy, project)
            found_cfile.parent = parent

    def __add_data_entry(self, cfile: CFile, value: List, timestamp):

        data_entry = self.__extract_dataentry(
            value=value, cfile_path=cfile.path, timestamp=timestamp)
        if data_entry is None:
            return
        else:
            cfile.data_entries.append(data_entry)

    def __add_cfile_to_project(
        self,
        path: str,
        parent_or_compile_command: str,
        hierarchy: int,
        value: List,
        project: Project,
    ) -> CFile:
        '''to be called if no cfile with path==path was found yet. '''
        if hierarchy > 0:
            if parent_or_compile_command == "":
                parent = None
            else:
                parent = self.__all_cfiles.get(parent_or_compile_command, None)
                if parent is None:
                    parent = self.__add_parent(
                        parent_or_compile_command, hierarchy, project)

            new_header = Header(path=path, parent=parent,
                                hierarchy_level=hierarchy)
            # TODO append header only when parent path is not ""
            if parent is not None:
                parent.headers.append(new_header)
                project.file_dict.add_file(new_header)
            self.__all_cfiles[path] = new_header
            return new_header
        else:
            new_sourcefile: SourceFile = SourceFile(path)
            if not parent_or_compile_command == "":
                new_sourcefile.compile_command = parent_or_compile_command
            project.source_files.append(new_sourcefile)
            project.file_dict.add_file(new_sourcefile)
            # TODO maybe need to add to project dict as well?
            self.__all_cfiles[path] = new_sourcefile

            return new_sourcefile

    def __add_parent(self, parent_path: str, hierarchy: int, project: Project) -> CFile:
        parent: CFile
        if hierarchy == 1:
            parent = SourceFile(parent_path)
            project.source_files.append(parent)
            project.file_dict.add_file(parent)
        if hierarchy == 2:
            parent = Header(path=parent_path, parent=None, hierarchy_level=1)
        self.__all_cfiles[parent_path] = parent
        return parent

    def __extract_dataentry(self, value: List | None, cfile_path: str, timestamp: float) -> Optional[DataEntry]:
        if value is None:
            return None
        metrics: List[Metric] = value
        # TODO if compile command add to sourcefile
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
