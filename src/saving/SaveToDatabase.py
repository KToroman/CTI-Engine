from os.path import join

from rocksdict import Rdict
from pathlib import Path
from typing import List

from src.model.DataBaseEntry import DataBaseEntry


from src.model.core.Project import Project
from src.saving.SaveInterface import SaveInterface


class SaveToDatabase(SaveInterface):

    def __init__(self, saves_path: str):
        self.__current_project_name: str = ""
        self.__saves_path: Path = Path(saves_path)
        self.__data_base_path: str

    def save_project(self, project: Project, delta: List[DataBaseEntry]):
        project_name: str = project.name
        if self.__current_project_name != project_name:
            self.__add_new_project(project_name)
            # project is being saved for the first time
            # TODO save metadata
        self.add_to_data_base(delta)

    def __add_new_project(self, new_proj_name: str):
        self.__current_project_name = new_proj_name
        self.__set_path()
        self.__saves_path.mkdir(exist_ok=True, parents=True)
        data_base_path: str = join(
            self.__saves_path, self.__current_project_name + "_DataBase"
        )
        db: Rdict = Rdict(self.__data_base_path)
        self.__data_base_path = data_base_path

    def add_to_data_base(self, delta: List[DataBaseEntry]):
        db: Rdict = Rdict(self.__data_base_path)
        for entry in delta:
            key = join(entry.source_file + "\n" + entry.header)
            value = (entry.timestamp, entry.metrics)
            db[key] = value

    def __set_path(self):
        path: str = join(self.__saves_path, self.__current_project_name)
        self.__saves_path = Path(path)
