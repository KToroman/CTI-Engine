from os.path import join

from rocksdict import Rdict
from pathlib import Path
from typing import List
from multiprocessing.synchronize import Lock as SyncLock

from src.model.DataBaseEntry import DataBaseEntry
from src.model.Model import Model


from src.model.core.Project import Project
from src.saving.SaveInterface import SaveInterface


class SaveToDatabase(SaveInterface):

    def __init__(self, saves_path: str, model_lock: SyncLock, model: Model):
        print("initializing")
        self.__current_project_name: str = ""
        self.__saves_path: str = saves_path
        print(self.__saves_path)
        self.__data_base_path: str
        self.__model_lock = model_lock
        self.__model: Model = model

    def save_project(self, project_name: str):
        project = self.__model.get_project_by_name(project_name)
        with self.__model_lock:
            delta: List[DataBaseEntry] = project.delta_entries
            project.delta_entries = list()
        if self.__current_project_name != project_name:
            print("[SaveToDataBase]     new project saved")
            self.__add_new_project(project_name)
            # project is being saved for the first time
        self.__add_to_data_base(delta)
        print(f"[SaveToDatabase]    saved {len(delta)} new entries")

    def __add_new_project(self, new_proj_name: str):
        self.__current_project_name = new_proj_name
        self.__set_path()
        Path(self.__saves_path).mkdir(exist_ok=True, parents=True)
        data_base_path: str = join(
            self.__saves_path, self.__current_project_name + "_DataBase"
        )
        self.__data_base_path = data_base_path
        db: Rdict = Rdict(self.__data_base_path)
        db.close()

    def __add_to_data_base(self, delta: List[DataBaseEntry]):
        db: Rdict = Rdict(self.__data_base_path)
        print(f"opened Database: {self.__data_base_path}")
        for entry in delta:
            key = entry.source_file + "\n" + entry.header
            value = (entry.timestamp, entry.metrics)
            db[key] = value
        db.close()

    def __set_path(self):
        path: str = join(self.__saves_path, self.__current_project_name)
        self.__saves_path = path
