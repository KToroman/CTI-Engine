import colorsys

import os

import random
import time

from PyQt5.QtCore import pyqtSignal, QThreadPool, QMutex
from typing import List
from multiprocessing import Queue, Event
from multiprocessing.synchronize import Event as SyncEvent

from PyQt5.QtWidgets import (QMainWindow, QStackedWidget, QApplication, QCheckBox, QSpinBox, QLineEdit, QPushButton,
                             QWidget)
from PyQt5.QtGui import QIcon, QCloseEvent
from PyQt5.QtWidgets import (QMainWindow, QStackedWidget, QApplication, QCheckBox, QSpinBox, QLineEdit,
                             QPushButton)

from src.model.core.ProjectReadViewInterface import ProjectReadViewInterface
from src.view.GUI.Threading.PlotRunnable import PlotRunnable
from src.view.GUI.Threading.AddRunnable import AddRunnable
from src.view.GUI.Graph.BarWidget import BarWidget
from src.view.GUI.Graph.GraphWidget import GraphWidget
from src.view.GUI.MainWindowMeta import MainWindowMeta
from src.view.GUI.Threading.RemoveRunnable import RemoveRunnable
from src.view.GUI.UserInteraction.DisplayableHolder import DisplayableHolder
from src.view.GUI.UserInteraction.DisplayableInterface import DisplayableInterface
from src.view.GUI.UserInteraction.MenuBar import MenuBar
from src.view.GUI.UserInteraction.Displayable import Displayable
from src.view.GUI.UserInteraction.MetricBar import MetricBar
from src.model.ModelReadViewInterface import ModelReadViewInterface
from src.model.core.CFileReadViewInterface import CFileReadViewInterface
from src.view.GUI.Graph.Plot import Plot
from src.model.core.MetricName import MetricName
from src.view.GUI.Visuals.StatusBar import StatusBar
from src.model.core.StatusSettings import StatusSettings
from src.view.UIInterface import UIInterface
from src.view.GUI.Visuals.ErrorWindow import ErrorWindow
import src.view.GUI.Visuals.GuiDesign as gd
from src.view.GUI.UserInteraction.TreeWidget import TreeWidget


class MainWindow(QMainWindow, UIInterface, metaclass=MainWindowMeta):
    WINDOWSIZE1: int = 800
    WINDOWSIZE2: int = 600
    WINDOWTITLE: str = "CTI Engine"
    SELECT_ALL: str = "select all"
    RAM_Y_AXIS: str = "RAM (in mb)"
    CPU_Y_AXIS: str = "CPU (in %)"

    error_signal: pyqtSignal = pyqtSignal()
    visualize_signal: pyqtSignal = pyqtSignal()
    status_signal: pyqtSignal = pyqtSignal()
    change_table_signal: pyqtSignal = pyqtSignal()
    index_queue: "Queue[int]" = Queue()

    def __init__(self, shutdown_event: SyncEvent, q_application: QApplication, status_queue: "Queue[StatusSettings]",
                 project_queue: "Queue[str]", error_queue: "Queue[BaseException]",
                 load_path_queue: "Queue[str]", active_mode_queue: "Queue[str]", cancel_event: SyncEvent,
                 restart_event: SyncEvent, model: ModelReadViewInterface) -> None:
        super(MainWindow, self).__init__()

        self.central_widget: QWidget = QWidget(self)
        self.setWindowTitle(self.WINDOWTITLE)
        self.resize(self.WINDOWSIZE1, self.WINDOWSIZE2)

        # Queues and events for communication between app and gui
        self.__model = model
        self.project_queue: "Queue[str]" = project_queue
        self.shutdown_event: SyncEvent = shutdown_event
        self.active_mode_queue = active_mode_queue
        self.status_queue: "Queue[StatusSettings]" = status_queue
        self.error_queue: "Queue[BaseException]" = error_queue

        # connecting the signals
        self.error_signal.connect(lambda: self.deploy_error())
        self.visualize_signal.connect(lambda: self.visualize())
        self.change_table_signal.connect(lambda: self.toggle_table_vis(self.index_queue.get()))
        self.status_signal.connect(lambda: self.update_statusbar())
        self.HIERARCHY_DEPTH: int = 3

        self.setWindowTitle(self.WINDOWTITLE)
        self.resize(self.WINDOWSIZE1, self.WINDOWSIZE2)

        # setting up main components
        self.current_table: TreeWidget = TreeWidget(self.active_mode_queue)
        self.menu_bar: MenuBar = MenuBar(load_path_queue, cancel_event, restart_event, self.project_queue,
                                         self.visualize_signal, self.index_queue,
                                         self.change_table_signal)  # type: ignore[arg-type]
        self.metric_bar: MetricBar = MetricBar()

        self.__setup_resource_connections()

        images_folder = os.path.join(os.path.dirname(__file__), "Images")
        logo_path = os.path.join(images_folder, "CTIEngineLogo.png")
        icon: QIcon = QIcon(logo_path)
        self.setWindowIcon(icon)
        self.stylesheets: dict[str, str] = {}

        self.ram_graph_widget: GraphWidget = GraphWidget(self.RAM_Y_AXIS)
        self.cpu_graph_widget: GraphWidget = GraphWidget(self.CPU_Y_AXIS)
        self.bar_chart_widget: BarWidget = BarWidget()
        self.stacked_widget: QStackedWidget = QStackedWidget()
        self.status_bar: StatusBar = StatusBar()
        self.select_all_checkbox: QCheckBox = QCheckBox(self.SELECT_ALL)
        self.upper_limit: QSpinBox = QSpinBox()
        self.lower_limit: QSpinBox = QSpinBox()
        self.line_edit: QLineEdit = QLineEdit()
        self.stacked_table_widget: QStackedWidget = QStackedWidget()
        self.search_button: QPushButton = QPushButton()
        self.sidebar: QWidget = QWidget(self.central_widget)
        self.menu_bar.switch_style_box.currentIndexChanged.connect(lambda: self.set_stylesheet())

        # initialize lists and variables
        self.__q_application: QApplication = q_application
        self.__visible_plots: List[Displayable] = []
        self.project_time: float = 0

        self.mutex: QMutex = QMutex()
        self.thread_pool: QThreadPool = QThreadPool.globalInstance()
        self.thread_pool.setMaxThreadCount(10)
        self.displayed_project: str = ""
        self.all_tables: List[TreeWidget] = []

        # call instantiation methods
        self.__setup_resource_connections()
        self.__connect_new_table()
        self.load_stylesheets()
        gd.setup_ui(self)

    def execute(self) -> None:
        self.show()
        self.__q_application.exec()

    def load_stylesheets(self) -> None:
        stylesheets_dir = os.path.join(os.path.dirname(__file__), "Stylesheets")
        for stylesheet in os.listdir(stylesheets_dir):
            if stylesheet.endswith(".qss"):
                with open(os.path.join(stylesheets_dir, stylesheet), "r") as file:
                    style_name = os.path.splitext(stylesheet)[0]
                    self.stylesheets[style_name] = file.read()
                    self.menu_bar.switch_style_box.addItem(style_name)
        self.set_stylesheet()

    def set_stylesheet(self) -> None:
        selected_style = self.menu_bar.switch_style_box.currentText()
        self.setStyleSheet(self.stylesheets[selected_style])
        self.ram_graph_widget.set_stylesheet(selected_style)
        self.cpu_graph_widget.set_stylesheet(selected_style)
        self.bar_chart_widget.set_stylesheet(selected_style)
        self.menu_bar.set_stylesheet(selected_style)

    def visualize(self) -> None:
        """displays the data contained in that model to the user."""
        project_name: str = self.project_queue.get()
        project: ProjectReadViewInterface = self.__model.get_project_by_name(project_name)
        self.project_time = project.get_project_time()
        self.displayed_project = project_name
        # distinguish if active measurement flag was set or not
        if self.current_table.active_started or self.current_table.insertion_point:
            self.__visualize_active(project)
            self.current_table.active_started = False
        else:
            self.__update_project_list()
            self.__visualize_passive(project)

    def __visualize_passive(self, project: ProjectReadViewInterface) -> None:
        """Visualizes data from passive mode."""
        self.__connect_new_table()
        # Update TableWidget for each cfile
        cfile_list: List[CFileReadViewInterface] = project.get_cfiles()
        file_count: int = 1
        displayable_list: List[DisplayableHolder] = []
        for cfile in cfile_list:
            file_count += 1
            displayable_list.append(self.__create_displayable(cfile, 0, None))
        self.current_table.insert_values(displayables=displayable_list)
        self.lower_limit.setMaximum(file_count)
        self.upper_limit.setMaximum(file_count)
        # Update other Widgets
        self.__setup_connections()
        self.status_bar.update_status(StatusSettings.FINISHED, project.get_project_name())
        self.menu_bar.project_buttons[len(self.menu_bar.project_buttons) - 1].setStyleSheet("background-color: #00FF00")

    def __visualize_active(self, project: ProjectReadViewInterface) -> None:
        """Visualizes data from active mode."""
        # Find file used for active build
        active_row: str = self.current_table.insertion_point[0]
        active_file: CFileReadViewInterface
        for cfile in project.get_cfiles():
            if cfile.get_name() == active_row:
                active_file = cfile
                break

        # Update TableWidget for header list for said file
        cfile_list: List[CFileReadViewInterface] = active_file.get_headers()
        for cfile in active_file.get_headers():
            if cfile.get_headers():
                cfile_list.extend(cfile.get_headers())
        for item in self.current_table.items:
            if item.name == self.current_table.insertion_point[0]:
                color = item.row.displayable.runtime_plot.color
        for cfile in cfile_list:
            self.current_table.add_active_data(self.__create_displayable(cfile, 1, color))
        # Update other Widgets
        self.__setup_connections()
        self.status_bar.update_status(StatusSettings.FINISHED, self.current_table.insertion_point[0])
        self.current_table.insertion_point.pop(0)

    def __connect_new_table(self) -> None:
        """creates a new table for each loaded project and saves them in a list. That way the already loaded projects
           can be changed quickly"""
        self.select_all_checkbox.setChecked(True)
        time.sleep(4)
        self.select_all_checkbox.setChecked(False)
        self.current_table = TreeWidget(self.active_mode_queue)
        self.stacked_table_widget.addWidget(self.current_table)
        self.all_tables.append(self.current_table)
        self.select_all_checkbox.disconnect()
        # setting up connections for the new table
        self.select_all_checkbox.stateChanged.connect(lambda: self.current_table.toggle_all_rows())
        self.upper_limit.editingFinished.connect(
            lambda: self.current_table.toggle_custom_amount(self.lower_limit.value(), self.upper_limit.value()))
        self.lower_limit.editingFinished.connect(
            lambda: self.current_table.toggle_custom_amount(self.lower_limit.value(), self.upper_limit.value()))
        self.search_button.clicked.connect(lambda: self.current_table.search_item(self.line_edit))
        self.current_table.graph_signal.connect(lambda: self.__draw_graph())
        self.current_table.deselect_signal.connect(lambda: self.__deselect())
        self.current_table.run_count = 0
        self.__setup_connections()

        # change our gui to the page where the new table is located
        self.stacked_table_widget.setCurrentIndex(self.stacked_table_widget.count() - 1)

    def toggle_table_vis(self, index: int) -> None:
        """changes the currently displayed table. Deselects all graphs to make sure the change goes flawlessly"""
        self.select_all_checkbox.setChecked(True)
        time.sleep(2)
        self.select_all_checkbox.setChecked(False)
        self.stacked_table_widget.setCurrentIndex(index + 1)
        self.current_table = self.all_tables[index + 1]
        self.select_all_checkbox.disconnect()
        # setting up connections for the new table
        self.__setup_connections()
        self.select_all_checkbox.stateChanged.connect(lambda: self.current_table.toggle_all_rows())

    def __deselect(self):
        self.upper_limit.clearFocus()
        self.lower_limit.clearFocus()
        if self.select_all_checkbox.isChecked():
            self.select_all_checkbox.disconnect()
            self.select_all_checkbox.setChecked(False)
            self.select_all_checkbox.stateChanged.connect(lambda: self.current_table.toggle_all_rows())

    def deploy_error(self) -> None:
        """Receives an Exception, displays information regarding that exception to the user."""
        if self.error_queue.empty():
            return
        error = self.error_queue.get()
        if (error.__str__() == "[ActiveFetcherThread] This SourceFile has not compile_command!" or
                error.__str__() == "[ActiveFetcherThread] Active Fetcher Thread could not access its source-file-queue."
                or error.__str__() == "[ActiveFetcherThread] You can not build a single header!"):
            self.current_table.active_started = False
        error_window = ErrorWindow(error)
        error_window.show()

    def update_statusbar(self) -> None:
        """Receives a status string, changes the UI's status string accordingly."""
        status: StatusSettings = self.status_queue.get()
        if status.value[0] == "measuring":  # type: ignore[comparison-overlap]
            self.status_bar.update_status(status, self.__model.get_current_project_name().split("__")[0])
        elif status.value[0] == "active measuring":
            if self.current_table.insertion_point:
                self.status_bar.update_status(status, self.current_table.insertion_point[0].split(".o")[0].split("/")[-1])
        elif status.value[0] == "loading file":  # type: ignore[comparison-overlap]
            self.status_bar.update_status(status, self.menu_bar.load_path_name)
        else:
            self.status_bar.update_status(status, "")

    def __create_displayable(self, cfile: CFileReadViewInterface, depth_p: int, color) -> DisplayableHolder:
        """turns given cfile into displayable"""
        parent_list: List[CFileReadViewInterface] = list()
        self.__get_parent_list(cfile, parent_list)

        depth = depth_p + 1
        if depth >= self.HIERARCHY_DEPTH or not cfile.get_headers():
            return DisplayableHolder(self.__make_disp(cfile, color, parent_list), [])
        sub_disp_list: List[DisplayableInterface] = list()
        for header in cfile.get_headers():
            sub_disp_list.append(self.__create_displayable(header, depth, color))
        return DisplayableHolder(self.__make_disp(cfile, color, parent_list), sub_disp_list)

    def __get_parent_list(self, cfile: CFileReadViewInterface, parent_list: List[CFileReadViewInterface]) -> List[
        CFileReadViewInterface]:
        if cfile.get_parent() is not None:
            parent_list.append(cfile.get_parent())
            self.__get_parent_list(cfile.get_parent(), parent_list)
        else:
            return parent_list

    def __make_disp(self, cfile: CFileReadViewInterface, color_param,
                    parent_list: List[CFileReadViewInterface]) -> Displayable:
        name: str = cfile.get_name()
        ram_peak: float = cfile.get_max(MetricName.RAM)
        cpu_peak: float = cfile.get_max(MetricName.CPU)
        # Create Graph Plots
        x_values: List[float] = list()
        if parent_list:
            time: float = parent_list[-1].get_min_timestamps() - self.project_time
            if time <= 0:
                time = 0
            x_values.append(time)
            for i in range(cfile.get_timestamps().__len__() - 1):
                time += (cfile.get_timestamps()[i + 1] - cfile.get_timestamps()[i])
                x_values.append(time)
        else:
            for c in cfile.get_timestamps():
                x_values.append(c - self.project_time)
        ram_y_values: List[float] = cfile.get_metrics(MetricName.RAM)
        cpu_y_values: List[float] = cfile.get_metrics(MetricName.CPU)
        runtime: List[float] = list()
        runtime.append(cfile.get_total_time())
        if color_param is not None:
            color = color_param
        else:
            color: str = self.__generate_random_color()
        parent_name_list: List[str] = list()
        plot_name: str = cfile.get_name()
        for parent in parent_list:
            parent_name_list.append(parent.get_name())
            plot_name += "#" + parent.get_name()

        ram_plot: Plot = Plot(plot_name, color, x_values, ram_y_values)
        cpu_plot: Plot = Plot(plot_name, color, x_values, cpu_y_values)
        runtime_plot: Plot = Plot(plot_name, color, [], runtime)
        return Displayable(name, ram_plot, cpu_plot, runtime_plot, ram_peak, cpu_peak, cfile.has_error(),
                           parent_name_list)

    def __generate_random_color(self) -> str:
        """Generates random saturated color between light blue and pink."""
        light_blue_rgb = (173, 216, 230)  # Light Blue
        pink_rgb = (255, 182, 193)  # Pink
        saturation_factor = 2.1

        # Generate random RGB Values between Light Blue and Pink
        random_color_rgb = [
            random.randint(min(light_blue_rgb[i], pink_rgb[i]), max(light_blue_rgb[i], pink_rgb[i]))
            for i in range(3)
        ]

        hsv = colorsys.rgb_to_hsv(random_color_rgb[0] / 255.0, random_color_rgb[1] / 255.0, random_color_rgb[2] / 255.0)
        hsv = (hsv[0], min(1.0, hsv[1] * saturation_factor), hsv[2])
        random_color_rgb = list(int(x * 255) for x in colorsys.hsv_to_rgb(*hsv))
        random_color_hex = "#{:02X}{:02X}{:02X}".format(*random_color_rgb)

        return random_color_hex

    def __setup_connections(self) -> None:
        """Sets up connections between table and graph widgets."""
        for item in self.current_table.items:
            if not item.row.connected and item.row.checkbox.isEnabled():
                item.row.checkbox.stateChanged.connect(
                    lambda state, current_row=item.row: self.__update_visibility(current_row.displayable))
                item.row.connected = True

        self.__setup_click_connections()

    def __setup_resource_connections(self) -> None:
        """Sets up connections between metric bar and graph/bar chart widgets."""
        self.metric_bar.cpu_button.pressed.connect(lambda: self.stacked_widget.setCurrentIndex(1))
        self.metric_bar.ram_button.pressed.connect(lambda: self.stacked_widget.setCurrentIndex(0))
        self.metric_bar.runtime_button.pressed.connect(lambda: self.stacked_widget.setCurrentIndex(2))

    def __reset_graph(self) -> None:
        for displayable in self.__visible_plots:
            self.__visible_plots.remove(displayable)
            remove_runnable: RemoveRunnable = RemoveRunnable(ram_graph=self.ram_graph_widget,
                                                             cpu_graph=self.cpu_graph_widget,
                                                             runtime_graph=self.bar_chart_widget,
                                                             displayable=displayable, mutex=self.mutex)
            self.thread_pool.start(remove_runnable)

    def __update_visibility(self, displayable: Displayable) -> None:
        """Shows or hides plots of given displayable."""
        visibility: bool = False
        for visible_displayable in self.__visible_plots:
            if displayable.parent_list.__len__() != visible_displayable.parent_list.__len__():
                continue
            if displayable.name != visible_displayable.name:
                continue
            equal: bool = True
            for i in range(displayable.parent_list.__len__()):
                if displayable.parent_list[i] != visible_displayable.parent_list[i]:
                    equal = False
            if equal and displayable.runtime_plot.y_values[0] != 0:
                visibility = True
                self.__visible_plots.remove(visible_displayable)
                remove_runnable: RemoveRunnable = RemoveRunnable(ram_graph=self.ram_graph_widget,
                                                                 cpu_graph=self.cpu_graph_widget,
                                                                 runtime_graph=self.bar_chart_widget,
                                                                 displayable=displayable, mutex=self.mutex)
                self.thread_pool.start(remove_runnable)
                break
        if not visibility:
            self.__visible_plots.append(displayable)
            add_runnable: AddRunnable = AddRunnable(ram_graph=self.ram_graph_widget,
                                                    cpu_graph=self.cpu_graph_widget,
                                                    runtime_graph=self.bar_chart_widget, displayable=displayable,
                                                    mutex=self.mutex)
            self.thread_pool.start(add_runnable)
        if not self.current_table.in_row_loop:
            plot_runnable: PlotRunnable = PlotRunnable(ram_graph=self.ram_graph_widget, cpu_graph=self.cpu_graph_widget,
                                                       runtime_graph=self.bar_chart_widget, mutex=self.mutex)
            self.thread_pool.start(plot_runnable)

    def __draw_graph(self):
        plot_runnable: PlotRunnable = PlotRunnable(ram_graph=self.ram_graph_widget, cpu_graph=self.cpu_graph_widget,
                                                   runtime_graph=self.bar_chart_widget, mutex=self.mutex)
        self.thread_pool.start(plot_runnable)

    def __setup_click_connections(self) -> None:
        """Sets up connections between clicking on graph and highlighting according table row."""
        self.bar_chart_widget.click_signal.connect(
            lambda: self.current_table.highlight_row(self.bar_chart_widget.bar_clicked))
        self.cpu_graph_widget.click_signal.connect(
            lambda: self.current_table.highlight_row(self.cpu_graph_widget.plot_clicked))
        self.ram_graph_widget.click_signal.connect(
            lambda: self.current_table.highlight_row(self.ram_graph_widget.plot_clicked))

    def __update_project_list(self) -> None:
        """updates the list displayed in the sidebar, changing the color according to the currently shown project"""
        self.menu_bar.update_scrollbar(self.__model.get_all_project_names())

    def closeEvent(self, event: QCloseEvent) -> None:
        self.shutdown_event.set()
        event.accept()
