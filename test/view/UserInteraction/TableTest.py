import pytest
import pytestqt
from PyQt5.QtCore import QSize
from PyQt5.QtWidgets import QPushButton, QInputDialog, QAbstractButton

from src.app.App import App
from src.app.Threads.FileFetcherThread import FileFetcherThread
from src.model.Model import Model
from src.view.GUI.prepare_gui import prepare_gui
import multiprocessing
from multiprocessing import Queue, Lock
from queue import Queue
from unittest.mock import MagicMock, patch, Mock


@pytest.fixture
def app():
    model: Model = Model()
    model_lock = Lock()
    shutdown_event = multiprocessing.Event()
    active_mode_event = multiprocessing.Event()
    passive_mode_event = multiprocessing.Event()
    passive_mode_event.set()
    load_event = multiprocessing.Event()
    # Queues for GUI messages
    load_path_queue = Queue(3)
    source_file_name_queue = Queue(1)

    error_queue: Queue = Queue(4)

    status_queue = Queue()
    project_queue = Queue()
    cancel_event = multiprocessing.Event()
    restart_event = multiprocessing.Event()

    test_gui = prepare_gui(shutdown_event=shutdown_event, status_queue=status_queue,
                           project_queue=project_queue,
                           error_queue=error_queue, load_path_queue=load_path_queue, cancel_event=cancel_event,
                           active_mode_queue=source_file_name_queue, restart_event=restart_event, model=model)
    visualize_signal = test_gui.visualize_signal
    status_signal = test_gui.status_signal
    error_signal = test_gui.error_signal

    test_app = App(shutdown_event=shutdown_event, passive_mode_event=passive_mode_event,
                   load_event=load_event, load_path_queue=load_path_queue,
                   source_file_name_queue=source_file_name_queue,
                   visualize_signal=visualize_signal, error_queue=error_queue, error_signal=error_signal,
                   status_queue=status_queue,
                   project_queue=project_queue, cancel_event=cancel_event, restart_event=restart_event,
                   status_signal=status_signal, model=model)
    file_fetcher_thread = FileFetcherThread(error_queue, model, model_lock, shutdown_event, load_path_queue, load_event,
                                            project_queue, visualize_signal)
    return [test_app, test_gui, file_fetcher_thread]


@pytest.fixture
def menu_bar(app):
    return app[1].menu_bar


@pytest.fixture
def gui(app):
    return app[1]



@pytest.fixture
def button_with_dialog():
    # Erstellen des QPushButton
    button = QPushButton()

    # Erstellen des QInputDialog
    input_dialog = QInputDialog()
    input_dialog.getText = lambda *args: ("Test", True)

    return button, input_dialog


def test_select_all_for_one_loaded_project(menu_bar, gui, app):

    gui_mock = Mock()
    gui_mock.visualize()
    gui_mock.visualize_passive.assert_called()


