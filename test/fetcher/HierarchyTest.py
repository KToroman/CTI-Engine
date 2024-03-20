import json
import unittest
from multiprocessing import Event, Queue

from src.fetcher.hierarchy_fetcher.HierarchyFetcher import HierarchyFetcher
from src.model.Model import Model
from src.model.core.Project import Project


class HierarchyTest(unittest.TestCase):

    def setUp(self):
        self.model = Model()
        self.project = Project("/common/homes/students/uruoe_sauer/code/axiiWorkspace2/simox", "simox")

        self.fetching_event = Event()
        self.shutdown_event = Event()
        self.source_file_queue = Queue()
        self.pid_queue = Queue()

        self.hierarchy_fetcher = HierarchyFetcher(self.fetching_event, self.shutdown_event, self.source_file_queue, self.pid_queue, max_workers=50)
        self.hierarchy_fetcher.project = self.project

        self.compile_commands_json = json.load(open("/common/homes/students/uruoe_sauer/code/axiiWorkspace2/simox/build/compile_commands.json"))

    def tearDown(self):
        self.shutdown_event.set()
        self.fetching_event.clear()
        self.hierarchy_fetcher.__del__()
        self.source_file_queue.close()
        self.pid_queue.close()

    def test_sourcefile_creation(self):
        self.hierarchy_fetcher.update_project()

        self.assertEqual(len(self.project.source_files), len(self.compile_commands_json))

    def test_hierarchy_creation(self):
        self.fetching_event.set()
        self.hierarchy_fetcher.update_project()
        total_headers = sum(len(sourcefile.headers) for sourcefile in self.project.source_files)
        self.assertGreater(total_headers, 0)

