import multiprocessing
from multiprocessing import Queue
from queue import Queue
from unittest.mock import MagicMock, patch

import pytest
from PyQt5.QtCore import QSize
from PyQt5.QtWidgets import QPushButton, QInputDialog, QAbstractButton

from src.app.App import App
from src.model.Model import Model
from src.view.GUI.prepare_gui import prepare_gui


@pytest.fixture
def app():
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

    test_app = App(shutdown_event=shutdown_event, passive_mode_event=passive_mode_event,
                   load_event=load_event, load_path_queue=load_path_queue,
                   source_file_name_queue=source_file_name_queue,
                   visualize_signal=visualize_signal, error_queue=error_queue, error_signal=error_signal,
                   status_queue=status_queue,
                   project_queue=project_queue, cancel_event=cancel_event, restart_event=restart_event,
                   status_signal=status_signal, model=model)

    return [test_app, test_gui]


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


def test_button_click_sets_signal(qtbot, gui, menu_bar):
    menu_bar.load_file_button.click()


def test_update_scrollbar(menu_bar):
    # Test that the scroll_layout is initially empty
    assert menu_bar.scroll_layout.count() == 0

    # Create a list of project names
    project_names = ["Project 1", "Project 2", "Project 3"]

    # Call the update_scrollbar method
    menu_bar.update_scrollbar(project_names)

    # Test that the scroll_layout now contains the correct number of widgets
    assert menu_bar.scroll_layout.count() == len(project_names)

    # Test that each widget is a QPushButton
    for i in range(menu_bar.scroll_layout.count()):
        widget = menu_bar.scroll_layout.itemAt(i).widget()
        assert isinstance(widget, QPushButton)

    # Test that each widget has the correct text
    for i in range(menu_bar.scroll_layout.count()):
        widget = menu_bar.scroll_layout.itemAt(i).widget()
        name = project_names[i].split(" ")[0]
        assert widget.text() == name

    # Test that each widget is checkable
    for i in range(menu_bar.scroll_layout.count()):
        widget = menu_bar.scroll_layout.itemAt(i).widget()
        assert isinstance(widget, QAbstractButton)

    # Test that the scroll_button is checked
    assert menu_bar.scroll_button.isCheckable() is True

    # Test that the scroll_bar is visible
    assert menu_bar.scroll_bar.isHidden() is True

    # Test that the scroll_bar has the correct maximum size
    assert menu_bar.scroll_bar.maximumSize() == QSize(135, 500)

    # Test that the scroll_bar has the correct minimum height
    assert menu_bar.scroll_bar.minimumHeight() == 200

    # Test that the scroll_bar is widget resizable
    assert menu_bar.scroll_bar.widgetResizable() is True

    # Test that the scroll_bar is initially hidden
    assert menu_bar.scroll_bar.isHidden() is True

    # Test that the scroll_button is connected to the toggle_scrollbar method
    menu_bar.scroll_button.click()

    # Test that the scroll_bar is now visible
    assert menu_bar.scroll_bar.isHidden() is False

    # Test that the scroll_button is checked
    assert menu_bar.scroll_button.isChecked() is True

    # Test that the scroll_bar has the correct maximum size
    assert menu_bar.scroll_bar.maximumSize() == QSize(135, 500)

    # Test that the scroll_bar has the correct minimum height
    assert menu_bar.scroll_bar.minimumHeight() == 200

    # Test that the scroll_bar is widget resizable
    assert menu_bar.scroll_bar.widgetResizable() is True

    # Test that the scroll_bar is initially hidden
    assert menu_bar.scroll_bar.isHidden() is False


def test_project_buttons(menu_bar, gui):
    project_names = ["a", "b", "c", "d"]
    menu_bar.update_scrollbar(project_names)
    last_button = menu_bar.scroll_layout.itemAt(menu_bar.scroll_layout.count() - 1).widget()
    assert last_button.styleSheet() == "background-color: #00FF00"

    # Assertions
    assert menu_bar.scroll_layout.count() == len(project_names)

    for i in range(menu_bar.scroll_layout.count()):
        widget = menu_bar.scroll_layout.itemAt(i).widget()
        widget.click()
        assert isinstance(widget, QPushButton)
        assert widget.styleSheet() == "background-color: #00FF00"


def test_signal_set(menu_bar, gui):
   with patch.object(gui, 'visualize') as visualize:
       menu_bar.show_input_dialog()
       visualize.assert_called_once()

