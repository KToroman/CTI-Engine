import os
import subprocess
import threading
import time
from os.path import join
from re import split
from typing import List, IO, Optional

import psutil
from psutil import NoSuchProcess

from src.model.Model import Model
from src.model.core.Project import Project

'''collects processes with psutil and filters them'''


class ProcessCollector:
    PROC_NAME_FILTER = "cc1plus"

    def __init__(self, model: Model, check_for_project: bool, model_lock: threading.Lock):
        self.__check_for_project = check_for_project

        self.__process_list_lock: threading.Lock = threading.Lock()
        self.__process_list: List[psutil.Process] = list()

        self.__model_lock = model_lock
        self.__model = model

    def catch_process(self) -> IO[str] | None:
        grep = subprocess.Popen('ps -e | grep cc1plus', stdout=subprocess.PIPE, shell=True, encoding='utf-8')
        return grep.stdout
