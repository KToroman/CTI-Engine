import shutil
import subprocess
from multiprocessing import Queue
from pathlib import Path
from subprocess import CompletedProcess, CalledProcessError

from src.builder.BuilderInterface import BuilderInterface
from src.builder.header_builder.FileBuilder import FileBuilder
from src.builder.header_builder.HeaderIterator import HeaderIterator
from src.model.core.Header import Header
from src.model.core.SourceFile import SourceFile


class CompilingTool(BuilderInterface):
    """Class for building the Header files included in a Source File"""

    DEFAULT_HEADER_DEPTH: int = 2

    def __init__(self,
                 curr_project_dir: str,
                 source_file: SourceFile,
                 path: str,
                 header_error_queue: "Queue[str]",
                 header_depth: int = DEFAULT_HEADER_DEPTH) -> None:
        """Compiling tool:
        curr_project_dir    -- The working directory of the project the SourceFile is from
        source_file         -- the sourceFile object to have its headers built
        path                -- The path at which the headers are built
        header_depth        -- Determines how many layers of the include hierarchy should be built.
                               0 means only headers directly included in the source file are built.
                               Default: 1"""
        self.source_file: SourceFile = source_file
        self.__header_error_queue = header_error_queue
        self.__build_path = path
        self.__curr_project_dir = curr_project_dir

        self.__file_builder = FileBuilder(curr_project_dir=curr_project_dir,
                                          compile_command=self.source_file.compile_command,
                                          source_file_name=source_file.get_name(),
                                          build_path=path)
        self.__header_iterator = HeaderIterator(self.source_file, header_depth)

    def build(self) -> bool:
        """returns true if there is another header to be built"""
        if not self.__header_iterator.has_next_header():
            return False
        header: Header = self.__header_iterator.pop_next_header()
        self.build_header(header)
        if not header.error:
            self.__header_error_queue.put("fin")
            self.__header_error_queue.put(header.get_name())

        return self.__header_iterator.has_next_header()

    def build_header(self, header: Header) -> None:
        file_path: Path = self.__file_builder.generate_source_file(header)
        proc: CompletedProcess[bytes] = self.__compile(file_path)

        try:
            proc.check_returncode()
        except CalledProcessError:
            header.error = True
            self.__header_error_queue.put(header.get_name())

    def __compile(self, file_name: Path) -> CompletedProcess[bytes]:
        args: list[str] = self.__file_builder.get_compile_command(file_name)
        try:
            proc: CompletedProcess[bytes] = subprocess.run(args=args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            return proc
        except TypeError as e:
            self.__header_error_queue.put("ERROR")

    def get_next_header(self) -> Header:
        return self.__header_iterator.get_next_header()

    def clear_directory(self) -> None:
        try:
            path: Path = (Path(self.__build_path) / Path(
                self.__curr_project_dir) / "Active_Mode_Build" / "temp").resolve()
            shutil.rmtree(path)
        except FileNotFoundError:
            pass
