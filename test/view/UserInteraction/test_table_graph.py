import sys
from multiprocessing import Queue, Event
from multiprocessing.synchronize import Event as SyncEvent

import pytest
from PyQt5.QtWidgets import QApplication

from src.model.Model import Model
from src.model.ModelReadViewInterface import ModelReadViewInterface
from src.view.gui.graph.GraphWidget import GraphWidget
from src.view.gui.graph.Plot import Plot
from src.view.gui.MainWindow import MainWindow
from src.view.gui.user_interaction.Displayable import Displayable
from src.view.gui.user_interaction.TreeWidget import TreeWidget


@pytest.fixture
def app():
    q_application: QApplication = QApplication(sys.argv)
    return q_application


@pytest.fixture
def tree_widget(main_window):
    return main_window.current_table


@pytest.fixture
def graph_widget(main_window) -> GraphWidget:
    return main_window.ram_graph_widget


@pytest.fixture
def main_window(app) -> MainWindow:
    shutdown_event: SyncEvent = Event()
    cancel_event: SyncEvent = Event()
    restart_event: SyncEvent = Event()
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
    return main_window


"""def test_main_window(main_window, tree_widget, graph_widget):
    assert isinstance(main_window, MainWindow)
    assert main_window.current_table == tree_widget
    assert main_window.ram_graph_widget == graph_widget"""


def test_click_checkbox_shows_graph(main_window, app, graph_widget, tree_widget) -> None:
    # Insert Dummy Data
    plot_mock1: Plot = Plot(name="mock_disp1", color="#FFFFFF", x_values=[0, 0], y_values=[0, 0])
    mock_disp1: Displayable = Displayable(name="mock_disp1", ram_plot=plot_mock1, cpu_plot=plot_mock1,
                                          runtime_plot=plot_mock1, ram_peak=0, cpu_peak=0, headers=[],
                                          secondary_headers=[])
    main_window.ram_graph_widget = graph_widget
    main_window.current_table = tree_widget
    main_window.current_table.insert_values([mock_disp1])
    main_window.setup_connections()
    for row in main_window.current_table.rows:
        row.checkbox.setCheckState(True)
    #main_window.ram_graph_widget.add_plot(mock_disp1.ram_plot)
    #tree_widget.rows[0].checkbox.setChecked(True)
    assert len(graph_widget.lines) == len(tree_widget.rows)


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
if __name__ == "__main__":
    test_click_checkbox_shows_graph(main_window=main_window, app=app, graph_widget=graph_widget, tree_widget=tree_widget)
