import sys
import random
from PyQt5.QtWidgets import (QMainWindow, QFrame, QVBoxLayout, QWidget,
                             QStackedWidget, QTableWidget, QTableWidgetItem, QCheckBox, QApplication, QHBoxLayout)
from Graph.BarWidget import BarWidget
from Graph.GraphWidget import GraphWidget
from UserInteraction.MenuBar import MenuBar
from UserInteraction.TableWidget import TableWidget
from UserInteraction.Displayable import Displayable
from Graph.Plot import Plot
from src.model.core.MetricName import MetricName


# noinspection LanguageDetectionInspection
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CTI Engine")
        self.resize(800, 600)

        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)

        # Layouts
        self.main_layout = QVBoxLayout(self.central_widget)
        self.user_interaction_frame_layout = QVBoxLayout()
        self.menu_bar_frame_layout = QHBoxLayout()
        self.metric_frame_layout = QHBoxLayout()
        self.widget_frame_layout = QHBoxLayout()
        self.graph_frame_layout = QVBoxLayout()
        self.table_frame_layout = QVBoxLayout()
        # Adding the layouts to one another
        self.user_interaction_frame_layout.addLayout(self.menu_bar_frame_layout)
        self.user_interaction_frame_layout.addLayout(self.metric_frame_layout)
        self.main_layout.addLayout(self.user_interaction_frame_layout)

        self.widget_frame_layout.addLayout(self.graph_frame_layout)
        self.widget_frame_layout.addLayout(self.table_frame_layout)
        self.main_layout.addLayout(self.widget_frame_layout)

        # Frame structure
        self.user_interaction_frame = QFrame(self.central_widget)
        self.main_layout.addWidget(self.user_interaction_frame)
        # Has:
        self.menu_bar_frame = QFrame(self.user_interaction_frame)
        # And:
        self.metric_frame = QFrame(self.user_interaction_frame)
        self.widget_frame = QFrame(self.central_widget)
        self.main_layout.addWidget(self.widget_frame)
        # Has:
        self.graph_frame = QFrame(self.widget_frame)
        # And
        self.table_frame = QFrame(self.widget_frame)

        # Setting up the components
        self.stacked_widget = QStackedWidget(self.graph_frame)
        self.page_1 = GraphWidget()  # Hier später die implementierte Version von GraphWidget
        self.page_2 = BarWidget()  # Hier später die implementierte Version von BarWidget
        self.stacked_widget.addWidget(self.page_1)
        self.stacked_widget.addWidget(self.page_2)

        self.table_widget = QTableWidget(5, 3)  # Hier später die implementierte Version von TableWidget

        # Fülle das Table Widget mit Beispielwerten
        for row in range(5):
            for col in range(3):
                item = QTableWidgetItem(f"Row {row + 1}, Col {col + 1}")
                self.table_widget.setItem(row, col, item)

        self.menu_bar = MenuBar(self.menu_bar_frame, self.menu_bar_frame_layout, self)
        self.metric_bar = MetricBar(self.metric_frame, self.metric_frame_layout, self.stacked_widget)

        # Adding the custom widgets to the layouts, so they fit nicely
        self.graph_frame_layout.addWidget(self.stacked_widget)
        self.table_frame_layout.addWidget(self.table_widget)


    def visualize(self, model):

        cfile_list = model.get_cfiles()
        displayables: list[:Displayable]

        # Create Displayable List
        for cfile in cfile_list:

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

            # Create Displayable and add to Displayable List
            displayables.append(Displayable(name, ram_plot, cpu_plot, runtime_plot, ram_peak, cpu_peak))

        # Insert Displayables into TableWidget
        self.table_widget.insert_values(displayables)

        # Update Widgets
        self.setup_connections()
        """Statusbar muss hier geupdatet werden"""


    # Generate Random Color for plot
    def generate_random_color(self):
        random_color = "#{:06X}".format(random.randint(0, 0xFFFFFF))
        return random_color

    def setup_connections(self):

        """to be implemented"""






class MetricBar:
    def __init__(self, metric_frame, metric_frame_layout, stacked_widget):
        self.cpu_checkbox = QCheckBox("CPU", metric_frame)
        self.cpu_checkbox.stateChanged.connect(lambda: ...)
        self.ram_checkbox = QCheckBox("RAM", metric_frame)
        self.ram_checkbox.stateChanged.connect(lambda: ...)
        self.time_checkbox = QCheckBox("Time", metric_frame)
        self.time_checkbox.stateChanged.connect(lambda: stacked_widget.setCurrentIndex(
            1))  # Nur als Beispiel, hier kommt nachher die switch ressources Methode rein
        metric_frame_layout.addWidget(self.ram_checkbox)
        metric_frame_layout.addWidget(self.cpu_checkbox)
        metric_frame_layout.addWidget(self.time_checkbox)



if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
