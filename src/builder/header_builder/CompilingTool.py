from msilib.schema import File
from src.builder.BuilderInterface import BuilderInterface
from src.model.core.SourceFile import SourceFile
from src.model.core.Header import Header
from src.builder.header_builder.FileBuilder import FileBuilder
from src.builder.header_builder.HeaderIterator import HeaderIterator

from subprocess import Popen
import shlex


class CompilingTool(BuilderInterface):

    DEFAULT_HEADER_DEPTH: int = 2

    def __init__(self, source_file: SourceFile, path: str, header_depth: int = DEFAULT_HEADER_DEPTH) -> None:
        self.source_file = source_file
<<<<<<< HEAD
        self.__build_path = path
        self.__file_builder = FileBuilder(self.source_file.compile_command)
        self.__header_iterator = HeaderIterator(self.source_file, header_depth)
=======
        self.file_builder = FileBuilder(self.source_file.compile_command, source_file.get_name(), path)
        self.header_iterator = HeaderIterator(self.source_file, header_depth)
>>>>>>> ca23c4aa036a738aad4aa4e8373050c0f570e449

    def build(self) -> bool:
        if not self.__header_iterator.has_next_header():
            return False
<<<<<<< HEAD
        header: Header = self.__header_iterator.get_next_header()
        self.__file_builder.generate_source_file(header, self.__build_path)
        self.compile(header)
        return self.__header_iterator.get_next_header()

    def compile(self, header: Header) -> None:
        command: str = self.__file_builder.get_compile_commmand(header)
=======
        header: Header = self.header_iterator.get_next_header()
        self.file_builder.generate_source_file(header)
        self.compile(header)
        return self.header_iterator.has_next_header()

    def compile(self, header: Header) -> None:
        command: str = self.file_builder.get_compile_command(header)
>>>>>>> ca23c4aa036a738aad4aa4e8373050c0f570e449
        args: list[str] = shlex.split(command)

        proc: Popen = Popen(args)

    def get_next_header(self) -> str:
        return self.__header_iterator.get_next_header()