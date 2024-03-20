import threading
import time
import unittest
from io import StringIO
from unittest.mock import Mock, MagicMock
from multiprocessing import Event, Queue
from multiprocessing.synchronize import Event as SyncEvent, Lock as SyncLock
import random

import psutil

from src.fetcher.process_fetcher.PassiveDataFetcher import PassiveDataFetcher
from src.fetcher.process_fetcher.Threads.PassiveDataCollectionThread import PassiveDataCollectionThread
from src.fetcher.process_fetcher.process_observer.metrics_observer.DataObserver import DataObserver
from src.model.Model import Model
from src.model.core.DataEntry import DataEntry
from src.model.core.Metric import Metric
from src.model.core.MetricName import MetricName
from src.model.core.Project import Project
from src.model.core.SourceFile import SourceFile

total_metric_accesses: int = 0

class PassiveDataCollectionThreadMock:
    def __init__(self):
        self.time_till_false = 0

    def __call__(self, *args, **kwargs):
        self.__model = args[2]
        return self

    def start(self):
        pass
    def stop(self):
        pass
    def has_work(self) -> bool:
        return False
    def add_work(self):
        if self.__model.current_project.source_files and random.random() > 0.5:
            sourcefile = random.choice(self.__model.current_project.source_files)
        else:
            sourcefile = SourceFile(f"test_path_{random.randint(1, 1000)}.o")
        self.__model.insert_datapoint(DataEntry(
            sourcefile.path, time.time(), [Metric(random.random(), MetricName.CPU), Metric(random.random(), MetricName.RAM)]))
        self.time_till_false = time.time() + 35

class ProcessFindingThreadMock:
    def __init__(self):
        pass
    def __call__(self, *args, **kwargs):
        self.collector = args[1][0]
        return self
    def start(self):
        pass
    def stop(self):
        pass
    def set_work(self, pid_list):
        self.collector.add_work()

class ProcessCollectorThreadMock:
    def __init__(self):
        self.time_till_false = 0
    def __call__(self, *args, **kwargs):
        self.model = args[2]
        self.fetcher = args[5][0]
        return self
    def start(self):
        pass
    def stop(self):
        pass
    def add_work(self):
        if self.model.current_project is None:
            self.model.add_project(Project("test_dir", "test_name", "test_save_path"), Mock())
        self.fetcher.add_work()
        self.time_till_false = time.time() + 45

class ProcessMock:
    def __init__(self):
        self.index = 0
    def __call__(self, *args, **kwargs):
        return self
    def cpu_percent(self):
        global total_metric_accesses
        total_metric_accesses += 1
        return random.random() + 1
    def memory_info(self):
        mock = MagicMock()
        mock.configure_mock(vms=1000000)
        return mock
    def cwd(self):
        return "test_dir"
    def is_running(self):
        return True
    def cmdline(self):
        self.index += 1
        return ["g++", "-arg1", "-arg2", f"test_file_{self.index % 10}.o"]

class PopenMock:
    def __call__(self, *args, **kwargs):
        self.stdout = StringIO("1 name")
        return self


class TestPassiveFetcher(unittest.TestCase):
    def setUp(self):
        self.model = Model()
        self.model_lock = threading.Lock()
        self.shutdown_event: Event = Event()
        self.passive_mode_event: Event = Event()
        self.passive_mode_event.set()
        self.fetcher = PassiveDataFetcher(model=self.model,
                                          model_lock=self.model_lock,
                                          saver_queue=Mock(),
                                          hierarchy_queue=Mock(),
                                          shutdown=self.shutdown_event,
                                          save_path="",
                                          project_queue=Mock(),
                                          finished_event=Mock(),
                                          project_finished_event=Mock(),
                                          passive_mode_event=self.passive_mode_event,
                                          pid_queue=Queue(),
                                          process_finder_count=1)

    def tearDown(self):
        self.shutdown_event.set()

    @unittest.mock.patch("src.fetcher.process_fetcher.PassiveDataFetcher.ProcessCollectorThread", new_callable=ProcessCollectorThreadMock)
    @unittest.mock.patch("src.fetcher.process_fetcher.PassiveDataFetcher.ProcessFindingThread", new_callable=ProcessFindingThreadMock)
    @unittest.mock.patch("src.fetcher.process_fetcher.PassiveDataFetcher.PassiveDataCollectionThread", new_callable=PassiveDataCollectionThreadMock)
    def test_update_project(self, mock1, mock2, mock3):
        self.fetcher.start()
        for i in range(10):
            self.fetcher.update_project()
        self.shutdown_event.set()
        self.fetcher.stop()
        self.assertTrue(sum([len(sf.data_entries) for sf in self.model.current_project.source_files]) > 0)
        self.assertTrue(self.model.current_project.source_files.__len__() > 3)
        self.assertTrue(self.model.current_project.name == "test_name")

    @unittest.mock.patch("psutil.Process", new_callable=ProcessMock)
    @unittest.mock.patch("subprocess.Popen", new_callable=PopenMock)
    def test_fetch(self, psutilmock, popenmock):
        self.fetcher.start()
        for i in range(200):
            self.fetcher.update_project()
            time.sleep(0.1)
        self.shutdown_event.set()
        self.fetcher.stop()
        self.assertEquals(len(self.model.projects), 1)
        for source_file in self.model.current_project.source_files:
            self.assertTrue(len(source_file.data_entries) > 0)
            self.assertTrue(min([entry.metrics[0].value for entry in source_file.data_entries]) >= 1)
            self.assertTrue(max([entry.metrics[0].value for entry in source_file.data_entries]) < 2)
        self.assertEquals(sum([len(sf.data_entries) for sf in self.model.current_project.source_files]), total_metric_accesses)
        self.assertEquals(self.model.current_project.source_files.__len__(), 10)
        self.assertTrue(self.model.current_project.name == "test_dir_2024-03-20")


if __name__ == "__main__":
    unittest.main()
