import subprocess, shlex

from io import StringIO

class GCCCommandExecutor:

    def __init__(self) -> None:
        pass

    def execute(self, command: str) -> str:
        """executes the passed command via a subprocess and returns the standart output. Raises CalledProcessError if the Command is not completed sucessfully (exitcode != 0)"""
        args: list[str] = shlex.split(command)
        completed_process: subprocess.CompletedProcess = subprocess.run(
            args=args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if completed_process.returncode != 0:
            print(completed_process.stderr)
            completed_process.check_returncode()
        return completed_process.stdout
