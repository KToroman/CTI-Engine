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

    def __create_processes(self, line: str) -> Optional[psutil.Process]:
        try:
            proc_info = split(" ", line, 10)
            proc_id: str = proc_info[0]
            process = psutil.Process(int(proc_id))
            return process
        except NoSuchProcess:
            return None
        return None

    def catch_process(self) -> IO[str] | None:
        grep = subprocess.Popen('ps -e | grep cc1plus', stdout=subprocess.PIPE, shell=True, encoding='utf-8')
        return grep.stdout

    def remove_process_from_list(self, process: psutil.Process):
        self.__process_list_lock.acquire()
        self.__process_list.remove(process)
        self.__process_list_lock.release()

    def make_process(self, line: str) -> Optional[psutil.Process]:
        process = self.__create_processes(line)
        if process is not None and not self.__is_process_in_list(process):
            if self.__check_for_project:
                self.__project_checker(process)

            self.__process_list_lock.acquire()
            self.__process_list.append(process)
            self.__process_list_lock.release()
            return process
        return None

    def __is_process_in_list(self, process: psutil.Process) -> bool:
        self.__process_list_lock.acquire()
        for proc in self.__process_list:
            try:
                if proc.pid == process.pid:
                    self.__process_list_lock.release()
                    return True
            except NoSuchProcess:
                continue
        self.__process_list_lock.release()
        return False

    def __project_checker(self, proc: psutil.Process):
        try:
            time.sleep(0.1)
            project_name: str = self.__get_project_name(proc)
            self.__model_lock.acquire()
            if project_name != self.__model.get_current_working_directory():
                self.__model.add_project(Project(project_name))
            self.__model_lock.release()
        except NoSuchProcess:
            self.__model_lock.release()
            return

    def __get_project_name(self, process: psutil.Process) -> str:
        working_dir: str = process.cwd()
        if working_dir.split("build").__len__() > 2:
            return join(working_dir.split("build/")[0], "build", working_dir.split("build/")[1])
        return working_dir.split("build")[0]
