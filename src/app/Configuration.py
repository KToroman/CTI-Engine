import os
from os.path import join

# from typing import Self
import json
from attr import define, frozen
import cattrs


@define
class Configuration:
    process_finder_count: int
    process_collector_count: int
    fetcher_count: int
    fetcher_process_count: int
    hierarchy_fetcher_worker_count: int
    active_build_dir_path: str
    saves_path: str

    @classmethod
    def load(cls, config_path: str):
        with open(config_path, "r") as config_json:
            config: Configuration = cattrs.structure(
                json.load(config_json), cls)
            if config.active_build_dir_path == "None":
                print("[Configuration]  active_build_dir_path is None")
                config.active_build_dir_path = Configuration.__get_cti_folder_path() + "\\builds"
            if config.saves_path == "None":
                print("[Configuration]  saves_path is None")
                config.saves_path = Configuration.__get_cti_folder_path() + "\\saves"
            return config

    @classmethod
    def __get_cti_folder_path(cls) -> str:
        path: str = ""
        path += join(os.getcwd().split("cti-engine-prototype")[0])
        return path


if __name__ == "__main__":
    config = Configuration.load("./config/ConfigFile.json")
    print(config.active_build_dir_path)
