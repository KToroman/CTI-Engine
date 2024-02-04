import os
import subprocess
import time
from re import split
from typing import List
import psutil

from src.fetcher.process_fetcher.CProcess import CProcess

'''collects processes with psutil and filters them'''


class ProcessCollector:
    PROC_NAME_FILTER = "cc1plus"

    def __init__(self, current_origin_pid: int) -> None:
        self.current_origin_pid = current_origin_pid

    def catch_processes(self, processes) -> List[CProcess]:
        process_list: List[CProcess] = list()
        for line in processes:
            proc_info = split(" *", line, 10)
            process_list.append(CProcess(proc_info[1]))

        return process_list

