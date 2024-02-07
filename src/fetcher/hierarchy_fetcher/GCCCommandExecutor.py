import subprocess, shlex


class GCCCommandExecutor:

    def __init__(self) -> None:
        pass

    def execute(self, command: str) -> str:
        """executes the passed command via a subprocess and returns the standart output. Raises CalledProcessError if the Command is not completed sucessfully (exitcode != 0)"""
        args: list[str] = shlex.split(command)
        completed_process: subprocess.CompletedProcess = subprocess.run(
            args=args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, check=True)
        return completed_process.stdout

