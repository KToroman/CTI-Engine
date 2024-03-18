from multiprocessing import Event, Lock, Queue
from unittest.mock import Mock
import pytest
from src.app.Threads.ActiveFetcherThread import ActiveFetcherThread

from src.model.Model import Model
from PyQt5.QtCore import pyqtSignal


@pytest.fixture
def active_fetcher_thread():
    model: Model = Model()
    model_lock = Lock()
    shutdown = Event()
    sourcefile_queue = Queue()
    error_queue = Queue()
    build_dir_path = "test/builds"
    active_measurement_active = Event()
    saver_queue = Queue()
    save_path = "test/saves"
    visualize_signal = pyqtSignal()
    vizualize_queue = Queue()

    actv_fetch_thread = ActiveFetcherThread(shutdown_event=shutdown, saver_queue=saver_queue, save_path=save_path,
                                            model=model, model_lock=model_lock, source_file_name_queue=sourcefile_queue, error_queue=error_queue,
                                            build_dir_path=build_dir_path, active_measurement_active=active_measurement_active, visualise_event=visualize_signal, visualise_project_queue=vizualize_queue)
    thread_mock = Mock()
    thread_mock.patch('__thread.start', return_value=True)
    actv_fetch_thread.__thread = thread_mock
    return actv_fetch_thread


def test_start(active_fetcher_thread):
    
    assert active_fetcher_thread.start()
    assert True
