from multiprocessing import Lock
from typing import List, Tuple

from rocksdict import Rdict
from src.model.DataBaseEntry import DataBaseEntry
from src.model.Model import Model
from src.model.core.Metric import Metric
from src.model.core.MetricName import MetricName
from src.model.core.Project import Project
from src.saving.SaveToDatabase import SaveToDatabase


def test_db():
    path = "DataBaseTest"
    model = Model()
    saver = SaveToDatabase("saves", Lock(), model)
    saver.__saves_path = "saves"
    saves_path = saver.__saves_path
    delta: List[DataBaseEntry] = list()
    metrics: List[Metric] = [Metric(40, MetricName.RAM), Metric(300, MetricName.CPU)]
    delta.append(DataBaseEntry("testfile", "", "", 0.6, metrics))
    project: Project = Project(path, "project_name", "")
    model.add_project(project, None)
    project.delta_entries = delta
    saver.save_project(project.name)
    saves_path = saver.__saves_path
    db = Rdict("saves/project_name/project_name_DataBase")
    value: Tuple[float, List[Metric]] = db["testfile" + "\n" + ""]  # type: ignore
    assert value[0] == 0.6
    print(f"correct timestamp = {value[0]} was saved")
    first_metric: Metric = value[1][0]
    assert first_metric.value == 40
    assert first_metric.name == MetricName.RAM
    print("correct metric was saved")
    db.close()
    print("[basic save test]    passed")


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
    test_split()
    print("[SaveToDataBaseTest]     concluded tests")
