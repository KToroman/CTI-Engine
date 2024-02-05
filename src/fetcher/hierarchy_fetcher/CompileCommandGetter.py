import json
from io import FileIO
from os.path import join
from src.model.core.SourceFile import SourceFile


class CompileCommandGetter:

    def __init__(self, compile_commands_path: str) -> None:
        self.compile_commands_json: list[dict[str, str]] = self.__get_json(compile_commands_path)
        self.commands: dict[str, str] = {}
        self.__setup_commands()

    class CompileCommandError(Exception):
        pass

    def __get_json(self, path: str) -> list[dict[str, str]]:
        path = join(path, "compile_commands.json")
        json_file: FileIO
        try:
            with open(path, "r") as json_file:
                return json.load(json_file)
        except FileNotFoundError:
            raise FileNotFoundError(f"Did not find compile_commands.json file in project working directory\n {path}")
        
    def __setup_commands(self):
        command_object: dict[str, str]
        for command_object in self.compile_commands_json:
            if "command" not in command_object:
                raise self.CompileCommandError(f"Command Object {command_object} does not contain command")
            self.commands[command_object["file"]] = command_object["command"]

    def get_compile_command(self, source_file: SourceFile) -> str:
        if source_file.path not in self.commands:
            raise self.CompileCommandError(f"Source file {source_file.path} does not have a stored command")
        return self.commands[source_file.path]
    
    def generate_hierarchy_command(self, source_file: SourceFile) -> str:
        origin_command: str = self.commands[source_file.path]
        if origin_command.startswith("gcc "):
            return origin_command.replace("gcc", "gpp -H", 1)
        elif origin_command.startswith("g++ "):
            return origin_command.replace("g++", "gpp -H", 1)
        elif origin_command.startswith("c++"):
            return origin_command.replace("c++", "gpp -H", 1)
        else:
            raise self.CompileCommandError(f"the stored command is not a recognized command\n {origin_command}")
