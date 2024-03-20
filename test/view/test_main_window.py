import sys
import time
from multiprocessing import Event, Queue
from multiprocessing.synchronize import Event as SyncEvent
from typing import List
import pytest
from PyQt5.QtWidgets import QApplication, QPushButton
from src.model.Model import Model
from src.model.ModelReadViewInterface import ModelReadViewInterface
from src.model.core.CFileReadViewInterface import CFileReadViewInterface
from src.model.core.Header import Header
from src.model.core.MetricName import MetricName
from src.model.core.Project import Project
from src.model.core.SourceFile import SourceFile
from src.view.GUI.MainWindow import MainWindow
from src.view.GUI.UserInteraction.MenuBar import MenuBar


class MenuBarMock(MenuBar):

    def set_project_buttons(self):
        self.project_buttons.append(QPushButton("Mock"))


class ModelMock(Model):

    def get_project_by_name(self, name: str) -> Project:
        return self.projects.pop()

    def set_project(self, proj: Project):
        self.projects.append(proj)


class MainWindowMock(MainWindow):

    def get_model(self) -> ModelReadViewInterface:
        return self.__model

    def set_model(self, model: ModelReadViewInterface):
        self.__model = model


class HeaderMock(Header):

    def get_name(self) -> str:
        return "Header Mock"

    def get_total_time(self) -> float:
        return 1

    def get_max(self, metric_name: MetricName) -> float:
        return float(self.path)

    def set_max(self, maximum: str):
        self.path = maximum

    def get_metrics(self, metric_name: MetricName) -> List[float]:
        return [1]

    def get_timestamps(self) -> List[float]:
        return [1]

    def get_headers(self) -> List[CFileReadViewInterface]:
        return []


class CFileMock(SourceFile):

    def get_name(self) -> str:
        return "CFile Mock"

    def get_total_time(self) -> float:
        return 1

    def get_max(self, metric_name: MetricName) -> float:
        return 1

    def get_metrics(self, metric_name: MetricName) -> List[float]:
        return [1]

    def get_timestamps(self) -> List[float]:
        return [1]

    def get_headers(self) -> List[HeaderMock]:
        return [HeaderMock(path="1", hierarchy_level=1, parent=None)]


class ProjectMock(Project):

    def get_project_name(self) -> str:
        return "Mock Project Name"

    def get_cfiles(self) -> list[CFileMock]:
        cfiles_view: List[CFileReadViewInterface] = list()
        cfiles_view.extend(self.source_files)
        return cfiles_view

    def get_project_time(self) -> float:
        return 0


@pytest.fixture
def app():
    q_application: QApplication = QApplication(sys.argv)
    return q_application


@pytest.fixture
def main_window(app) -> MainWindowMock:
    shutdown_event: SyncEvent = Event()
    cancel_event: SyncEvent = Event()
    restart_event: SyncEvent = Event()
    status_queue: Queue = Queue()
    project_queue: Queue = Queue()
    error_queue: Queue = Queue()
    load_path_queue: Queue = Queue()
    active_mode_queue: Queue = Queue()
    model: ModelReadViewInterface = ModelMock()
    main_window: MainWindowMock = MainWindowMock(q_application=app, project_queue=project_queue,
                                                 status_queue=status_queue, restart_event=restart_event,
                                                 error_queue=error_queue, load_path_queue=load_path_queue,
                                                 active_mode_queue=active_mode_queue, cancel_event=cancel_event,
                                                 shutdown_event=shutdown_event, model=model)
    main_window.set_model(model=model)
    return main_window


def test_visualize_passive(main_window):
    project_mock: ProjectMock = ProjectMock("", "Project Mock")
    project_mock.source_files.append(CFileMock(""))
    main_window.get_model().set_project(project_mock)
    main_window.project_queue.put(project_mock)
    main_window.visualize()
    assert main_window.current_table.rows[0].displayable.name == project_mock.get_cfiles()[0].get_name()
    assert main_window.current_table.rows[0].displayable.cpu_peak == project_mock.get_cfiles()[0].get_max(
        MetricName.CPU)
    assert main_window.current_table.rows[0].displayable.ram_peak == project_mock.get_cfiles()[0].get_max(
        MetricName.RAM)


def test_select_all(main_window):
    test_visualize_passive(main_window)
    main_window.select_all_checkbox.setCheckState(True)
    time.sleep(1)
    for row in main_window.current_table.rows:
        assert row.checkbox.isChecked()
    assert len(main_window.ram_graph_widget.lines) == len(main_window.current_table.rows)
    assert len(main_window.cpu_graph_widget.lines) == len(main_window.current_table.rows)
    assert len(main_window.bar_chart_widget.categories) == len(main_window.current_table.rows)


def test_select_only(main_window):
    # Mock visualize project
    project_mock: ProjectMock = ProjectMock("", "Project Mock")
    project_mock.source_files.append(CFileMock(""))
    project_mock.source_files.append(CFileMock(""))
    project_mock.source_files.append(CFileMock(""))
    project_mock.source_files.append(CFileMock(""))
    main_window.get_model().set_project(project_mock)
    main_window.project_queue.put(project_mock)
    main_window.visualize()

    # Mock updating spinboxes
    main_window.lower_limit.setValue(2)
    main_window.upper_limit.setValue(3)
    main_window.upper_limit.editingFinished.emit()

    amount_selected: int = main_window.upper_limit.value() - main_window.lower_limit.value() + 1
    for row in main_window.current_table.rows[main_window.lower_limit.value():main_window.upper_limit.value()]:
        assert row.checkbox.isChecked()
        time.sleep(0.1)
    assert len(main_window.ram_graph_widget.lines) == amount_selected
    assert len(main_window.cpu_graph_widget.lines) == amount_selected
    assert len(main_window.bar_chart_widget.categories) == amount_selected
