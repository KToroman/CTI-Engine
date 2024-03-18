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
        print("[SaveToDatabase]     "+self.__saves_path)
        self.__model_lock = model_lock
        self.__model: Model = model

    def save_project(self, project_name: str):
        project = self.__model.get_project_by_name(project_name)
        with self.__model_lock:
            delta: List[DataBaseEntry] = project.delta_entries
            project.delta_entries = list()
        if self.__current_project_name != project_name:
            print("[SaveToDataBase]     new project saved")
            self.__add_new_project(project)
            # project is being saved for the first time
        self.__add_to_data_base(delta)
        print(f"[SaveToDatabase]    saved {len(delta)} new entries")

    def __add_new_project(self, project: Project):
        self.__current_project_name = project.name
        self.__saves_path = project.path_to_save
        Path(self.__saves_path).mkdir(exist_ok=True, parents=True)
        db: Rdict = Rdict(self.__saves_path)
        db.close()

    def __add_to_data_base(self, delta: List[DataBaseEntry]):
        db: Rdict = Rdict(self.__saves_path)
        print(f"opened Database: {self.__saves_path}")
        for entry in delta:
            key = f"{entry.path}\n{entry.parent}\n{entry.hierarchy_level}"
            value = (entry.timestamp, entry.metrics)
            db[key] = value
        db.close()
