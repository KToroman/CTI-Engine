import concurrent.futures
import threading
import time
from multiprocessing import Queue
from subprocess import CalledProcessError
from concurrent.futures import ThreadPoolExecutor, Future
from multiprocessing.synchronize import Event as SyncEvent
from multiprocessing.synchronize import Lock as SyncLock


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

    def __init__(
        self,
        hierarchy_fetching_event: SyncEvent,
        shutdown_event: SyncEvent,
        source_file_queue: Queue,
        pid_queue: Queue,
        max_workers,
    ) -> None:
        self.source_file_queue = source_file_queue
        self.__gcc_command_executor: GCCCommandExecutor = GCCCommandExecutor(pid_queue)
        self.command_getter: CompileCommandGetter
        self.__open_timeout: int = 0
        self.__hierarchy_fetching_event = hierarchy_fetching_event
        self.__shutdown_event = shutdown_event
        self.project: Project
        self.worker_thread_pool: ThreadPoolExecutor = ThreadPoolExecutor(
            max_workers=max_workers, thread_name_prefix="hierarchy_worker"
        )

    def update_project(self) -> bool:
        """Updates the current project by adding a hierarchical structure of header objects to all source files
        Returns True if this method should be called again"""

        try:
            self.command_getter = CompileCommandGetter(self.project.working_dir)
            self.__open_timeout = 0
        except FileNotFoundError as e:
            time.sleep(15)
            if self.__open_timeout > 2:
                self.__open_timeout = 0
                self.source_file_queue.put(SourceFile(self.project.name))
                raise e
            else:
                self.__open_timeout += 1
                return True

        self.source_file_queue.put(SourceFile(self.project.name))
        self.__setup_hierarchy(self.project)
        self.source_file_queue.put(SourceFile("fin"))
        self.project = None
        return False

    def __setup_hierarchy(self, project: Project) -> None:
        """the main Method of the Hierarchy Fetcher class"""
        source_files: list[SourceFile] = self.__setup_source_files(project)
        print(
            f"\033[96m [HierarchyFetcher]     {len(source_files)} Sourcefiles added to Project\033[0m"
        )
        source_files_retry: list[SourceFile] = []
        futures: dict[Future, SourceFile] = {}
        failed_source_files: int = 0
        for source_file in source_files:
            if (
                not self.__hierarchy_fetching_event.is_set()
            ) or self.__shutdown_event.is_set():
                return
            try:
                self.__set_compile_command(source_file)
                futures[
                    self.worker_thread_pool.submit(
                        self.__generate_header_result, source_file
                    )
                ] = source_file
            except CompileCommandError as e:
                source_file.error = True
                failed_source_files += 1
            except CalledProcessError as e:
                source_files_retry.append(source_file)

        for future in concurrent.futures.as_completed(futures):
            if (
                not self.__hierarchy_fetching_event.is_set()
            ) or self.__shutdown_event.is_set():
                return
            try:
                self.__update_headers(futures[future], future.result())
            except CompileCommandError as e:
                futures[future].error = True
                failed_source_files += 1
            except CalledProcessError as e:
                source_files_retry.append(futures[future])

        print(
            f"\033[96m [HierarchyFetcher]     Retry making Hierarchy for {len(source_files_retry)} Sourcefiles\033[0m"
        )
        futures = {}
        for source_file in source_files_retry:
            if (
                not self.__hierarchy_fetching_event.is_set()
            ) or self.__shutdown_event.is_set():
                return
            try:
                # self.__set_compile_command(source_file)
                futures[
                    self.worker_thread_pool.submit(
                        self.__generate_header_result, source_file
                    )
                ] = source_file
            except CompileCommandError as e:
                source_file.error = True
                failed_source_files += 1
                continue
            except CalledProcessError as e:
                source_file.error = True
                failed_source_files += 1
                continue
        for future in concurrent.futures.as_completed(futures):
            if (
                not self.__hierarchy_fetching_event.is_set()
            ) or self.__shutdown_event.is_set():
                return
            try:
                self.__update_headers(futures[future], future.result())
            except CompileCommandError as e:
                futures[future].error = True
                failed_source_files += 1
            except CalledProcessError as e:
                futures[future].error = True
                failed_source_files += 1
        print(
            f"\033[96m [HierarchyFetcher]     Hierarchy Fetching completed. {failed_source_files} files failed\033[0m"
        )

    def __setup_source_files(self, project: Project) -> list[SourceFile]:
        created_source_files: list[SourceFile] = []
        for opath in self.command_getter.get_all_opaths():
            created_source_files.append(project.get_sourcefile(opath))
        return created_source_files

    def __generate_header_result(self, source_file: SourceFile) -> str:
        hierarchy_command: str = self.command_getter.generate_hierarchy_command(
            source_file
        )
        hierarchy_result: str = self.__gcc_command_executor.execute(hierarchy_command)
        return hierarchy_result

    def __set_compile_command(self, source_file: SourceFile) -> None:
        old_compile_command: str = source_file.compile_command
        if old_compile_command == "":
            compile_command: str = self.command_getter.get_compile_command(source_file)
            source_file.compile_command = compile_command

    def __update_headers(self, source_file: SourceFile, hierarchy_result: str) -> bool:
        lines_to_append: list[str] = list()
        for line in hierarchy_result.splitlines():
            if line.startswith("."):
                lines_to_append.append(line)
        hierarchy: list[tuple[Header, int]] = []
        for line in lines_to_append:
            self.__append_header_recursive(line, hierarchy, source_file)
        self.source_file_queue.put(source_file)
        return True

    def __append_header_recursive(
        self, line: str, hierarchy: list[tuple[Header, int]], source_file: SourceFile
    ) -> None:
        line_depth: int = self.__get_depth(line)
        path: str = self.__get_path_from_line(line)
        if not hierarchy:
            new_header: Header = self.__append_header_to_file(source_file, path)
            hierarchy.append((new_header, line_depth))
        elif line_depth > hierarchy[-1][1]:
            new_header: Header = self.__append_header_to_file(hierarchy[-1][0], path)
            hierarchy.append((new_header, line_depth))
        else:
            hierarchy.pop()
            self.__append_header_recursive(line, hierarchy, source_file)

    def __append_header_to_file(self, cfile: CFile, new_header_path: str) -> Header:
        new_header = Header(new_header_path, parent=cfile)
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

    def __del__(self) -> None:
        self.worker_thread_pool.shutdown(wait=True, cancel_futures=True)
