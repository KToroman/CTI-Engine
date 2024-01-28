import sys

import random
from typing import List

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QMainWindow, QVBoxLayout, QWidget,
                             QStackedWidget, QCheckBox, QApplication, QHBoxLayout, QSplitter)
from Graph.BarWidget import BarWidget
from Graph.GraphWidget import GraphWidget
from UserInteraction.MenuBar import MenuBar
from UserInteraction.TableWidget import TableWidget
from UserInteraction.Displayable import Displayable
from UserInteraction.TableRow import TableRow
from UserInteraction.MetricBar import MetricBar
from src.model.Model import Model
from src.model.ModelReadViewInterface import ModelReadViewInterface
from src.model.core.CFile import CFile
from src.model.core.CFileReadViewInterface import CFileReadViewInterface
from src.view.GUI.Graph.Plot import Plot
from src.model.core.MetricName import MetricName


class MainWindow(QMainWindow):
    WINDOWSIZE1 = 800
    WINDOWSIZE2 = 600
    WINDOWTITLE = "CTI Engine"

    def __init__(self):
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
        self.status_bar_frame_layout.addWidget(QCheckBox())  # Hier anstatt Checkbox die Status Bar hin
        self.top_frame_layout.addLayout(self.status_bar_frame_layout)

        self.widget_frame_layout: QVBoxLayout = QVBoxLayout()
        self.main_layout.addLayout(self.widget_frame_layout)

        self.splitter1: QSplitter = QSplitter(Qt.Horizontal)
        self.widget_frame_layout.addWidget(self.splitter1)

        self.metric_bar_frame_layout: QHBoxLayout = QHBoxLayout()

        self.menu_bar_frame_layout: QHBoxLayout = QHBoxLayout()

        self.user_interaction_frame_layout.addLayout(self.menu_bar_frame_layout)
        self.user_interaction_frame_layout.addLayout(self.metric_bar_frame_layout)

        # Initialize the components
        self.stacked_widget: QStackedWidget = QStackedWidget()
        self.page_1: GraphWidget = GraphWidget()  # Hier später die implementierte Version von GraphWidget
        self.page_2: BarWidget = BarWidget()  # Hier später die implementierte Version von BarWidget
        self.stacked_widget.addWidget(self.page_1)
        self.stacked_widget.addWidget(self.page_2)
        self.splitter1.addWidget(self.stacked_widget)

        self.table_widget: TableWidget = TableWidget()
        self.splitter1.addWidget(self.table_widget)

        self.menu_bar: MenuBar = MenuBar(self.menu_bar_frame_layout, self)
        self.metric_bar: MetricBar = MetricBar(self.metric_bar_frame_layout, self.stacked_widget)

        # Test nur als Beispiel
        self.dis = Displayable("test123", ..., ..., ..., 39, 123, 123)
        self.table_widget.add_row(TableRow(self.dis))
        self.table_widget.add_row(TableRow(self.dis))
        self.table_widget.add_row(TableRow(self.dis))

    def visualize(self, model):
        # Select spot for Displayables to be inserted into
        self.table_widget.set_insertion_point(model.get_project_name())

        # Update TableWidget for each cfile
        cfile_list = model.get_cfiles()
        for cfile in cfile_list:
            self.update_table(cfile)

        # Update other Widgets
        self.setup_connections()
        """Statusbar muss hier geupdatet werden"""

    # Possibly some mistakes here, needs testing
    def visualize_active(self, model: ModelReadViewInterface):
        # Find file used for active build
        active_row = self.table_widget.insertion_point
        active_file: CFileReadViewInterface
        for cfile in model.get_cfiles():
            active_file = self.get_hierachy(cfile, active_row)
            if active_file == active_row:
                break

        # Update TableWidget for said file
        self.update_table(active_file)

        # Update other Widgets
        self.setup_connections()
        """Statusbar muss hier geupdatet werden"""

    # Find cfile which started active mode
    def get_hierachy(self, cfile: CFileReadViewInterface, active_row: str) -> CFileReadViewInterface:
        if cfile.get_name() == active_row:
            return cfile
        elif not cfile.get_headers():
            return None
        for header in cfile.get_headers():
            self.get_hierachy(header)

    # Create Displayable for every cfile and insert into TableWidget
    def update_table(self, cfile: CFileReadViewInterface):
        # Collect data for Displayable
        name = cfile.get_name()
        ram_peak = cfile.get_max(MetricName.RAM)
        cpu_peak = cfile.get_max(MetricName.CPU)

        # Create Graph Plots
        x_values = cfile.get_timestamp()
        ram_y_values = cfile.get_metrics(MetricName.RAM)
        cpu_y_values = cfile.get_metrics(MetricName.CPU)
        runtime = [cfile.get_total_time()]
        color = self.generate_random_color()
        ram_plot = Plot(name, color, x_values, ram_y_values)
        cpu_plot = Plot(name, color, x_values, cpu_y_values)
        runtime_plot = Plot(name, color, runtime, None)

        # Create header list for current Displayable
        headers: List[Displayable] = list()
        for header in cfile.get_headers():
            headers.append(header.get_name())

        # Create Displayable and insert into TableWidget
        self.table_widget.insert_values(
            Displayable(name, ram_plot, cpu_plot, runtime_plot, ram_peak, cpu_peak, headers))

    # Generate Random Color for plot
    def generate_random_color(self):
        random_color = "#{:06X}".format(random.randint(0, 0xFFFFFF))
        return random_color

    def setup_connections(self):
        """to be implemented"""


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
