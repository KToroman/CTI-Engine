import threading
import time
from threading import Thread
from subprocess import CalledProcessError

from src.fetcher.FetcherInterface import FetcherInterface
from src.fetcher.hierarchy_fetcher.GCCCommandExecutor import GCCCommandExecutor
from src.fetcher.hierarchy_fetcher.CompileCommandGetter import CompileCommandGetter
from src.model.Model import Model
from src.model.core.Project import Project
from src.model.core.SourceFile import SourceFile
from src.model.core.CFile import CFile
from src.model.core.Header import Header
from src.exceptions.CompileCommandError import CompileCommandError


class HierarchyFetcher(FetcherInterface):

    def __init__(self, model: Model, project_name: str, model_lock: threading.Lock) -> None:
        self.__model: Model = model
        self.__model_lock = model_lock
        self.project_name = project_name
        self.__gcc_command_executor: GCCCommandExecutor = GCCCommandExecutor()
        self.command_getter: CompileCommandGetter
        self.__open_timeout: int = 0
        self.is_done: bool = False


    def update_project(self) -> bool:
        print("hierarchy update")
        """Updates the current project by adding a hierarchical structure of header objects to all source files"""
        self.__model_lock.acquire()
        project: Project = self.__model.current_project
        self.__model_lock.release()
        try:
            self.command_getter = CompileCommandGetter(project.working_dir, self.__model_lock)
            self.__open_timeout = 0
        except FileNotFoundError as e:
            time.sleep(5)
            if self.__open_timeout > 2:
                self.__open_timeout = 0
                self.is_done = True
                raise e
            else:
                self.__open_timeout += 1
                print(e.__str__() + "\n trying again...")
                return True

        self.__setup_hierarchy(project)
        self.is_done = True
        return False

    def __setup_hierarchy(self, project: Project) -> None:
        """the main Method of the Hierarchy Fetcher class, to be called in a separate thread"""
        source_files: list[SourceFile] = self.__setup_source_files(project)
        print(f"\033[96m {len(source_files)} Sourcefiles added to Project\033[0m")
        source_files_retry: list[SourceFile] = []
        for source_file in source_files:
            try:
                self.__set_compile_command(source_file)
                self.__update_headers(source_file)
            except CompileCommandError as e:
                print(f"\033[93m{e.__str__()}\033[0m")
                source_file.error = True
            except CalledProcessError as e:
                print(f"\033[93m{e.__str__()}\033[0m")
                source_files_retry.append(source_file)
        print(f"\033[96mRetry making Hierarchy for {len(source_files_retry)} Sourcefiles\033[0m")
        for source_file in source_files_retry:
            try:
                self.__set_compile_command(source_file)
                self.__update_headers(source_file)
            except (CompileCommandError, CalledProcessError) as e:
                print(f"\033[93m{e.__str__()}\033[0m")
                source_file.error = True
        print(f"\033[96mHierarchy Fetching completed\033[0m")

    def __setup_source_files(self, project: Project) -> list[SourceFile]:
        created_source_files: list[SourceFile] = []
        for opath in self.command_getter.get_all_opaths():
            self.__model_lock.acquire()
            created_source_files.append(project.get_sourcefile(opath))
            self.__model_lock.release()
        return created_source_files

    def __set_compile_command(self, source_file: SourceFile) -> None:
        compile_command: str = self.command_getter.get_compile_command(
            source_file)
        self.__model_lock.acquire()
        source_file.compile_command = compile_command
        self.__model_lock.release()

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
        self.__model_lock.acquire()
        cfile.headers.append(new_header)
        self.__model_lock.release()
        return new_header

    def __get_depth(self, line: str) -> int:
        index: int = 0
        while line[index] == ".":
            index += 1
        return index

    def __get_path_from_line(self, line: str) -> str:
        out: str = line.strip(". ")
        return out
