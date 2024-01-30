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

    def test_insert_datapoints_for_existing_cfile(self):
        self.maxDiff = None
        test_model: Model = Model()
        test_project: Project = Project("", 123, "")
        test_project.get_sourcefile("test_cfile")
        test_metrics: List[Metric] = [Metric(10, MetricName.CPU), Metric(10, MetricName.RAM)]
        test_entry_1: DataEntry = DataEntry("test_cfile", 2, test_metrics)
        test_entry_2: DataEntry = DataEntry("test_cfile", 3, test_metrics)
        test_entry_list: List[DataEntry] = [test_entry_1, test_entry_2]
        test_model.add_project(test_project)

        test_model.insert_datapoints(test_entry_list)
        test_result: CFile = test_model.current_project.source_files[0]
        test_cfile: CFile = SourceFile("test_cfile")
        test_cfile.data_entries.extend(test_entry_list)

        self.assertEqual(jsonpickle.encode(test_result), jsonpickle.encode(test_cfile))

    def test_insert_datapoints_for_non_existing_cfile(self):
        self.maxDiff = None
        test_model: Model = Model()
        test_project: Project = Project("", 123, "")
        test_metrics: List[Metric] = [Metric(10, MetricName.CPU), Metric(10, MetricName.RAM)]
        test_entry_1: DataEntry = DataEntry("test_cfile", 2, test_metrics)
        test_entry_2: DataEntry = DataEntry("test_cfile", 3, test_metrics)
        test_entry_list: List[DataEntry] = [test_entry_1, test_entry_2]
        test_model.add_project(test_project)

        test_model.insert_datapoints(test_entry_list)
        test_result: CFile = test_model.current_project.source_files[0]
        test_cfile: CFile = SourceFile("test_cfile")
        test_cfile.data_entries.extend(test_entry_list)

        self.assertEqual(jsonpickle.encode(test_result), jsonpickle.encode(test_cfile))

    def test_add_project(self):
        test_model: Model = Model()
        test_project: Project = Project("", 123, "")
        test_model.projects.append(test_project)

        test_result: Model = Model()
        test_result.add_project(test_project)

        self.assertEqual(jsonpickle.encode(test_result.projects[0]), jsonpickle.encode(test_project))

    def test_current_project(self):
        test_model: Model = Model()
        test_project: Project = Project("", 123, "")
        test_model.projects.append(test_project)

        test_result: Model = Model()
        test_result.add_project(Project("", 1234, ""))
        test_result.add_project(test_project)

        self.assertEqual(jsonpickle.encode(test_result.current_project), jsonpickle.encode(test_project))

    def test_get_sourcefile_by_name(self):
        pass

    def test_get_project_name(self):
        pass

    def test_get_cfiles(self):
        pass

    def test_two_projects(self):
        pass

