import json
import threading
import time
import unittest
from multiprocessing import Event, Queue

from src.app.Threads.HierarchyProcess import HierarchyProcess
from src.app.Threads.HierarchyThread import HierarchyThread
from src.fetcher.hierarchy_fetcher.HierarchyFetcher import HierarchyFetcher
from src.model.Model import Model
from src.model.core.Project import Project
from src.model.core.ProjectFinishedSemaphore import ProjectFinishedSemaphore

print("hasjdosajdojasjflsad")

class HierarchyProcessTest(unittest.TestCase):

    def setUp(self):

        self.model = Model()
        self.project = Project("/common/homes/students/uruoe_sauer/code/axiiWorkspace2/simox", "simox")
        self.semaphore = ProjectFinishedSemaphore(self.project.working_dir, self.project.name, None, None, None, None)
        self.model.add_project(self.project, self.semaphore)

        self.model_lock = threading.Lock()

        self.fetching_event = Event()
        self.shutdown_event = Event()
        self.source_file_queue = Queue()
        self.pid_queue = Queue()
        self.error_queue = Queue()
        self.work_queue = Queue()

        self.hierarchy_fetcher = HierarchyFetcher(self.fetching_event, self.shutdown_event, self.source_file_queue, self.pid_queue, max_workers=50)

        with open("/common/homes/students/uruoe_sauer/code/axiiWorkspace2/simox/build/compile_commands.json") as jfile:
            self.compile_commands_json = json.load(jfile)

        self.hierarchy_process = HierarchyProcess(self.shutdown_event, self.hierarchy_fetcher, self.error_queue, self.work_queue, self.fetching_event)

        self.hierarchy_thread = HierarchyThread(self.shutdown_event, self.fetching_event, self.source_file_queue, self.model, self.model_lock, self.hierarchy_process, self.work_queue, self.shutdown_event)
        self.hierarchy_thread.start()


    def tearDown(self):
        self.fetching_event.clear()
        self.shutdown_event.set()
        self.source_file_queue.close()
        self.pid_queue.close()
        self.error_queue.close()
        self.work_queue.close()
        self.hierarchy_thread.stop()

    def test_make_hierarchy(self):
        print("in test")
        self.fetching_event.set()
        self.work_queue.put(self.project)
        print("waiting")

        while not self.shutdown_event.is_set():
            time.sleep(1)


        total_headers = sum(len(sourcefile.headers) for sourcefile in self.project.source_files)
        print(str([header for header in self.project.source_files]))
        self.assertGreater(total_headers, 0)


if __name__ == "__main__":
    unittest.main()