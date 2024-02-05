import psutil


class CProcess(psutil.Process):
    def __init__(self, pid: int, working_dir: str):
        super(CProcess, self).__init__(pid)
        self.gets_observed: bool = False
        self.working_dir = working_dir
