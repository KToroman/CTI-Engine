from io import TextIOWrapper
from os.path import join


from pathlib import Path
from typing import List
from src.model.DataBaseEntry import DataBaseEntry


from src.model.core.CFile import CFile
from src.model.core.Project import Project
from src.saving.SaveInterface import SaveInterface


class SaveToDatabase(SaveInterface):

    def __init__(self, saves_path: str):
        self.__current_project_name: str = ""
        self.__saves_path: Path = Path(saves_path)

    def save_project(self, project_name: str, delta: List[DataBaseEntry]):
        if self.__current_project_name != project_name:
            # project is being saved for the first time
            self.__current_project_name = project_name
            self.__set_path()
            # TODO save metadata
        self.__saves_path.mkdir(exist_ok=True, parents=True)
        self.add_to_data_base(delta)

    def __set_name(self, project: Project) -> bool:
        if self.__current_project_name != project.name:
            self.__current_project_name = project.name
            return True
        return False

    def __set_path(self):
        path: str = join(self.__saves_path, self.__current_project_name)
        self.__saves_path = Path(path)
