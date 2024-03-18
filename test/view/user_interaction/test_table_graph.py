import sys
from multiprocessing import Queue, Event
from multiprocessing.synchronize import Event as SyncEvent

import pytest
from PyQt5.QtWidgets import QApplication

from src.model.Model import Model
from src.model.ModelReadViewInterface import ModelReadViewInterface
from src.view.gui.AddRunnable import AddRunnable
from src.view.gui.graph.BarWidget import BarWidget
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
def bar_widget(main_window) -> BarWidget:
    return main_window.bar_chart_widget


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


def create_mock_data() -> Displayable:
    """Creates mock data for testing."""
    plot_mock1: Plot = Plot(name="mock_disp1", color="#FFFFFF", x_values=[0], y_values=[0])
    mock_disp1: Displayable = Displayable(name="mock_disp1", ram_plot=plot_mock1, cpu_plot=plot_mock1,
                                          runtime_plot=plot_mock1, ram_peak=0, cpu_peak=0, headers=[],
                                          secondary_headers=[])
    return mock_disp1


def setup_connections_mock(tree_widget: TreeWidget, graph_widget: GraphWidget, bar_widget: BarWidget):
    """Mock for private method in MainWindow Class."""
    for row in tree_widget.rows:
        if not row.connected:
            row.checkbox.stateChanged.connect(
                lambda state, current_row=row: update_visibility_mock(displayable=current_row.displayable,
                                                                      graph_widget=graph_widget, bar_widget=bar_widget))
            row.connected = True


def setup_click_connections_mock(tree_widget: TreeWidget, graph_widget: GraphWidget, bar_widget: BarWidget):
    """Mock for private method in MainWindow Class."""
    graph_widget.click_signal.connect(lambda: tree_widget.highlight_row(graph_widget.plot_clicked))
    bar_widget.click_signal.connect(lambda: tree_widget.highlight_row(bar_widget.bar_clicked))


def update_visibility_mock(displayable: Displayable, graph_widget: GraphWidget, bar_widget: BarWidget):
    """Mock for private method in MainWindow Class."""
    graph_widget.add_plot(displayable.ram_plot)
    graph_widget.plot_graph()
    bar_widget.add_bar(displayable.runtime_plot)
    bar_widget.plot_bar_chart()


def test_clicking_checkbox_shows_graph(graph_widget, bar_widget, tree_widget) -> None:
    tree_widget.insert_values([create_mock_data()])
    setup_connections_mock(tree_widget=tree_widget, graph_widget=graph_widget, bar_widget=bar_widget)

    # checkbox in tree_widget set to checked
    for row in tree_widget.rows:
        row.checkbox.setCheckState(True)

    # assert whether plot was added to graph_widget
    assert len(graph_widget.lines) == len(tree_widget.rows)
    assert len(bar_widget.categories) == len(tree_widget.rows)


def test_click_on_graph_selects_corresponding_row(tree_widget, graph_widget, bar_widget):
    mock_data: Displayable = create_mock_data()
    tree_widget.insert_values([mock_data])
    setup_click_connections_mock(tree_widget=tree_widget, graph_widget=graph_widget, bar_widget=bar_widget)
    update_visibility_mock(displayable=mock_data, graph_widget=graph_widget, bar_widget=bar_widget)

    # simulates click on graph
    graph_widget.plot_clicked = mock_data.name
    graph_widget.click_signal.emit()

    # check whether according row in table was selected
    selected_item: int = tree_widget.currentItem()
    selected_row: str
    row_index: int = 0
    for item in tree_widget.items:
        if item == selected_item:
            selected_row = tree_widget.rows[row_index].displayable.name
            break
        row_index += 1
    assert selected_row == graph_widget.plot_clicked

    # simulates click on bar
    bar_widget.bar_clicked = mock_data.name
    bar_widget.click_signal.emit()

    # check whether according row in table was selected
    selected_item: int = tree_widget.currentItem()
    selected_row: str
    row_index: int = 0
    for item in tree_widget.items:
        if item == selected_item:
            selected_row = tree_widget.rows[row_index].displayable.name
            break
        row_index += 1
    assert selected_row == bar_widget.bar_clicked

