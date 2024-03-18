import json
import time
import unittest
from multiprocessing import Event, Queue

from src.app.Threads.HierarchyProcess import HierarchyProcess
from src.fetcher.hierarchy_fetcher.HierarchyFetcher import HierarchyFetcher
from src.model.Model import Model
from src.model.core.Project import Project

class HierarchyProcessTest(unittest.TestCase):

    def setUp(self):
        print("in setup")
        self.model = Model()
        self.project = Project("/common/homes/students/uruoe_sauer/code/axiiWorkspace2/simox", "simox")

        self.fetching_event = Event()
        self.shutdown_event = Event()
        self.source_file_queue = Queue()
        self.pid_queue = Queue()
        self.error_queue = Queue()
        self.work_queue = Queue()
        print("check1")
        self.hierarchy_fetcher = HierarchyFetcher(self.fetching_event, self.shutdown_event, self.source_file_queue, self.pid_queue, max_workers=50)
        print("check2")
        self.compile_commands_json = json.load(open("/common/homes/students/uruoe_sauer/code/axiiWorkspace2/simox/build/compile_commands.json"))
        print("check3")
        self.hierarchy_process = HierarchyProcess(self.shutdown_event, self.hierarchy_fetcher, self.error_queue, self.work_queue, self.fetching_event)
        self.hierarchy_process.start()
        print("check4")

    def tearDown(self):
        self.fetching_event.clear()
        self.shutdown_event.set()
        self.source_file_queue.close()
        self.pid_queue.close()
        self.error_queue.close()
        self.work_queue.close()
        self.hierarchy_process.stop()

    def test_make_hierarchy(self):
        print("in test")
        self.fetching_event.set()
        self.work_queue.put(self.project)
        print("waiting")

        time.sleep(20)


        total_headers = sum(len(sourcefile.headers) for sourcefile in self.project.source_files)
        self.assertGreater(total_headers, 0)
