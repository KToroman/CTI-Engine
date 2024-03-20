import subprocess, shlex
from multiprocessing import Queue


class GCCCommandExecutor:

    def __init__(self, pid_queue: "Queue[str]") -> None:
        self.__pid_queue: Queue[str] = pid_queue

    def execute(self, command: str) -> str:
        """executes the passed command via a subprocess and returns the standart output. Raises CalledProcessError if the Command is not completed sucessfully (exitcode != 0)"""
        args: list[str] = shlex.split(command)
        process: subprocess.Popen[str] = subprocess.Popen(args=args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        self.__pid_queue.put(str(process.pid))


        stdout, stderr = process.communicate()

        if process.returncode != 0:
            raise subprocess.CalledProcessError(cmd=command, returncode=process.returncode)
        return stderr
