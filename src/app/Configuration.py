import os
from os.path import join

from typing import Optional, Self
import json
from attr import define, frozen
import cattrs
from cattrs.gen import override

from src.app.FetcherCountConfiguration import FetcherCountConfiguration

@define(frozen=True)
class Configuration:
    process_finder_count: int
    process_collector_count: int
    fetcher_count: int
    fetcher_process_count: int
    hierarchy_fetcher_worker_count: int
    active_build_dir_path: str
    saves_path: str

    def __init__(self, config_path: str):
        return self.load(config_path)

    def load(self, config_path: str) -> Self:
        with open(config_path, "r") as config_json: 
            config: Configuration = cattrs.structure(config_json, Configuration)
            if config.active_build_dir_path is None:
                config.active_build_dir_path = self.__get_cti_folder_path() + "\\builds"
            if config.saves_path is None:
                config.saves_path = self.__get_cti_folder_path() + "\\saves"
            return config
    
    def __get_cti_folder_path(self) -> str:
        path: str = ""
        path += join(os.getcwd().split("cti-engine-prototype")[0])
        return path

