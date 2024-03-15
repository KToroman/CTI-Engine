from typing import List

from rocksdict import Rdict
from src.model.DataBaseEntry import DataBaseEntry
from src.model.core.Metric import Metric
from src.model.core.MetricName import MetricName
from src.model.core.Project import Project
from src.saving.SaveToDatabase import SaveToDatabase


def test_db():
    path = "DataBaseTest"
    saver = SaveToDatabase("saves")
    saver.__saves_path = "saves"
    saves_path = saver.__saves_path
    delta: List[DataBaseEntry] = list()
    metrics: List[Metric] = [Metric(40, MetricName.RAM), Metric(300, MetricName.CPU)]
    delta.append(DataBaseEntry("testfile", "", 0.6, metrics))
    saver.save_project(Project(path, "project_name", ""), delta)
    saves_path = saver.__saves_path
    db = Rdict("saves/project_name/project_name_DataBase")
    value = db["testfile" + "\n" + ""]
    assert value[0] == 0.6
    print("correct timestamp (0.6) was saved")
    assert value[1][0].value == 40
    assert value[1][0].name == MetricName.RAM
    print("correct metric was saved")
    db.close()
    print("test_passed")


if __name__ == "__main__":
    print("starting tests")
    test_db()
