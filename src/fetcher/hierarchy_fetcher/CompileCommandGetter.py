import json, shlex
from io import FileIO
from src.model.core.SourceFile import SourceFile
from os.path import join


class CompileCommandGetter:

    def __init__(self, compile_commands_path: str) -> None:
        self.compile_commands_json: list[dict[str, str]] = self.__get_json(compile_commands_path)
        self.commands: dict[str, str] = {}
        self.__setup_commands()

    class CompileCommandError(Exception):
        pass

    def __get_json(self, path: str) -> list[dict[str, str]]:
        path = join(path, "build", "compile_commands.json")
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
            self.commands[self.__get_name_from_path(command_object["file"])] = command_object["command"]

    def __get_name_from_path(self, path: str) -> str:
        name: str = path.split("/")[-1]
        return name.removesuffix(".o")

    def get_compile_command(self, source_file: SourceFile) -> str:
        name = self.__get_name_from_path(source_file.path)
        if name not in self.commands:
            raise self.CompileCommandError(f"Source file does not have a stored command \n {source_file.path}")
        return self.commands[name]
    
    def generate_hierarchy_command(self, source_file: SourceFile) -> str:
        origin_command: str = self.get_compile_command(source_file)
        args: list[str] = shlex.split(origin_command)
        delindex: int
        for i in range(len(args)):
            if args[i] == "-o":
                delindex = i
        del args[delindex: delindex + 2]
        args.append("-H")
        return shlex.join(args)
