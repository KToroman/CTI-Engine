import sys
from multiprocessing import Queue, Event

import pytest
from PyQt5.QtWidgets import QApplication

from src.model.Model import Model
from src.model.ModelReadViewInterface import ModelReadViewInterface
from src.view.GUI.Graph.GraphWidget import GraphWidget
from src.view.GUI.Graph.Plot import Plot
from src.view.GUI.MainWindow import MainWindow
from src.view.GUI.UserInteraction.Displayable import Displayable
from src.view.GUI.UserInteraction.TreeWidget import TreeWidget


@pytest.fixture
def app():
    q_application: QApplication = QApplication(sys.argv)
    return q_application


@pytest.fixture
def tree_widget():
    active_mode_queue: Queue = Queue()
    tree_widget: TreeWidget = TreeWidget(active_mode_queue)
    return tree_widget


@pytest.fixture
def graph_widget():
    return GraphWidget("Y Axis Label")


@pytest.fixture
def main_window(app, tree_widget, graph_widget):
    shutdown_event: Event = Event()
    cancel_event: Event = Event()
    restart_event: Event = Event()
    status_queue: Queue = Queue()
    project_queue: Queue = Queue()
    error_queue: Queue = Queue()
    load_path_queue: Queue = Queue()
    active_mode_queue: Queue = Queue()
    model: ModelReadViewInterface = Model()
    main_window: MainWindow = MainWindow(q_application=app, project_queue=project_queue,
                                         status_queue=status_queue, restart_event=restart_event,
                                         error_queue=error_queue, load_path_queue=load_path_queue,
                                         active_mode_queue=active_mode_queue, cancel_event=cancel_event,
                                         shutdown_event=shutdown_event, model=model)

    main_window.current_table = tree_widget
    main_window.ram_graph_widget = graph_widget
    return main_window


def test_main_window(main_window, tree_widget, graph_widget):
    assert isinstance(main_window, MainWindow)
    assert main_window.current_table == tree_widget
    assert main_window.ram_graph_widget == graph_widget


def test_click_checkbox_shows_graph(app, main_window):
    # Insert Dummy Data
    plot_mock1: Plot = Plot(name="mock_disp1", color="#FFFFFF", x_values=[0, 0], y_values=[0, 0])
    mock_disp1: Displayable = Displayable(name="mock_disp1", ram_plot=plot_mock1, cpu_plot=plot_mock1,
                                          runtime_plot=plot_mock1, ram_peak=0, cpu_peak=0, headers=[],
                                          secondary_headers=[])
    plot_mock2: Plot = Plot(name="mock_disp2", color="#FFFFFF", x_values=[0], y_values=[0])
    mock_disp2: Displayable = Displayable(name="mock_disp2", ram_plot=plot_mock2, cpu_plot=plot_mock2,
                                          runtime_plot=plot_mock2, ram_peak=0, cpu_peak=0, headers=[],
                                          secondary_headers=[])
    plot_mock3: Plot = Plot(name="mock_disp3", color="#FFFFFF", x_values=[0], y_values=[0])
    mock_disp3: Displayable = Displayable(name="mock_disp3", ram_plot=plot_mock3, cpu_plot=plot_mock3,
                                          runtime_plot=plot_mock3, ram_peak=0, cpu_peak=0, headers=[],
                                          secondary_headers=[])
    main_window.current_table.insert_values([mock_disp1, mock_disp2, mock_disp3])
    main_window.setup_connections()
    for row in main_window.current_table.rows:
        row.checkbox.setChecked(True)
    assert True
    assert len(main_window.ram_graph_widget.lines) == len(main_window.current_table.rows)


"""def test_click_on_graph_selects_corresponding_row(app, main_window):
    # Insert Dummy Data
    plot_mock1: Plot = Plot(name="mock_disp1", color="#FFFFFF", x_values=[0, 0], y_values=[0, 0])
    mock_disp1: Displayable = Displayable(name="mock_disp1", ram_plot=plot_mock1, cpu_plot=plot_mock1,
                                          runtime_plot=plot_mock1, ram_peak=0, cpu_peak=0, headers=[],
                                          secondary_headers=[])
    plot_mock2: Plot = Plot(name="mock_disp2", color="#FFFFFF", x_values=[0], y_values=[0])
    mock_disp2: Displayable = Displayable(name="mock_disp2", ram_plot=plot_mock2, cpu_plot=plot_mock2,
                                          runtime_plot=plot_mock2, ram_peak=0, cpu_peak=0, headers=[],
                                          secondary_headers=[])
    plot_mock3: Plot = Plot(name="mock_disp3", color="#FFFFFF", x_values=[0], y_values=[0])
    mock_disp3: Displayable = Displayable(name="mock_disp3", ram_plot=plot_mock3, cpu_plot=plot_mock3,
                                          runtime_plot=plot_mock3, ram_peak=0, cpu_peak=0, headers=[],
                                          secondary_headers=[])
    main_window.current_table.insert_values([mock_disp1, mock_disp2, mock_disp3])
    main_window.setup_connections()

    main_window.ram_graph_widget.click_signal.emit()
    clicked_graph = main_window.ram_graph_widget.plot_clicked
    selected_row = main_window.current_table.selectionModel().currentIndex().row()
    assert selected_row == clicked_graph"""
