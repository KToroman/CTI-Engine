import unittest
from datetime import datetime
import time
from src.model.core.CFile import CFile
from src.model.core.DataEntry import DataEntry
from src.model.core.Metric import Metric
from src.model.core.MetricName import MetricName


class TestCFile(unittest.TestCase):
    def setUp(self):
        self.cfile = CFile("test_path")
        self.metric_name = MetricName.CPU

    def test_get_name(self):
        self.assertEqual(self.cfile.get_name(), "test_path")

    def test_get_total_time_empty_entries(self):
        self.assertEqual(self.cfile.get_total_time(), 0)

    def test_get_total_time(self):
        timestamp1 = datetime.timestamp(datetime.now())
        time.sleep(0.1)
        timestamp2 = datetime.timestamp(datetime.now())
        data_entry1 = DataEntry("test_path", timestamp1, [Metric(10, self.metric_name)])
        data_entry2 = DataEntry("test_path", timestamp2, [Metric(10, self.metric_name)])
        self.cfile.data_entries = [data_entry1, data_entry2]
        self.assertAlmostEqual(self.cfile.get_total_time(), timestamp2 - timestamp1, delta=0.01)

    def test_get_max_empty_entries(self):
        self.assertEqual(self.cfile.get_max(self.metric_name), 0)

    def test_get_max(self):
        metric_value1 = 10
        metric_value2 = 20
        data_entry1 = DataEntry("test_path", datetime.timestamp(datetime.now()), [Metric(metric_value1, self.metric_name)])
        data_entry2 = DataEntry("test_path", datetime.timestamp(datetime.now()), [Metric(metric_value2, self.metric_name)])
        self.cfile.data_entries = [data_entry1, data_entry2]
        self.assertEqual(self.cfile.get_max(self.metric_name), metric_value2)

    def test_get_metrics_empty_entries(self):
        self.assertEqual(self.cfile.get_metrics(self.metric_name), [])

    def test_get_metrics(self):
        metric_value1 = 10
        metric_value2 = 20
        data_entry1 = DataEntry("test_path", datetime.timestamp(datetime.now()), [Metric(metric_value1, self.metric_name)])
        data_entry2 = DataEntry("test_path", datetime.timestamp(datetime.now()), [Metric(metric_value2, self.metric_name)])
        self.cfile.data_entries = [data_entry1, data_entry2]
        self.assertEqual(self.cfile.get_metrics(self.metric_name), [metric_value1, metric_value2])

    def test_get_header_by_name(self):
        header_name = "test_header"
        header = CFile(header_name)
        self.cfile.headers.append(header)
        self.assertEqual(header_name, self.cfile.headers[-1].get_name())

    def test_get_timestamps_empty_entries(self):
        self.assertEqual(self.cfile.get_timestamps(), [])

    def test_get_timestamps(self):
        timestamp1 = datetime.timestamp(datetime.now())
        time.sleep(0.1)
        timestamp2 = datetime.timestamp(datetime.now())
        data_entry1 = DataEntry("test_path", timestamp1, [Metric(10, self.metric_name)])
        data_entry2 = DataEntry("test_path", timestamp2, [Metric(20, self.metric_name)])
        self.cfile.data_entries = [data_entry1, data_entry2]
        self.assertEqual(self.cfile.get_timestamps(), [timestamp1, timestamp2])

    def test_get_headers(self):
        header1 = CFile("header1")
        header2 = CFile("header2")
        self.cfile.headers = [header1, header2]
        self.assertEqual(self.cfile.get_headers(), [header1, header2])

    def test_has_header(self):
        self.assertFalse(self.cfile.has_header())
        self.cfile.error = True
        self.assertTrue(self.cfile.has_header())
