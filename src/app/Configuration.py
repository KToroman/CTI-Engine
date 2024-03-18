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
                config.active_build_dir_path = ""
            if config.saves_path == "None":
                print("[Configuration]  saves_path is None")
                config.saves_path = ""
            return config
