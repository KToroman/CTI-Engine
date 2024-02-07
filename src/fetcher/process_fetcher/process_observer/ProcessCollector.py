import os
import subprocess
import time
from os.path import join
from re import split
from typing import List, IO
import psutil

from src.model.Model import Model
from src.model.core.Project import Project

'''collects processes with psutil and filters them'''


class ProcessCollector:
    PROC_NAME_FILTER = "cc1plus"

    def __init__(self, model: Model, path_to_save: str):
        self.process_list: List[psutil.Process] = list()
        self.__model = model
        self.__path_to_save = path_to_save

    def __create_processes(self, line: str) -> psutil.Process:
        try:
            proc_info = split(" ", line, 10)
            proc_id: str = proc_info[0]
            process = psutil.Process(int(proc_id))
            if process.name() == self.PROC_NAME_FILTER:
                return process
        except:
            return None
        return None

    def catch_process(self) -> IO[str] | None:
        ps = subprocess.Popen(['ps', '-e'], stdout=subprocess.PIPE)
        grep = subprocess.Popen(['grep', 'cc1plus'], stdin=ps.stdout, stdout=subprocess.PIPE, encoding='utf-8')
        ps.stdout.close()
        grep.stdout.readline()
        return grep.stdout

    def make_process(self, line: str) -> psutil.Process:
        process = self.__create_processes(line)
        if not self.__is_process_in_list(process) and process is not None:
            self.process_list.append(process)
            self.project_checker(process)
            return process
        return None

    def __is_process_in_list(self, process: psutil.Process):
        for proc in self.process_list:
            try:
                if proc.pid == process.pid:
                    return True
            except:
                continue
        return False

    def project_checker(self, proc: psutil.Process):
        try:
            time.sleep(0.1)
            project_name: str = self.__get_project_name(proc)
            if self.__model.current_project is None or project_name != self.__model.current_project.working_dir:
                self.__model.add_project(Project(project_name, proc.ppid(), self.__path_to_save))
        except:
            return

    def __get_project_name(self, process: psutil.Process) -> str:
        working_dir: str = process.cwd()
        if working_dir.split("build").__len__() > 2:
            return join(working_dir.split("build/")[0], "build", working_dir.split("build/")[1])
        return working_dir.split("build")[0]
