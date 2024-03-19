import sys
from multiprocessing import Event, Queue
from multiprocessing.synchronize import Event as SyncEvent
from typing import List
from unittest.mock import Mock, MagicMock

import pytest
from PyQt5.QtWidgets import QApplication, QPushButton

from src.model.Model import Model
from src.model.ModelReadViewInterface import ModelReadViewInterface
from src.model.core.CFile import CFile
from src.model.core.CFileReadViewInterface import CFileReadViewInterface
from src.model.core.Header import Header
from src.model.core.MetricName import MetricName
from src.model.core.Project import Project
from src.model.core.ProjectReadViewInterface import ProjectReadViewInterface
from src.view.gui.MainWindow import MainWindow
from src.view.gui.user_interaction.MenuBar import MenuBar


class MenuBarMock(MenuBar):

    def set_project_buttons(self):
        self.project_buttons.append(QPushButton("Mock"))


class ModelMock(Model):

    def get_project_by_name(self, name: str) -> Project:
        project = ProjectMock(" ", " ")
        return project


class MainWindowMock(MainWindow):

    def get_model(self):
        return self.__model

    def set_model(self, model: ModelReadViewInterface):
        self.__model = model

class HeaderMock(Header):

    def get_name(self) -> str:
        return "Header Mock"

    def get_total_time(self) -> float:
        return 1

    def get_max(self, metric_name: MetricName) -> float:
        return 1

    def get_metrics(self, metric_name: MetricName) -> List[float]:
        return [1]

    def get_timestamps(self) -> List[float]:
        return [1]

    def get_headers(self) -> List[CFileReadViewInterface]:
        return []


class CFileMock(CFile):

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

    def get_headers(self) -> List[CFileReadViewInterface]:
        return [HeaderMock("")]


class ProjectMock(Project):

    def get_project_name(self) -> str:
        return "Mock Project Name"

    def get_cfiles(self) -> list[CFileMock]:
        return [CFileMock("")]

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

@pytest.fixture
def cfile() -> CFileMock:
    cfile = CFileMock("")
    cfile.headers = []
    return


def test_visualize_passive(main_window):
    project_mock: ProjectMock = ProjectMock(" ", " ")
    main_window.project_queue.put(project_mock)
    main_window.visualize()
    assert main_window.current_table.rows[0].displayable.name == project_mock.get_cfiles()[0].get_name()


def test_visualize_active(main_window):
    test_visualize_passive(main_window)
    main_window.current_table.start_active_measurement("Header Mock")
    """assert main_window.current_table.insertion_point = """
