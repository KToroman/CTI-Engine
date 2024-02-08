import subprocess, shlex

from io import StringIO

class GCCCommandExecutor:

    def __init__(self) -> None:
        pass

#    def execute(self, command: str) -> str:
#        """executes the passed command via a subprocess and returns the standart output. Raises CalledProcessError if the Command is not completed sucessfully (exitcode != 0)"""
#        args: list[str] = shlex.split(command)
#        print("hier command being executed")
#        with open("/common/homes/students/uruoe_sauer/Documents/PSE/CTIEngine/buffer.txt", "w") as stream:
#            completed_process: subprocess.CompletedProcess = subprocess.run(
#                args=args, stdout=stream, stderr=subprocess.STDOUT, check=True)
#        with open("/common/homes/students/uruoe_sauer/Documents/PSE/CTIEngine/buffer.txt", "r") as stream:
#            output: str = stream.read()
#        return output

    def execute(self, command: str) -> str:
        """executes the passed command via a subprocess and returns the standart output. Raises CalledProcessError if the Command is not completed sucessfully (exitcode != 0)"""
        args: list[str] = shlex.split(command)
        print("hier command being executed")
        completed_process: subprocess.CompletedProcess = subprocess.run(
            args=args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, check=True)
        return completed_process.stdout
