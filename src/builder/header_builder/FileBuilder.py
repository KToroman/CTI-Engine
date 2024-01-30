from typing import List
from src.model.core.Header import Header


class FileBuilder:
    def __init__(self, compile_command: str) -> None:
        self.original_compile_command: List[str] = compile_command.split(" ")

    def generate_source_file(self, header: Header) -> str:
        pass

    def get_compile_command(self, header: Header) -> str:
        for entry in self.original_compile_command:
            
