import time
import unittest, jsonpickle, os

from src.builder.BuilderInterface import BuilderInterface
from src.builder.header_builder.CompilingTool import CompilingTool
from src.model.Model import Model
from src.model.core.Project import Project
from src.model.core.SourceFile import SourceFile

BUILD_PATH: str = "/common/homes/students/uruoe_sauer/Documents/PSE/Building"
class BuilderTest(unittest.TestCase):
    def setUp(self):
        self.model: Model = Model()
        with open("/common/homes/students/uruoe_sauer/Documents/PSE/simox_2024-03-14_2/simox_2024-03-14_2.json", "r") as projfile:
            self.project: Project = jsonpickle.loads(projfile.read())
        self.model.add_project(self.project, None)

    def setup_source_file(self, source_file: SourceFile):
        self.source_file: SourceFile = source_file
        self.assertIn(source_file, self.project.source_files, "sourcefile not found in project")
        self.builder: BuilderInterface = CompilingTool(self.project.working_dir, source_file, BUILD_PATH)

    @unittest.skip
    def test_all_source_files(self):
        for source_file in self.project.source_files:
            self.test_single_source_file(source_file)

    def test_single_source_file(self, source_file: SourceFile = None):
        if source_file is None:
            source_file = self.project.source_files[3]
        self.setup_source_file(source_file)
        if source_file.headers:
            while self.__build_header():
                print("check")
                pass
        with self.assertRaises(IndexError):
            self.builder.get_next_header()

    def __build_header(self) -> bool:

        header = self.builder.get_next_header()
        self.assertIsNotNone(header, "header is none")
        out = self.builder.build()

        time.sleep(3)

        sf_build_dir: str = self.source_file.get_name().replace("/", "#")
        header_cpp_name: str = header.get_name().replace("/", "#") + ".cpp"
        self.assertIn(sf_build_dir,
                      [f.name for f in os.scandir(BUILD_PATH + "/Active_Mode_Build/temp")],
                      "SF build directory not created")
        self.assertIn(header_cpp_name,
                      [f.name for f in os.scandir(BUILD_PATH + "/Active_Mode_Build/temp/" + sf_build_dir)],
                      "header build .cpp file not created")
        with open(BUILD_PATH + "/Active_Mode_Build/temp/" + sf_build_dir + "/" + header_cpp_name, "r") as cppfile:
            self.assertIn(header.get_name(), cppfile.read(), "header not referenced in build file")

        if not header.error:
            self.assertIn(header_cpp_name + ".o",
                          [f.name for f in os.scandir(BUILD_PATH + "/Active_Mode_Build/temp/" + sf_build_dir)],
                          "header object .o file not created")

        return out
