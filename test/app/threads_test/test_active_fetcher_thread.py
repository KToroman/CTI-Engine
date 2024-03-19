from logging import shutdown
from multiprocessing import Event, Lock, Queue
from threading import Thread
import time
import pytest
from src.app.Threads.ActiveFetcherThread import ActiveFetcherThread

from src.model.Model import Model
from PyQt5.QtCore import pyqtSignal
from unittest import mock
from unittest.mock import MagicMock
from src.model.core.Project import Project

from src.model.core.SourceFile import SourceFile

    

shutdown = Event()
model: Model = Model()
model_lock = Lock()
sourcefile_queue = Queue()
error_queue = Queue()
build_dir_path = "test/builds"
active_measurement_active = Event()
saver_queue = Queue()
save_path = "test/saves"
visualize_signal = pyqtSignal()
vizualize_queue = Queue()

@pytest.fixture
def active_fetcher_thread() -> ActiveFetcherThread:
    
    model: Model = Model()
    model_lock = Lock()

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
    actv_fetch_thread.__thread = Thread()
    return actv_fetch_thread


def test_run(active_fetcher_thread):
    shutdown.clear()
    active_fetcher_thread.__shutdown_event = shutdown
    active_fetcher_thread.start()
    shutdown.set()
    time.sleep(0.5)
    assert not active_fetcher_thread.__thread.is_alive()

def test_start_new_measurement(active_fetcher_thread):
    active_fetcher_thread.measure_source_file = MagicMock(return_value = True)
    
    
