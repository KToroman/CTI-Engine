import os
from os.path import isfile, join

import jsonpickle

from src.fetcher.FetcherInterface import FetcherInterface
from src.model.Model import Model
from src.model.core.Project import Project


class FileLoader(FetcherInterface):

    def __init__(self, path: str, model: Model):
        self.__path = path
        self.__model = model

    def update_project(self) -> bool:
        if self.__is_valid_file():
            self.__model.add_project(self.__create_project())
            return True

        elif self.__is_valid_path() and self.__search_json():
            self.__model.add_project(self.__create_project())
            return True

        return False

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
                    self.__path += "\\" + file
                    return True
        return False
