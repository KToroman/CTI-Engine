import typing
from os.path import join

import jsonpickle  # type: ignore[import-untyped]
from pathlib import Path


from src.model.core.Project import Project
from src.saving.SaveInterface import SaveInterface


class SaveToJSON(SaveInterface):

    def __init__(self, cti_engine_folder: str) -> None:
        self.__current_project_name: str = ""
        self.__save_path: Path
        self.__cti_engine_folder: str = cti_engine_folder

    def save_project(self, project: Project | str) -> None:
        if type(project) is str:
            raise Exception
        project = typing.cast(Project, project)
        if self.__set_name(project):
            self.__set_path()

        self.__save_path.mkdir(exist_ok=True, parents=True)
        project_string: str = jsonpickle.encode(project)

        self.__write_file(project_string)

    def __write_file(self, project_string: str) -> None:
        writer = open(join(self.__save_path, self.__current_project_name + ".json"), "w")
        writer.write(project_string)
        writer.close()

    def __set_name(self, project: Project) -> bool:
        if self.__current_project_name != project.name:
            self.__current_project_name = project.name
            return True
        return False

    def __set_path(self) -> None:
        path: str = join(self.__cti_engine_folder, self.__current_project_name)
        self.__save_path = Path(path)
