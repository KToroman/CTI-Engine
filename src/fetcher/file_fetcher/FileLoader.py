import os
from multiprocessing import Manager, Queue
from os.path import isfile, join
from multiprocessing.synchronize import Lock as SyncLock
from typing import Dict


import jsonpickle
from rocksdict import Rdict

from src.fetcher.FetcherInterface import FetcherInterface
from src.model.Model import Model
from src.model.core.Header import Header
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
        self.__sourcefiles: Dict[str, SourceFile] = dict()
        self.__headers: Dict[str, Header] = dict()

    def update_project(self) -> bool:
        if self.__is_valid_file():
            project: Project = self.__create_project()
            with self.__model_lock:
                self.__insert_values(project)
                self.__model.add_project(project, None)
                self.__model.current_project = project
            self.__project_queue.put(project.name)
            self.__visualize_signal.emit()
            return False

        elif self.__is_valid_path() and self.__search_json():
            project: Project = self.__create_project()
            with self.__model_lock:
                self.__model.add_project(project, None)
            self.__project_queue.put(project.name)
            self.__visualize_signal.emit()
            return False

        raise FileNotFoundError("Couldn't find any saved projects on the given path")

    def __insert_values(self, project: Project):
        db: Rdict = Rdict(self.__path)
        for key, value in db.items():
            self.__add_to_project(key, value)
        db.close()
    
    def __add_to_project(self, key, value):
        with self.__model_lock:


    def __create_project(self) -> Project:
        project_name = self.__path.removesuffix("_DataBase")
        project = Project("", project_name, self.__path)
        return project

    def __read_file(self) -> str:
        reader = open(self.__path, "r")
        file_string: str = reader.read()
        reader.close()
        return file_string

    def __is_valid_path(self) -> bool:
        return os.path.isdir(self.__path)

    def __is_valid_file(self) -> bool:
        return os.path.isfile(self.__path)

    def __search_json(self) -> bool:
        for file in os.listdir(self.__path):
            if "json" in file:
                if isfile(join(self.__path, file)):
                    self.__path = join(self.__path, file)
                    return True
        return False
