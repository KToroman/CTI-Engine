import subprocess


class GCCCommandExecutor:

    def __init__(self) -> None:
        pass

    def execute(self, command: str) -> str:
        """executes the passed command via a subprocess and returns the standart output. Raises CalledProcessError if the Command is not completed sucessfully (exitcode != 0)"""
        completed_process: subprocess.CompletedProcess = subprocess.run(args=command, text=True)
        completed_process.check_returncode()
        return completed_process.stdout
    

