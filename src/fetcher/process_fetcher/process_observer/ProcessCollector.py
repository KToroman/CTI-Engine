import os
from typing import List
import psutil

'''collects processes with psutil and filters them'''


class ProcessCollector:
    PROC_NAME_FILTER = "cc1plus"

    def __init__(self, current_origin_pid: int) -> None:
        self.current_origin_pid = current_origin_pid

    def __check_for_object_file(cmdline: List[str]) -> bool:
        for entry in cmdline:
            if entry.endswith(".o"):
                return True

    '''catches all build processes that produce .o files'''

    def catch_processes(self) -> List[psutil.Process]:
        build_processes: List[psutil.Process] = list()
        for process in psutil.process_iter(['pid', 'name', 'username']):
            if process.name() == self.PROC_NAME_FILTER:
                valid: bool = self.__check_for_object_file(process.cmdline())
            if valid:
                build_processes.append(process)
        return build_processes

    def check(self, process: psutil.Process) -> bool:
        ppid: int = process.ppid()
        parent_ppid: int = psutil.Process(ppid).ppid()
        parent_parent_proc = psutil.Process(parent_ppid)
        if parent_parent_proc.name() != "gcc":
            raise ValueError  # root of process is not gcc
        if parent_ppid == self.current_origin_pid:
            return True
        return False
