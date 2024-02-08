from threading import Thread

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
        self.command_getter: CompileCommandGetter

    def update_project(self) -> bool:
        """Updates the current project by adding a hierarchical structure of header objects to all source files"""
        project: Project = self.__model.current_project
        self.command_getter = CompileCommandGetter(project.working_dir)

        hierarchy_thread: Thread = Thread(target=self.__setup_hierarchy, args=[project], daemon=False)
        hierarchy_thread.start()
        return False

    def __setup_hierarchy(self, project: Project) -> None:
        """the main Method of the Hierarchy Fetcher class, to be called in a separate thread"""
        source_files: list[SourceFile] = self.__setup_source_files(project)
        for source_file in source_files:
            self.__set_compile_command(source_file)
            self.__update_headers(source_file)

    def __setup_source_files(self, project: Project) -> list[SourceFile]:
        created_source_files: list[SourceFile] = []
        for opath in self.command_getter.get_all_opaths():
            created_source_files.append(project.get_sourcefile(opath))
        return created_source_files

    def __set_compile_command(self, source_file: SourceFile) -> None:
        compile_command: str = self.command_getter.get_compile_command(
            source_file)
        source_file.compile_command = compile_command

    def __update_headers(self, source_file: SourceFile) -> None:
        hierarchy_command: str = self.command_getter.generate_hierarchy_command(
            source_file)
        hierarchy_result: str = self.__gcc_command_executor.execute(
            hierarchy_command)

        lines_to_append: list[str] = list()
        for line in hierarchy_result.splitlines():
            if line.startswith("."):
                lines_to_append.append(line)
        hierarchy: list[tuple[Header, int]] = []
        for line in lines_to_append:
            self.__append_header_recursive(line, hierarchy, source_file)

    def __append_header_recursive(self, line: str, hierarchy: list[tuple[Header, int]], source_file: SourceFile) -> None:
        line_depth: int = self.__get_depth(line)
        path: str = self.__get_path_from_line(line)
        if not hierarchy:
            new_header:  Header = self.__append_header_to_file(
                source_file, path)
            hierarchy.append((new_header, line_depth))
        elif line_depth > hierarchy[-1][1]:
            new_header: Header = self.__append_header_to_file(
                hierarchy[-1][0], path)
            hierarchy.append((new_header, line_depth))
        else:
            HierarchyFetcher.__HeaderDepthWrapper = hierarchy.pop()
            self.__append_header_recursive(line, hierarchy, source_file)

    def __append_header_to_file(self, cfile: CFile, new_header_path: str) -> Header:
        new_header = Header(new_header_path)
        cfile.headers.append(new_header)
        return new_header

    def __get_depth(self, line: str) -> int:
        index: int = 0
        while line[index] == ".":
            index += 1
        return index

    def __get_path_from_line(self, line: str) -> str:
        out: str = line.strip(". ")
        return out
