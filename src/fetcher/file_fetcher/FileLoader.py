import multiprocessing
import os
import threading
from os.path import isfile, join

import jsonpickle

from src.fetcher.FetcherInterface import FetcherInterface
from src.model.Model import Model
from src.model.core.Project import Project


class FileLoader(FetcherInterface):

    def __init__(self, path: str, model: Model, model_lock: multiprocessing.Lock):
        self.__model_lock = model_lock
        self.__path = path
        self.__model = model

    def update_project(self) -> bool:
        if self.__is_valid_file():
            project: Project = self.__create_project()
            #self.__model_lock.acquire()
            self.__model.add_project(project)
            #self.__model_lock.release()
            return False

        elif self.__is_valid_path() and self.__search_json():
            project: Project = self.__create_project()
            self.__model_lock.acquire()
            self.__model.add_project(project)
            self.__model_lock.release()
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
