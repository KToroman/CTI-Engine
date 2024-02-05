from typing import List, Optional

from src.fetcher.FetcherInterface import FetcherInterface
from src.fetcher.hierarchy_fetcher.GCCCommandExecutor import GCCCommandExecutor
from src.fetcher.hierarchy_fetcher.CompileCommandGetter import CompileCommandGetter
from src.model.Model import Model
from src.model.core.Project import Project
from src.model.core.SourceFile import SourceFile
from src.model.core.CFile import CFile
from src.model.core.Header import Header


class HierarchyFetcher(FetcherInterface):

    def __init__(self, model: Model) -> None:
        self.__model: Model = model
        self.__gcc_command_executor: GCCCommandExecutor = GCCCommandExecutor()
        self.command_getter: Optional[CompileCommandGetter] = None

    def update_project(self) -> bool:
        """Updates the current project by adding a hierarchical structure of header objects to all source files"""
        project: Project = self.__model.current_project
        self.command_getter = CompileCommandGetter(project.working_dir)

        for source_file in project.source_files:
            self.__set_compile_command(source_file)
            self.__update_headers(source_file)
        return False

    class __HeaderDepthWrapper:
        def __init__(self, header: Header, depth: int):
            self.header: Header = header
            self.depth: int = depth

    def __set_compile_command(self, source_file: SourceFile) -> None:
        compile_command: str = self.command_getter.get_compile_command(
            source_file)
        source_file.compile_command = compile_command

    def __update_headers(self, source_file: SourceFile) -> None:
        hierarchy_command: str = self.command_getter.generate_hierarchy_command(
            source_file)
        hierarchy_result: str = self.__gcc_command_executor.execute(
            hierarchy_command)

        lines_to_append: List[str] = list()
        for line in hierarchy_result.splitlines():
            if line.startswith(".") and line.endswith(".h"):
                lines_to_append.append(line)
        hierarchy: List[HierarchyFetcher.__HeaderDepthWrapper] = []
        for line in lines_to_append:
            self.__append_header_recursive(line, hierarchy, source_file)

    def __append_header_recursive(self, line: str, hierarchy: List[__HeaderDepthWrapper], source_file: SourceFile) -> None:
        line_depth: int = self.__get_depth(line)
        path: str = self.__get_path_from_line(line)
        if not hierarchy:
            new_header:  Header = self.__append_header_to_file(
                source_file, path)
            hierarchy.append(self.__HeaderDepthWrapper(new_header, line_depth))
        elif line_depth > hierarchy[-1].depth:
            new_header: Header = self.__append_header_to_file(
                hierarchy[-1].header, path)
            hierarchy.append(self.__HeaderDepthWrapper(new_header, line_depth))
        else:
            hierarchy.pop()
            self.__append_header_recursive(line, hierarchy, source_file)

    def __append_header_to_file(self, cfile: CFile, new_header_path: str) -> Header:
        new_header = Header(new_header_path)
        cfile.header.append(new_header)
        return new_header

    def __get_depth(self, line: str) -> int:
        index: int = 0
        while line[index] == ".":
            index += 1
        return index

    def __get_path_from_line(self, line: str) -> str:
        out: str = line.strip(". ")
        return out
