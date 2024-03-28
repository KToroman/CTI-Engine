import multiprocessing
import time
from multiprocessing import Queue
from queue import Queue
from unittest.mock import Mock

import pytest
from PyQt5.QtCore import pyqtSignal
from src.app.Threads.FileFetcherThread import FileFetcherThread
from src.model.Model import Model
from src.view.GUI.prepare_gui import prepare_gui


@pytest.fixture
def gui():
    model: Model = Model()
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

    return test_gui



@pytest.fixture
def menu_bar(gui):
    return gui.menu_bar


def test_loading_with_valid_path(menu_bar):
    error_queue = Queue()
    model = Model()
    model_lock = multiprocessing.Lock()
    shut_down_event = multiprocessing.Event()
    load_path_queue = menu_bar.load_path_queue
    load_event = multiprocessing.Event()
    project_queue = Queue()
    visualize_event = pyqtSignal()
    visualize_signal = Mock()
    visualize_event = visualize_signal

    file_fetcher_thread = FileFetcherThread(error_queue, model, model_lock, shut_down_event, load_path_queue,
                                            load_event, project_queue, visualize_event)
    file_loader = Mock()
    file_fetcher_thread.start()
    # test if input path triggers work in the File Loader Thread
    menu_bar.load_path_queue.put(
        "/common/homes/students/uyioc_brentel/PyCharm/pycharm-community-2023.3.1/mongocxx 2024-03-11/mongocxx 2024-03-11.json")
    time.sleep(0)
    # test if FileFetcherThread load event gets set
    assert load_event.is_set()
    # test if the loader gets triggered upon a valid path
    file_loader.update_project.called_once()
    # test if signal is being emited
    visualize_signal.emit.called_once()
    shut_down_event.set()
    file_fetcher_thread.stop()


def test_loading_with_invalid_path(menu_bar, gui):
    error_queue = Queue()
    model = Model()
    model_lock = multiprocessing.Lock()
    shut_down_event = multiprocessing.Event()
    load_path_queue = menu_bar.load_path_queue
    load_event = multiprocessing.Event()
    project_queue = Queue()
    visualize_event = pyqtSignal()
    file_fetcher_thread = FileFetcherThread(error_queue, model, model_lock, shut_down_event, load_path_queue,
                                            load_event, project_queue, visualize_event)
    file_loader_mock = Mock()
    # test if exception is being thrown when an invalid path is entered
    file_fetcher_thread.start()
    menu_bar.load_path_queue.put("abc")
    time.sleep(2)
    assert not error_queue.empty()
    shut_down_event.set()
    file_fetcher_thread.stop()
    file_loader_mock.update_project.assert_not_called()


def test_cancel(menu_bar, gui):
    # test if a cancel event triggers a status change
    menu_bar.cancel_event.set()
    time.sleep(5)
    assert gui.status_bar.counter == 1
