from typing import List
from src.model.core.Header import Header
from pathlib import Path


class FileBuilder:
    def __init__(self, compile_command: str, source_file_name: str, build_path: str) -> None:
        self.__original_compile_command: List[str] = compile_command.split(" ")
        self.__source_file_name = source_file_name
        self.__build_path = build_path

    def generate_source_file(self, header: Header) -> str:
        '''generates a source file that includes the header named header.path + .cpp
        The files are generated in the CTIEngine-directory/Active_Mode_Build.'''
        path = Path(self.__build_path) / 'Active_Mode_Build'
        # will just be ignored if directory already exists
        path.mkdir(exist_ok=True)
        file_name: str = header.path + ".cpp"
        with (path / file_name).open('w') as new_source_file:
            new_source_file.write(self.__source_file_content(header))
            new_source_file.close()
        return file_name

    def __source_file_content(header: Header) -> str:
        content: str = f'#include "{header.path}"'
        return content

    def get_compile_command(self, header: Header) -> str:
        # TODO -I for project directory
        compile_command_header: str = ""
        for entry in self.__original_compile_command:
            if entry is self.__source_file_name:
                compile_command_header += header.path + ".cpp"
            else:
                compile_command_header += entry
        return compile_command_header
