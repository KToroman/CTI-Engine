import subprocess, shlex

from io import BytesIO

class GCCCommandExecutor:

    def __init__(self) -> None:
        pass

    def execute(self, command: str) -> str:
        """executes the passed command via a subprocess and returns the standart output. Raises CalledProcessError if the Command is not completed sucessfully (exitcode != 0)"""
        args: list[str] = shlex.split(command)
        stream: BytesIO = BytesIO()
        completed_process: subprocess.CompletedProcess = subprocess.run(
            args=args, stdout=stream, stderr=subprocess.STDOUT, check=True)
        output: str = stream.read().decode()
        stream.close()
        return output
