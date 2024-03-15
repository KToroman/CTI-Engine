import colorsys

import os

import random
import time

from PyQt5.QtCore import pyqtSignal
from threading import Thread, Lock
from PyQt5.QtCore import pyqtSignal, QThreadPool
from typing import List
from multiprocessing import Queue, Event

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QIntValidator
from PyQt5.QtWidgets import (QMainWindow, QVBoxLayout, QWidget,
                             QStackedWidget, QApplication, QHBoxLayout, QSplitter, QCheckBox, QSpinBox)
from src.model.Model import Model
from src.model.core.ProjectReadViewInterface import ProjectReadViewInterface
from src.view.GUI.PlotRunnable import PlotRunnable
from src.view.GUI.AddRunnable import AddRunnable
from src.view.GUI.Graph.BarWidget import BarWidget
from src.view.GUI.Graph.GraphWidget import GraphWidget
from src.view.GUI.MainWindowMeta import MainWindowMeta
from src.view.GUI.RemoveRunnable import RemoveRunnable
from src.view.GUI.UserInteraction.MenuBar import MenuBar
from src.view.GUI.UserInteraction.TableWidget import TableWidget
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
from src.view.AppRequestsInterface import AppRequestsInterface
import src.view.GUI.Visuals.GuiDesign as gd
from src.view.GUI.UserInteraction.TreeWidget import TreeWidget

class MainWindow(QMainWindow, UIInterface, metaclass=MainWindowMeta):
    WINDOWSIZE1: int = 800
    WINDOWSIZE2: int = 600
    WINDOWTITLE: str = "CTI Engine"
    SELECT_ALL: str = "Select all"
    RAM_Y_AXIS: str = "RAM (in mb)"
    CPU_Y_AXIS: str = "CPU (in %)"

    error_signal: pyqtSignal = pyqtSignal()
    visualize_signal: pyqtSignal = pyqtSignal()
    status_signal: pyqtSignal = pyqtSignal()

    def __init__(self, shutdown_event: Event, q_application: QApplication, status_queue: Queue, project_queue: Queue,
                 error_queue: Queue, load_path_queue: Queue, active_mode_queue: Queue, cancel_event: Event,
                 restart_event: Event, model: ModelReadViewInterface):
        super(MainWindow, self).__init__()

        # Queues and events for communication between app and gui
        self.project_queue: Queue = project_queue
        self.visualize_signal.connect(lambda: self.visualize())

        self.__model = model
        self.table_widget: TreeWidget = TreeWidget(active_mode_queue=active_mode_queue)
        self.status_queue: Queue = status_queue
        self.status_signal.connect(lambda: self.update_statusbar())

        self.error_queue: Queue = error_queue
        self.error_signal.connect(lambda: self.deploy_error())
        self.shutdown_event: Event = shutdown_event

        self.__q_application: QApplication = q_application
        self.__visible_plots: List[Displayable] = []
        self.project_time: float = 0

        self.thread_pool: QThreadPool = QThreadPool.globalInstance()
        self.thread_pool.setMaxThreadCount(10)

        self.setWindowTitle(self.WINDOWTITLE)
        self.resize(self.WINDOWSIZE1, self.WINDOWSIZE2)

        self.select_all_checkbox = QCheckBox("select all")
        self.upper_limit = QSpinBox()
        self.lower_limit = QSpinBox()

        self.select_all_checkbox.stateChanged.connect(lambda: self.table_widget.toggle_all_rows())
        self.upper_limit.editingFinished.connect(
            lambda: self.table_widget.toggle_custom_amount(self.lower_limit.value(), self.upper_limit.value()))
        self.lower_limit.editingFinished.connect(
            lambda: self.table_widget.toggle_custom_amount(self.lower_limit.value(), self.upper_limit.value()))

        self.menu_bar: MenuBar = MenuBar(load_path_queue, cancel_event, restart_event, self.project_queue,
                                         self.visualize_signal)
        self.metric_bar: MetricBar = MetricBar()

        self.setup_resource_connections()

        images_folder = os.path.join(os.path.dirname(__file__), "Images")
        logo_path = os.path.join(images_folder, "CTIEngineLogo.png")
        icon: QIcon = QIcon(logo_path)
        self.setWindowIcon(icon)
        self.setStyleSheet("background-color: #ECEFF1;")
        self.stylesheets = {"Dark Mode": "src/view/GUI/Stylesheets/StylesheetDark.qss", "Light Mode": " "}

        """colors from cti engine logo:
        #237277
        #4095a1
        #61b3bf
        chatgpt: #ECEFF1
        himmelgrau: #CFD8DC
        caspars farbe: #444447"""

        self.ram_graph_widget: GraphWidget = GraphWidget(self.RAM_Y_AXIS)
        self.cpu_graph_widget: GraphWidget = GraphWidget(self.CPU_Y_AXIS)
        self.bar_chart_widget: BarWidget = BarWidget()

        self.stacked_widget = QStackedWidget()

        self.status_bar: StatusBar = StatusBar()

        gd.setupUI(self, active_mode_queue)
        self.menu_bar.switch_style_box.currentIndexChanged.connect(lambda: self.set_stylesheet())
        self.setup_resource_connections()

    def execute(self):
        self.show()
        self.__q_application.exec()

    def set_stylesheet(self):
        selected_style = self.menu_bar.switch_style_box.currentText()
        print(selected_style)
        self.__q_application.setStyleSheet(self.stylesheets[selected_style])

    def visualize(self):
        print("visualize")
        """displays the data contained in that Model to the user."""
        project_name: str = self.project_queue.get()
        project = self.__model.get_project_by_name(project_name)
        self.project_time = project.get_project_time()
        self.__update_project_list()
        if self.table_widget.active_started:
            self.__visualize_active(project)
            self.table_widget.active_started = False
        else:
            self.__visualize_passive(project)

    def __visualize_passive(self, project: ProjectReadViewInterface):
        """Visualizes data from passive mode."""
        #self.table_widget.clear_table()
        # Select spot for Displayables to be inserted into
        self.table_widget.insertion_point = project.get_project_name()

        # Update TableWidget for each cfile
        cfile_list: List[CFileReadViewInterface] = project.get_cfiles()
        file_count: int = 1
        displayable_list: List[Displayable] = []
        for cfile in cfile_list:
            file_count += 1
            displayable_list.append(self.__create_displayable(cfile))
        self.table_widget.insert_values(displayable_list)
        self.lower_limit.setMaximum(file_count)
        self.upper_limit.setMaximum(file_count)
        # Update other Widgets
        self.setup_connections()
        self.status_bar.update_status(StatusSettings.FINISHED)
        #self.table_widget.rebuild_table(self.table_widget.rows)

    def __visualize_active(self, project: ProjectReadViewInterface):
        """Visualizes data from active mode."""
        # Find file used for active build
        active_row: str = self.table_widget.insertion_point
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
        time1 = time.time()
        for cfile in cfile_list:
            print("[MW]    cfile being filled: " + cfile.get_name())
            print(cfile.get_total_time())
            self.table_widget.add_active_data(self.__create_displayable(cfile))
        print(str(time.time() - time1))
        # Update other Widgets
        self.setup_connections()
        self.status_bar.update_status(StatusSettings.FINISHED)
        print("updated")

    def deploy_error(self):
        """Receives an Exception, displays information regarding that exception to the user."""
        if self.error_queue.empty():
            return
        error = self.error_queue.get()
        error_window = ErrorWindow(error)
        error_window.show()

    def update_statusbar(self):
        """Receives a status string, changes the UI's status string accordingly."""
        status = self.status_queue.get()
        self.status_bar.update_status(status)

    def __get_hierarchy(self, cfile: CFileReadViewInterface, active_row: str) -> CFileReadViewInterface:
        """Finds cfile which started active mode."""
        if cfile.get_name() == active_row:
            return cfile
        elif not cfile.get_headers():
            return None
        for header in cfile.get_headers():
            self.__get_hierarchy(header, active_row)

    def __create_displayable(self, cfile: CFileReadViewInterface) -> Displayable:
        """Turns given cfile into displayable."""

        # Collect data for Displayable
        name: str = cfile.get_name()
        ram_peak: float = cfile.get_max(MetricName.RAM)
        cpu_peak: float = cfile.get_max(MetricName.CPU)

        # Create Graph Plots
        x_values: List[float] = list()
        for c in cfile.get_timestamps():
            x_values.append(c - self.project_time)
        ram_y_values: List[float] = cfile.get_metrics(MetricName.RAM)
        cpu_y_values: List[float] = cfile.get_metrics(MetricName.CPU)
        runtime: List[float] = [cfile.get_total_time()]
        color: str = self.__generate_random_color()
        ram_plot = Plot(name, color, x_values, ram_y_values)
        cpu_plot = Plot(name, color, x_values, cpu_y_values)
        runtime_plot = Plot(name, color, None, runtime)

        # Create header and secondary header list for current Displayable
        headers: List[str] = list()
        secondary_headers: List[List[str]] = list()
        for header in cfile.get_headers():
            headers.append(header.get_name())
            subheaders: List[str] = []
            for secondary_header in header.get_headers():
                subheaders.append(secondary_header.get_name())
            secondary_headers.append(subheaders)
        return Displayable(name, ram_plot, cpu_plot, runtime_plot, ram_peak, cpu_peak, headers, secondary_headers)

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
        random_color_rgb = tuple(int(x * 255) for x in colorsys.hsv_to_rgb(*hsv))
        random_color_hex = "#{:02X}{:02X}{:02X}".format(*random_color_rgb)

        return random_color_hex

    def setup_connections(self):
        """Sets up connections between table and graph widgets."""
        for row in self.table_widget.rows:
            if not row.connected:
                row.checkbox.stateChanged.connect(
                    lambda state, current_row=row: self.update_visibility(current_row.displayable))
                row.connected = True

        self.setup_click_connections()

    def setup_resource_connections(self):
        """Sets up connections between metric bar and graph/bar chart widgets."""
        self.metric_bar.cpu_button.pressed.connect(lambda: self.stacked_widget.setCurrentIndex(1))
        self.metric_bar.ram_button.pressed.connect(lambda: self.stacked_widget.setCurrentIndex(0))
        self.metric_bar.runtime_button.pressed.connect(lambda: self.stacked_widget.setCurrentIndex(2))

    def update_visibility(self, displayable: Displayable):
        """Shows or hides plots of given displayable."""
        visibility: bool = False
        for visible_displayable in self.__visible_plots:
            if visible_displayable.name == displayable.name:
                visibility = True
                self.__visible_plots.remove(visible_displayable)
                remove_runnable: RemoveRunnable = RemoveRunnable(ram_graph=self.ram_graph_widget,
                                                                 cpu_graph=self.cpu_graph_widget,
                                                                 runtime_graph=self.bar_chart_widget,
                                                                 displayable=displayable)
                self.thread_pool.start(remove_runnable)
        if not visibility:
            self.__visible_plots.append(displayable)
            add_runnable: AddRunnable = AddRunnable(ram_graph=self.ram_graph_widget,
                                                    cpu_graph=self.cpu_graph_widget,
                                                    runtime_graph=self.bar_chart_widget, displayable=displayable)
            self.thread_pool.start(add_runnable)
        if not self.table_widget.in_row_loop:
            plot_runnable: PlotRunnable = PlotRunnable(ram_graph=self.ram_graph_widget, cpu_graph=self.cpu_graph_widget,
                                                       runtime_graph=self.bar_chart_widget)
            self.thread_pool.start(plot_runnable)

    def setup_click_connections(self):
        """Sets up connections between clicking on graph and highlighting according table row."""
        self.bar_chart_widget.click_signal.connect(
            lambda: self.table_widget.highlight_row(self.bar_chart_widget.bar_clicked))
        self.cpu_graph_widget.click_signal.connect(
            lambda: self.table_widget.highlight_row(self.cpu_graph_widget.plot_clicked))
        self.ram_graph_widget.click_signal.connect(
            lambda: self.table_widget.highlight_row(self.ram_graph_widget.plot_clicked))

    def __update_project_list(self):
        self.menu_bar.update_scrollbar(self.__model.get_all_project_names())

    def closeEvent(self, event):
        self.shutdown_event.set()
        event.accept()
