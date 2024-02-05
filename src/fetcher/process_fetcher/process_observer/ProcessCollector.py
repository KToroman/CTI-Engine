
import subprocess
import time

from re import split


from src.fetcher.process_fetcher.CProcess import CProcess

'''collects processes with psutil and filters them'''


class ProcessCollector:
    PROC_NAME_FILTER = "cc1plus"

    def __init__(self, current_origin_pid: int) -> None:
        self.current_origin_pid = current_origin_pid

    def catch_processes(self, line: str) -> CProcess:
        try:
            proc_info = split(" ", line, 10)
            proc_id: str = proc_info[0]
            process = CProcess(int(proc_id), "")
            if process.name() == self.PROC_NAME_FILTER:
                process.working_dir = process.cwd()
                return process
        except:
            return None
        return None
