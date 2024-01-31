from typing import List
from src.model.core.Header import Header
from pathlib import Path


class FileBuilder:
    def __init__(self, compile_command: str, source_file_name: str, build_path: str) -> None:
        self.original_compile_command: List[str] = compile_command.split(" ")
        self.source_file_name = source_file_name
        self.build_path = build_path

    def generate_source_file(self, header: Header) -> str:
        path = Path(self.build_path) / 'Active_Mode_Build'
        path.mkdir(exist_ok=True)
        file_name: str = header.path + ".cpp"
        with (path / file_name).open('w') as new_source_file:
            new_source_file.write(...)

    def get_compile_command(self, header: Header) -> str:
        compile_command_header: str = ""
        for entry in self.original_compile_command:
            if entry is self.source_file_name:
                compile_command_header += header.path + ".cpp"
            else:
                compile_command_header += entry
        return compile_command_header
