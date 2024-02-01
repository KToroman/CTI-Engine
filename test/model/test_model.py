import unittest
from typing import List

import jsonpickle
import picklejson

from src.model.Model import Model
from src.model.core.CFile import CFile
from src.model.core.DataEntry import DataEntry
from src.model.core.Metric import Metric
from src.model.core.MetricName import MetricName
from src.model.core.Project import Project
from src.model.core.SourceFile import SourceFile


class TestModel(unittest.TestCase):
    test_project_1: Project = Project("", 123, "")
    test_project_2: Project = Project("", 1234, "")
    test_metrics: List[Metric] = [Metric(10, MetricName.CPU), Metric(10, MetricName.RAM)]
    test_entry_1: DataEntry = DataEntry("test_cfile", 2, test_metrics)
    test_entry_2: DataEntry = DataEntry("test_cfile", 3, test_metrics)
    test_entry_list: List[DataEntry] = [test_entry_1, test_entry_2]
    test_model: Model = Model()

    def test_insert_datapoints_for_existing_cfile(self):
        self.__clear()

        self.test_project_1.get_sourcefile("test_cfile")
        self.test_model.add_project(self.test_project_1)
        self.test_model.insert_datapoints(self.test_entry_list)
        test_result: CFile = self.test_model.current_project.source_files[0]

        test_cfile: CFile = SourceFile("test_cfile")
        test_cfile.data_entries.extend(self.test_entry_list)

        self.assertEqual(jsonpickle.encode(test_result), jsonpickle.encode(test_cfile))

    def test_insert_datapoints_for_non_existing_cfile(self):
        self.__clear()

        self.test_model.add_project(self.test_project_1)
        self.test_model.insert_datapoints(self.test_entry_list)

        test_result: CFile = self.test_model.current_project.source_files[0]
        test_cfile: CFile = SourceFile("test_cfile")
        test_cfile.data_entries.extend(self.test_entry_list)

        self.assertEqual(jsonpickle.encode(test_result), jsonpickle.encode(test_cfile))

    def test_add_project(self):
        self.__clear()
        self.test_model.add_project(self.test_project_1)

        self.assertEqual(jsonpickle.encode(self.test_model.projects[0]), jsonpickle.encode(self.test_project_1))

    def test_current_project(self):
        self.__clear()

        self.test_model.add_project(self.test_project_1)
        self.test_model.add_project(self.test_project_2)

        self.assertEqual(jsonpickle.encode(self.test_model.current_project), jsonpickle.encode(self.test_project_2))

    def test_get_sourcefile_by_name_for_existing_cfile(self):
        self.__clear()

        self.test_model.add_project(self.test_project_1)
        self.test_model.insert_datapoints(self.test_entry_list)
        test_result = self.test_model.get_sourcefile_by_name("test_cfile")

        test_cfile: CFile = SourceFile("test_cfile")
        test_cfile.data_entries.extend(self.test_entry_list)
        self.assertEqual(jsonpickle.encode(test_result), jsonpickle.encode(test_cfile))

    def test_get_sourcefile_by_name_for_non_existing_cfile(self):
        self.__clear()

        self.test_model.add_project(self.test_project_1)

        test_result = self.test_model.get_sourcefile_by_name("test_cfile")
        test_cfile: CFile = SourceFile("test_cfile")

        self.assertEqual(jsonpickle.encode(test_result), jsonpickle.encode(test_cfile))

    def test_get_project_name(self):
        pass

    def test_get_cfiles(self):
        pass

    def test_two_projects(self):
        pass

    def __clear(self):
        self.test_project_1 = Project("", 123, "")
        self.test_project_2 = Project("", 1234, "")
        self.test_metrics = [Metric(10, MetricName.CPU), Metric(10, MetricName.RAM)]
        self.test_entry_1 = DataEntry("test_cfile", 2, self.test_metrics)
        self.test_entry_2 = DataEntry("test_cfile", 3, self.test_metrics)
        self.test_entry_list = [self.test_entry_1, self.test_entry_2]
        self.test_model = Model()
