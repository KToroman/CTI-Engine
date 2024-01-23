from fetcher.FetcherInterface import FetcherInterface
from fetcher.hierarchy_fetcher.GCCCommandExecutor import GCCCommandExecutor
from fetcher.hierarchy_fetcher.CompileCommandGetter import CompileCommandGetter
from model.Model import Model
from model.core.Project import Project
from model.core.SourceFile import SourceFile

class HierarchyFetcher(FetcherInterface):

    def __init__(self, model: Model) -> None:
        self.__model : Model = model
        self.__gcc_command_executor : GCCCommandExecutor = GCCCommandExecutor()

    def update_project(self) -> None:
        """Updates a project by adding a hierarchical structure of header objects to all source files"""
        project : Project = self.__model.current_project
        self.command_getter : CompileCommandGetter = CompileCommandGetter(project.working_dir)

        for source_file in project.source_files:
            self.__set_compile_command(source_file)
            self.__update_headers(source_file)


    def __set_compile_command(self, source_file: SourceFile) -> None:
        compile_command : str = self.command_getter.get_compile_command(source_file)
        source_file.compile_command = compile_command

    def __update_headers(self, source_file: SourceFile) -> None:
        hierarchy_command : str = self.command_getter.generate_hierarchy_command(source_file)
        hierarchy_result: str = self.__gcc_command_executor.execute(hierarchy_command)


