import os
import subprocess
import time
from typing import List
import psutil

'''collects processes with psutil and filters them'''


class ProcessCollector:
    PROC_NAME_FILTER = "cc1plus"

    def __init__(self, current_origin_pid: int) -> None:
        self.current_origin_pid = current_origin_pid

    def catch_processes(self, processes: List[str]) -> List[psutil.Process]:
        process_list: List[psutil.Process] = list()
        for proc in processes:
            process_list.append(psutil.Process(self.get_pid(proc)))

        return process_list

    def get_pid(self, proc: str):
        pass
