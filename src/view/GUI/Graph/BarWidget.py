from matplotlib.backends.backend_template import FigureCanvas
from PyQt5.QtWidgets import QVBoxLayout, QWidget
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas


class BarWidget(QWidget):
    def __init__(self):
        super(BarWidget, self).__init__()

        self.figure = Figure(figsize=(5, 4), dpi=100)
        self.canvas = FigureCanvas(self.figure)

        layout = QVBoxLayout(self)
        layout.addWidget(self.canvas)
        self.plot_bar_chart()

    # Auch nur Beispiel
    def plot_bar_chart(self):
        # Daten für das Säulendiagramm
        categories = ['Category 1', 'Category 2', 'Category 3', 'Category 4', 'Category 5']
        values = [5, 12, 8, 15, 10]

        # Erstelle einen Subplot für das Säulendiagramm
        ax = self.figure.add_subplot(111)

        # Erstelle das Säulendiagramm
        ax.bar(categories, values, color='blue')

        # Beschriftungen und Titel hinzufügen
        ax.set_xlabel('Categories')
        ax.set_ylabel('Values')
        ax.set_title('Bar Chart Example')

        # Zeichne das Diagramm auf das Canvas
        self.canvas.draw()
