import os
import threading
from multiprocessing import Queue, Lock
from os.path import isfile, join

import jsonpickle

from src.fetcher.FetcherInterface import FetcherInterface
from src.model.Model import Model
from src.model.core.Project import Project
from PyQt5.QtCore import pyqtSignal


class FileLoader(FetcherInterface):

    def __init__(self, path: str, model: Model, model_lock: Lock, visualize_event: pyqtSignal,
                 project_queue: Queue):
        self.__model_lock = model_lock
        self.__path = path
        self.__model = model
        self.__visualize_event = visualize_event
        self.__project_queue = project_queue

    def update_project(self) -> bool:
        if self.__is_valid_file():
            project: Project = self.__create_project()
            with self.__model_lock:
                self.__model.add_project(project, None)
            self.__project_queue.put(project.name)
            self.__visualize_event.emit()
            return False

        elif self.__is_valid_path() and self.__search_json():
            project: Project = self.__create_project()
            with self.__model_lock:
                self.__model.add_project(project, None)
            self.__project_queue.put(project.name)
            self.__visualize_event.emit()
            return False

        raise FileNotFoundError("Couldn't find any saved projects on the given path")

    def __create_project(self) -> Project:
        project_string: str = self.__read_file()
        project: Project = jsonpickle.decode(project_string)
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
