from multiprocessing import Lock, Queue
from typing import List, Tuple
from unittest.mock import MagicMock
from PyQt5.QtCore import pyqtSignal
from qtpy import QT5
from rocksdict import Rdict, RdictIter
from src.fetcher.file_fetcher.FileLoader import FileLoader
from src.model.DataBaseEntry import DataBaseEntry
from src.model.Model import Model
from src.model.core.Header import Header
from src.model.core.Metric import Metric
from src.model.core.MetricName import MetricName
from src.model.core.Project import Project
from src.saving.SaveToDatabase import SaveToDatabase
import pytest

path = "saves/project_name/project_name_DataBase"
def test_db():
    model = Model()
    saver = SaveToDatabase("saves", Lock(), model)
    saver.__saves_path = "saves"
    delta: List[DataBaseEntry] = list()
    metrics: List[Metric] = [Metric(40, MetricName.RAM), Metric(300, MetricName.CPU)]
    delta.append(DataBaseEntry("testfile", "parent", 0.6, metrics, 0))
    project: Project = Project(path, "project_name", "")
    model.add_project(project, None)
    project.delta_entries = delta
    saver.save_project(project.name)
    saves_path = saver.__saves_path
    db = Rdict(path)
    value: Tuple[float, List[Metric]] = db["testfile" + "\n" + "parent" + "\n" + "0"]  # type: ignore
    
    assert value[0] == 0.6
    print(f"correct timestamp = {value[0]} was saved")
    first_metric: Metric = value[1][0]
    assert first_metric.value == 40
    assert first_metric.name == MetricName.RAM
    print("correct metric was saved")
    db.close()
    print("[basic save test]    passed")

class SignalMock():
    def emit(self):
        print("signal emitted")

def test_loading():
    model = Model()
    model_lock = Lock()
    signal_mock = SignalMock()
    loader = FileLoader(path, model=model, model_lock=model_lock, visualize_signal=signal_mock, project_queue=Queue())
    loader.__path = path
    assert not loader.update_project()
    print(model.projects[0].name)
    assert model.projects[0].name == "saves/project_name/project_name"

def test_split():
    key_str: str = "source_file\nparent\n"
    paths = key_str.split("\n")
    for i in range(0, 3):
        print(paths[i])
    assert True
    print("[key splitting test]    passed")


if __name__ == "__main__":
    print("[SaveToDataBaseTest]     starting tests")
    test_db()
    test_loading()
    test_split()
    db = Rdict("/common/homes/students/upufw_toroman/PSE/saves/simox_2024-03-18/simox_2024-03-18_DataBase")
    iter: RdictIter = db.iter()
    iter.seek_to_first()
    while iter.valid():
        print("next entry")
        key = iter.key()
        value = iter.value()
        print("new item")
        iter.next()
    print("[SaveToDataBaseTest]     concluded tests")
    Rdict.destroy(path)
