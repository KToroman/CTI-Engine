import psutil


class CProcess(psutil.Process):
    def __init__(self, pid: int):
        super(CProcess, self).__init__(pid)
        self.gets_observed: bool = False
