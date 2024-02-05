import sys

import random
from typing import List

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QMainWindow, QVBoxLayout, QWidget,
                             QStackedWidget, QCheckBox, QApplication, QHBoxLayout, QSplitter)
from src.view.GUI.Graph.BarWidget import BarWidget
from src.view.GUI.Graph.GraphWidget import GraphWidget
from src.view.GUI.UserInteraction.MenuBar import MenuBar
from src.view.GUI.UserInteraction.TableWidget import TableWidget
from src.view.GUI.UserInteraction.Displayable import Displayable
from src.view.GUI.UserInteraction.TableRow import TableRow
from src.view.GUI.UserInteraction.MetricBar import MetricBar
from src.model.Model import Model
from src.model.ModelReadViewInterface import ModelReadViewInterface
from src.model.core.CFileReadViewInterface import CFileReadViewInterface
from src.view.GUI.Graph.Plot import Plot
from src.model.core.MetricName import MetricName
from src.view.GUI.Visuals.StatusBar import StatusBar
from src.view.UIInterface import UIInterface

class MainWindowMeta(type(QMainWindow), type(UIInterface)):
    pass

class MainWindow(QMainWindow, UIInterface, metaclass=MainWindowMeta):
    WINDOWSIZE1: int = 800
    WINDOWSIZE2: int = 600
    WINDOWTITLE: str = "CTI Engine"

    __visible_plots: List[Displayable] = []
    __ram: bool = False
    __cpu: bool = False
    __runtime: bool = False

    def __init__(self, q_application: QApplication):
        self.__q_application: QApplication = q_application
        super().__init__()
        self.setWindowTitle(self.WINDOWTITLE)
        self.resize(self.WINDOWSIZE1, self.WINDOWSIZE2)

        # Setting up the Layout
        self.central_widget: QWidget = QWidget(self)
        self.setCentralWidget(self.central_widget)
        self.main_layout: QVBoxLayout = QVBoxLayout(self.central_widget)

        self.top_frame_layout: QHBoxLayout = QHBoxLayout()
        self.main_layout.addLayout(self.top_frame_layout)

        self.user_interaction_frame_layout: QVBoxLayout = QVBoxLayout()
        self.top_frame_layout.addLayout(self.user_interaction_frame_layout)

        self.status_bar_frame_layout: QHBoxLayout = QVBoxLayout()
        self.status_bar: StatusBar = StatusBar()
        self.status_bar.setMaximumHeight(100)
        self.status_bar_frame_layout.addWidget(self.status_bar)
        self.top_frame_layout.addLayout(self.status_bar_frame_layout)

        self.widget_frame_layout: QVBoxLayout = QVBoxLayout()
        self.main_layout.addLayout(self.widget_frame_layout)

        self.splitter1: QSplitter = QSplitter(Qt.Horizontal)
        self.widget_frame_layout.addWidget(self.splitter1)

        self.metric_bar_frame_layout: QHBoxLayout = QHBoxLayout()

        self.menu_bar_frame_layout: QHBoxLayout = QHBoxLayout()

        self.user_interaction_frame_layout.addLayout(
            self.menu_bar_frame_layout)
        self.user_interaction_frame_layout.addLayout(
            self.metric_bar_frame_layout)

        # Initialize the components
        self.stacked_widget: QStackedWidget = QStackedWidget()
        self.graph_widget: GraphWidget = GraphWidget()  # Hier später die implementierte Version von GraphWidget
        self.bar_chart_widget: BarWidget = BarWidget()  # Hier später die implementierte Version von BarWidget
        self.stacked_widget.addWidget(self.graph_widget)
        self.stacked_widget.addWidget(self.bar_chart_widget)
        self.splitter1.addWidget(self.stacked_widget)

        self.table_widget: TableWidget = TableWidget()
        self.splitter1.addWidget(self.table_widget)

        self.menu_bar: MenuBar = MenuBar(self.menu_bar_frame_layout, self)
        self.metric_bar: MetricBar = MetricBar(
            self.metric_bar_frame_layout, self.stacked_widget)

        self.graph_widget.toggle_ram()
        self.graph_widget.toggle_cpu()
        self.setup_resource_connections()

        # Test nur als Beispiel
        self.dis = Displayable("test", Plot("marie2", "#FF0000", [1.2, 1.8, 2.9], [7.4, 2.6, 7.8]),
                               Plot("marie", "#FF0000", [1.5, 2.3, 4.4], [6.4, 5.6, 7.8]),
                               Plot("marie", "#FF0000", [], [7.4, 9.6, 2.8]), 5.4, 7.88, [])
        self.dis1 = Displayable("asd", Plot("asd", "#0000FF", [1.2, 1.8, 2.9], [9.4, 5.6, 3.8]),
                                Plot("asd", "#0000FF", [0.5, 1.3, 3.4], [7.4, 9.6, 2.8]),
                                Plot("asd", "#0000FF", [], [3.4, 5.6, 3.8]), 7.4, 9.88, [])

        self.table_widget.insert_values(self.dis)
        self.table_widget.insert_values(self.dis1)
        self.setup_connections()

        self.show()

    def visualize(self, model):
        """visualizes data from passive mode"""

        # Select spot for Displayables to be inserted into
        self.table_widget.insertion_point = model.get_project_name()

        # Update TableWidget for each cfile
        cfile_list: List[CFileReadViewInterface] = model.get_cfiles()
        for cfile in cfile_list:
            self.table_widget.insert_values(self.__create_displayable(cfile))

        # Update other Widgets
        self.setup_connections()
        self.status_bar.update_status("finished")

    def visualize_active(self, model: ModelReadViewInterface):
        """visualizes data from active mode"""

        # Find file used for active build
        active_row: str = self.table_widget.insertion_point
        active_file: CFileReadViewInterface
        for cfile in model.get_cfiles():
            active_file = self.__get_hierarchy(cfile, active_row)
            if active_file.get_name() == active_row:
                break

        # Update TableWidget for header list for said file
        cfile_list: List[CFileReadViewInterface] = active_file.get_headers()
        for cfile in cfile_list:
            self.table_widget.add_subrow(self.__create_displayable(cfile))

        # Update other Widgets
        self.setup_connections()
        self.status_bar.update_status("finished")

    def __get_hierarchy(self, cfile: CFileReadViewInterface, active_row: str) -> CFileReadViewInterface:
        """finds cfile which started active mode"""
        if cfile.get_name() == active_row:
            return cfile
        elif not cfile.get_headers():
            return None
        for header in cfile.get_headers():
            self.__get_hierarchy(header, active_row)

    def __create_displayable(self, cfile: CFileReadViewInterface) -> Displayable:
        """turns given cfile into displayable"""

        # Collect data for Displayable
        name: str = cfile.get_name()
        ram_peak: float = cfile.get_max(MetricName.RAM)
        cpu_peak: float = cfile.get_max(MetricName.CPU)

        # Create Graph Plots
        x_values: List[float] = cfile.get_timestamps()
        ram_y_values: List[float] = cfile.get_metrics(MetricName.RAM)
        cpu_y_values: List[float] = cfile.get_metrics(MetricName.CPU)
        runtime: List[float] = [cfile.get_total_time()]
        color: str = self.__generate_random_color()
        ram_plot = Plot(name, color, x_values, ram_y_values)
        cpu_plot = Plot(name, color, x_values, cpu_y_values)
        runtime_plot = Plot(name, color, None, runtime)

        # Create header list for current Displayable
        headers: List[Displayable] = list()
        for header in cfile.get_headers():
            headers.append(header.get_name())

        return Displayable(name, ram_plot, cpu_plot, runtime_plot, ram_peak, cpu_peak, headers)

    def __generate_random_color(self):
        """generates random color for plots"""
        random_color: str = "#{:06X}".format(random.randint(0, 0xFFFFFF))
        return random_color

    def setup_connections(self):
        """sets up connections between table and graph widgets"""
        for row in self.table_widget.rows:
            if not row.connected:
                row.checkbox.stateChanged.connect(
                    lambda state, current_row=row: self.update_visibility(current_row.displayable))
                row.connected = True

    def setup_resource_connections(self):
        """sets up connections between metric bar and graph widgets"""
        self.metric_bar.cpu_checkbox.stateChanged.connect(lambda: self.switch_cpu())
        self.metric_bar.ram_checkbox.stateChanged.connect(lambda: self.switch_ram())
        self.metric_bar.time_checkbox.stateChanged.connect(lambda: self.switch_runtime())

    def switch_runtime(self):
        """is called by using runtime checkbox, shows or hides runtime bars"""
        if self.__runtime:
            self.__runtime = False
        elif not self.__ram and not self.__cpu:
            self.__runtime = True
            self.stacked_widget.setCurrentIndex(1)
        self.bar_chart_widget.toggle_chart()

    def switch_ram(self):
        """is called by using ram checkbox, shows or hides ram graphs"""
        if self.__ram:
            self.__ram = False
        elif not self.__runtime:
            self.__ram = True
            self.stacked_widget.setCurrentIndex(0)
        self.graph_widget.toggle_ram()

    def switch_cpu(self):
        """is called by using cpu checkbox, shows or hides cpu graphs"""
        if self.__cpu:
            self.__cpu = False
        elif not self.__runtime:
            self.__cpu = True
            self.stacked_widget.setCurrentIndex(0)
        self.graph_widget.toggle_cpu()

    def update_visibility(self, displayable: Displayable):
        """shows or hides plots of given displayable"""
        visibility: bool = False
        for visible_displayable in self.__visible_plots:
            if visible_displayable.name == displayable.name:
                visibility = True
                self.__visible_plots.remove(visible_displayable)
                self.__remove_from_graph(displayable)
        if not visibility:
            self.__visible_plots.append(displayable)
            self.__add_to_graph(displayable)

    def __add_to_graph(self, displayable: Displayable):
        """adds plots of given displayable to graph and bar chart widgets"""
        self.graph_widget.add_ram_plot(displayable.ram_plot)
        self.graph_widget.add_cpu_plot(displayable.cpu_plot)
        self.bar_chart_widget.add_bar(displayable.runtime_plot)

    def __remove_from_graph(self, displayable: Displayable):
        """removes plots of given displayable from graph and bar chart widgets"""
        self.graph_widget.remove_ram_plot(displayable.ram_plot)
        self.graph_widget.remove_cpu_plot(displayable.cpu_plot)
        self.bar_chart_widget.remove_bar(displayable.runtime_plot)

    def close(self):
        self.q_application.exec()
