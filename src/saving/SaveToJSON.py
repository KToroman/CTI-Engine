import os
from os.path import join

import jsonpickle
import time

from src.model.core.Project import Project
from src.saving.SaveInterface import SaveInterface


class SaveToJSON(SaveInterface):

    def __init__(self):
        self.__current_project_name: str = ""
        self.current_project_pid: int = 0
        self.__save_path: str = ""

    def save_project(self, project: Project):
        self.__set_name(project)
        self.__set_path(project.path_to_save)

        if not os.path.isdir(self.__save_path):
            os.makedirs(self.__save_path)

        project_string: str = jsonpickle.encode(project)

        self.__write_file(project_string)

    def __write_file(self, project_string: str):
        writer = open(join(self.__save_path, self.__current_project_name + ".json"), "w")
        writer.write(project_string)
        writer.close()

    def __set_name(self, project: Project):
        if self.current_project_pid != project.origin_pid:
            time_int: int = time.time().__int__()
            self.current_project_pid = project.origin_pid

            self.__current_project_name = ("CTI_ENGINE_SAVE " + self.current_project_pid.__str__() + " " +
                                           time_int.__str__())

    def __set_path(self, path: str = None):
        if path is None or path == "":
            self.__save_path = self.__default_path()
            return

        self.__save_path = join(path, self.__current_project_name)

    def __default_path(self) -> str:
        default_path: str = join(os.getcwd().split("src")[0], "saves")
        return join(default_path, self.__current_project_name)
