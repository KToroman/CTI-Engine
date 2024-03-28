import shlex
from src.model.core.Header import Header
from pathlib import Path


class FileBuilder:
    def __init__(self, curr_project_dir: str, compile_command: str, source_file_name: str, build_path: str) -> None:
        self.__original_compile_command: str = compile_command
        self.__source_file_name: str = source_file_name
        self.__build_path: Path = Path(build_path) / Path(
            curr_project_dir) / "CTI_Engine_Active_Mode_Build" / "temp" / source_file_name.replace("/", "#")
        self.__curr_project_dir: str = curr_project_dir

    def generate_source_file(self, header: Header) -> Path:
        """generates a source file that includes the given header

        The files are generated as build_path/Active_Mode_Build/temp/<source_file_path>/<header_path>.cpp
        where build_path is passed in the constructor"""
        path = self.__build_path
        # will just be ignored if directory already exists
        path.mkdir(exist_ok=True, parents=True)
        header_name: str = header.path.replace("/", "#") + ".cpp"
        header.build_file_name = header_name
        file_path: Path = Path(header_name)
        file_path = path / file_path
        with file_path.open('w') as new_source_file:
            new_source_file.write(self.__source_file_content(header))
            new_source_file.close()
        return file_path

    def __source_file_content(self, header: Header) -> str:
        content: str = f'#include "{header.path}"' + '\n int main() {}'
        return content

    def get_compile_command(self, file_path: Path) -> list[str]:
        """amends the original compile command of the Source File (passed in the constructor) to compile the header
         at the given path"""
        command: list[str] = shlex.split(self.__original_compile_command)

        delindex: int = -1
        if len(command) == 1:
            raise BaseException
        for i in range(len(command)):
            if command[i] == "-o":
                command[i + 1] = file_path.resolve().__str__() + ".o"
            elif command[i] == "-Werror":
                delindex = i
        if delindex != -1:
            del command[delindex]

        try:
            del command[-1]
        except:
            return
        command.append("-I" + self.__curr_project_dir)
        command.append(file_path.resolve().__str__())
        return command
