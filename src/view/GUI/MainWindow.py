import sys

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QMainWindow, QVBoxLayout, QWidget,
                             QStackedWidget, QCheckBox, QApplication, QHBoxLayout, QSplitter)
from Graph.BarWidget import BarWidget
from Graph.GraphWidget import GraphWidget
from UserInteraction.MenuBar import MenuBar
from UserInteraction.TableWidget import TableWidget
from UserInteraction.Displayable import Displayable
from UserInteraction.TableRow import TableRow


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


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
