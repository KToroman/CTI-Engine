from re import split
from typing import List
import psutil

'''collects processes with psutil and filters them'''


class ProcessCollector:
    PROC_NAME_FILTER = "cc1plus"

    def catch_processes(self, line: str) -> psutil.Process:
        try:
            proc_info = split(" ", line, 10)
            proc_id: str = proc_info[0]
            process = psutil.Process(int(proc_id))
            if process.name() == self.PROC_NAME_FILTER:
                return process
        except:
            return None
        return None
