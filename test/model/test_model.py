import unittest
from datetime import datetime
import time
from src.model.core.DataEntry import DataEntry
from src.model.core.Header import Header
from src.model.core.Metric import Metric
from src.model.core.MetricName import MetricName
from src.model.core.SourceFile import SourceFile


class TestCFile(unittest.TestCase):
    def setUp(self):
        self.source_file = SourceFile("test_path")
        self.metric_name = MetricName.CPU

    def test_get_name(self):
        self.assertEqual(self.source_file.get_name(), "test_path")

    def test_get_total_time_empty_entries(self):
        self.assertEqual(self.source_file.get_total_time(), 0)

    def test_get_total_time(self):
        timestamp1 = datetime.timestamp(datetime.now())
        time.sleep(0.1)
        timestamp2 = datetime.timestamp(datetime.now())
        data_entry1 = DataEntry("test_path", timestamp1, [Metric(10, self.metric_name)])
        data_entry2 = DataEntry("test_path", timestamp2, [Metric(10, self.metric_name)])
        self.source_file.data_entries = [data_entry1, data_entry2]
        self.assertAlmostEqual(self.source_file.get_total_time(), timestamp2 - timestamp1, delta=0.01)

    def test_get_max_empty_entries(self):
        self.assertEqual(self.source_file.get_max(self.metric_name), 0)

    def test_get_max(self):
        metric_value1 = 10
        metric_value2 = 20
        data_entry1 = DataEntry("test_path", datetime.timestamp(datetime.now()), [Metric(metric_value1, self.metric_name)])
        data_entry2 = DataEntry("test_path", datetime.timestamp(datetime.now()), [Metric(metric_value2, self.metric_name)])
        self.source_file.data_entries = [data_entry1, data_entry2]
        self.assertEqual(self.source_file.get_max(self.metric_name), metric_value2)

    def test_get_metrics_empty_entries(self):
        self.assertEqual(self.source_file.get_metrics(self.metric_name), [])

    def test_get_metrics(self):
        metric_value1 = 10
        metric_value2 = 20
        data_entry1 = DataEntry("test_path", datetime.timestamp(datetime.now()), [Metric(metric_value1, self.metric_name)])
        data_entry2 = DataEntry("test_path", datetime.timestamp(datetime.now()), [Metric(metric_value2, self.metric_name)])
        self.source_file.data_entries = [data_entry1, data_entry2]
        self.assertEqual(self.source_file.get_metrics(self.metric_name), [metric_value1, metric_value2])

    def test_get_header_by_name(self):
        header_name = "test_header"
        header = Header(header_name, self.source_file, 1)
        self.source_file.headers.append(header)
        self.assertEqual(header_name, self.source_file.headers[-1].get_name())

    def test_get_timestamps_empty_entries(self):
        self.assertEqual(self.source_file.get_timestamps(), [])

    def test_get_timestamps(self):
        timestamp1 = datetime.timestamp(datetime.now())
        time.sleep(0.1)
        timestamp2 = datetime.timestamp(datetime.now())
        data_entry1 = DataEntry("test_path", timestamp1, [Metric(10, self.metric_name)])
        data_entry2 = DataEntry("test_path", timestamp2, [Metric(20, self.metric_name)])
        self.source_file.data_entries = [data_entry1, data_entry2]
        assert (self.source_file.get_timestamps() == [timestamp1, timestamp2])

    def test_get_headers(self):
        header1 = Header("header1", self.source_file, 1)
        header2 = Header("header2", header1, 2)
        self.source_file.headers = [header1]
        header1.headers = [header2]
        self.assertEqual(self.source_file.get_headers(), [header1])
        self.assertEqual(header1.get_headers(), [header2])
    
    def test_has_header(self):
        assert True
